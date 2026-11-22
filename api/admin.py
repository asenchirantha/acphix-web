import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


def public(row):
    row = dict(row)
    row.pop("password_hash", None)
    row.pop("_id", None)
    return row


def authorized(request):
    database = db()
    auth = get_session(database, request)
    if not auth or not auth["user"] or auth["user"].get("role") != "admin":
        raise HTTPException(403, "Access denied")
    return database


@app.get("/api/admin")
async def admin(request: Request):
    database = authorized(request)
    result = {}
    for name in ("services", "portfolio", "requests", "jobs", "applications"):
        rows = list(database[name].find({}, {"_id": 0}).sort([("sort_order", 1), ("rowid", -1)])) if name not in ("requests", "applications") else list(database[name].find({}, {"_id": 0}))
        result[name] = rows
    result["settings"] = {}
    for row in database.settings.find({}, {"_id": 1, "key": 1, "value": 1}):
        key = row.get("key") or str(row.get("_id", ""))
        if key:
            result["settings"][key] = str(row.get("value", ""))
    result["notifications"] = list(database.notifications.find({"target_role": "admin"}, {"_id": 0}).sort("created_at", -1).limit(100))
    result["users_count"] = database.users.count_documents({"role": "user"})
    return result


@app.patch("/api/admin/settings")
async def settings(request: Request):
    database = authorized(request)
    body = await request.json()
    updates = body.get("settings", {})
    if not isinstance(updates, dict):
        raise HTTPException(400, "Invalid settings")
    for key, value in updates.items():
        if not isinstance(value, str) or len(value) > 4500:
            raise HTTPException(400, "Invalid setting")
        database.settings.update_one(
            {"$or": [{"key": key}, {"_id": key}]},
            {"$set": {"key": key, "value": value}},
            upsert=True,
        )
    return {"ok": True}


@app.patch("/api/admin/prices")
async def prices(request: Request):
    database = authorized(request)
    body = await request.json()
    updates = body.get("prices", [])
    if not isinstance(updates, list) or len(updates) > 150:
        raise HTTPException(400, "Invalid price updates")
    count = 0
    for row in updates:
        rid = row.get("id")
        amount = row.get("starting_price")
        if not isinstance(rid, str) or isinstance(amount, bool) or not isinstance(amount, int) or amount < 0 or amount > 100000000:
            raise HTTPException(400, "Invalid price row")
        changed = database.services.update_one({"id": rid}, {"$set": {
            "starting_price": amount,
            "price_visible": int(row.get("price_visible", 0)),
            "featured_price": int(row.get("featured_price", 0)),
        }})
        if changed.matched_count:
            count += 1
    return {"ok": True, "count": count}


@app.patch("/api/admin/requests")
async def update_request(request: Request):
    database = authorized(request)
    body = await request.json()
    rid = str(body.get("id", ""))
    status = str(body.get("status", ""))
    note = str(body.get("admin_note", ""))
    if status not in {"New", "Reviewing", "Quoted", "In Progress", "Completed", "Closed"}:
        raise HTTPException(400, "Invalid status")
    changed = database.requests.update_one({"id": rid}, {"$set": {"status": status, "admin_note": note}})
    if not changed.matched_count:
        raise HTTPException(404, "Request not found")
    return {"ok": True}


@app.patch("/api/admin/applications")
async def update_application(request: Request):
    database = authorized(request)
    body = await request.json()
    aid = str(body.get("id", ""))
    status = str(body.get("status", ""))
    if status not in {"New", "Reviewed", "Contacted", "Archived"}:
        raise HTTPException(400, "Invalid status")
    changed = database.applications.update_one({"id": aid}, {"$set": {"status": status}})
    if not changed.matched_count:
        raise HTTPException(404, "Application not found")
    return {"ok": True}


@app.post("/api/notifications/read")
async def read_notification(request: Request):
    database = db()
    auth = get_session(database, request)
    if not auth:
        raise HTTPException(401, "Please sign in")
    body = await request.json()
    nid = str(body.get("id", ""))
    from datetime import datetime, timezone
    database.notifications.update_one({"id": nid}, {"$set": {"read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}})
    return {"ok": True}


@app.patch("/api/admin")
async def patch_dispatch(request: Request):
    database = authorized(request)
    body = await request.json()
    action = body.pop("action", "")
    if action == "settings":
        updates = body.get("settings", {})
        if not isinstance(updates, dict):
            raise HTTPException(400, "Invalid settings")
        for key, value in updates.items():
            if not isinstance(value, str) or len(value) > 4500:
                raise HTTPException(400, "Invalid setting")
            database.settings.update_one({"$or": [{"key": key}, {"_id": key}]}, {"$set": {"key": key, "value": value}}, upsert=True)
        return {"ok": True}
    if action == "prices":
        updates = body.get("prices", [])
        if not isinstance(updates, list):
            raise HTTPException(400, "Invalid price updates")
        count = 0
        for row in updates:
            rid = row.get("id")
            amount = row.get("starting_price")
            changed = database.services.update_one({"id": rid}, {"$set": {"starting_price": amount, "price_visible": int(row.get("price_visible", 0)), "featured_price": int(row.get("featured_price", 0))}})
            if changed.matched_count:
                count += 1
        return {"ok": True, "count": count}
    if action == "request":
        rid = str(body.get("id", ""))
        status = str(body.get("status", ""))
        note = str(body.get("admin_note", ""))
        changed = database.requests.update_one({"id": rid}, {"$set": {"status": status, "admin_note": note}})
        if not changed.matched_count:
            raise HTTPException(404, "Request not found")
        return {"ok": True}
    if action == "application":
        rid = str(body.get("id", ""))
        status = str(body.get("status", ""))
        changed = database.applications.update_one({"id": rid}, {"$set": {"status": status}})
        if not changed.matched_count:
            raise HTTPException(404, "Application not found")
        return {"ok": True}
    if action == "entity":
        kind = body.pop("kind", "")
        rid = body.pop("id", "")
        if kind not in ("services", "portfolio", "jobs") or not rid:
            raise HTTPException(400, "Invalid entity")
        changed = database[kind].update_one({"id": rid}, {"$set": body})
        if not changed.matched_count:
            raise HTTPException(404, "Record not found")
        return {"ok": True}
    raise HTTPException(400, "Unknown admin action")


@app.patch("/api/admin/{kind}")
async def patch_entity(kind: str, request: Request):
    if kind not in ("services", "portfolio", "jobs"):
        raise HTTPException(404, "API route not found")
    database = authorized(request)
    body = await request.json()
    rid = body.pop("id", "")
    if not rid:
        raise HTTPException(400, "Missing id")
    changed = database[kind].update_one({"id": rid}, {"$set": body})
    if not changed.matched_count:
        raise HTTPException(404, "Record not found")
    return {"ok": True}


@app.post("/api/admin")
async def post_dispatch(request: Request):
    database = authorized(request)
    body = await request.json()
    action = body.pop("action", "")
    if action == "read-notification":
        from datetime import datetime, timezone
        nid = str(body.get("id", ""))
        database.notifications.update_one({"id": nid}, {"$set": {"read_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}})
        return {"ok": True}
    if action == "entity":
        kind = body.pop("kind", "")
        if kind not in ("services", "portfolio", "jobs"):
            raise HTTPException(400, "Invalid entity")
        body.pop("id", None)
        import os
        body["id"] = body.get("slug") or body.get("title") or os.urandom(8).hex()
        database[kind].insert_one(body)
        return {"ok": True, "id": body["id"]}
    raise HTTPException(400, "Unknown admin action")


@app.post("/api/admin/{kind}")
async def create_entity(kind: str, request: Request):
    if kind not in ("services", "portfolio", "jobs"):
        raise HTTPException(404, "API route not found")
    database = authorized(request)
    body = await request.json()
    body.pop("id", None)
    body["id"] = body.get("slug") or body.get("title") or os.urandom(8).hex()
    database[kind].insert_one(body)
    return {"ok": True, "id": body["id"]}


@app.delete("/api/admin")
async def delete_dispatch(request: Request):
    database = authorized(request)
    body = await request.json()
    action = body.pop("action", "")
    if action != "entity":
        raise HTTPException(400, "Unknown admin action")
    kind = body.get("kind", "")
    rid = body.get("id", "")
    if kind not in ("services", "portfolio", "jobs") or not rid:
        raise HTTPException(400, "Invalid entity")
    database[kind].delete_one({"id": rid})
    return {"ok": True}


@app.delete("/api/admin/{kind}")
async def delete_entity(kind: str, request: Request):
    if kind not in ("services", "portfolio", "jobs"):
        raise HTTPException(404, "API route not found")
    database = authorized(request)
    rid = request.query_params.get("id", "")
    if not rid:
        raise HTTPException(400, "Missing id")
    database[kind].delete_one({"id": rid})
    return {"ok": True}


@app.get("/api/admin/record")
async def admin_record(request: Request, kind: str = "", id: str = ""):
    database = authorized(request)
    if kind not in ("services", "portfolio", "jobs", "requests", "applications"):
        raise HTTPException(400, "Invalid record")
    row = database[kind].find_one({"id": id}, {"_id": 0})
    if not row:
        raise HTTPException(404, "Record not found")
    return {"record": row}

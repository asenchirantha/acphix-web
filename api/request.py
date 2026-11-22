import os
import sys
import re
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


@app.post("/api/request")
async def create_request(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    details = str(body.get("details", "")).strip()
    if len(name) < 1 or len(details) < 1:
        raise HTTPException(400, "Enter your name and project details")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Enter a valid email address")

    database = db()
    auth = get_session(database, request)
    user_id = str(auth["user"]["_id"]) if auth and auth["user"] else None
    rid = str(uuid.uuid4())
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    database.requests.insert_one({
        "id": rid, "user_id": user_id, "name": name, "email": email,
        "company": str(body.get("company", "")).strip(), "phone": str(body.get("phone", "")).strip(),
        "service_id": str(body.get("service_id", "")), "budget": str(body.get("budget", "")),
        "details": details, "status": "New", "admin_note": "", "created_at": now, "updated_at": now,
    })
    database.notifications.insert_one({"id": str(uuid.uuid4()), "target_role": "admin", "title": "New project enquiry", "message": f"{name} sent a new request.", "kind": "request", "related_id": rid, "created_at": now, "read_at": None})
    return {"ok": True, "id": rid}

import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


@app.post("/api/notifications/read")
async def mark_read(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    database = db()
    result = get_session(database, request)
    if not result:
        raise HTTPException(401, "Please sign in")
    user_id = str(result["user"]["_id"])
    role = result["user"].get("role", "user")
    notification_id = str(body.get("id", ""))
    database.notifications.update_one(
        {"_id": notification_id, "$or": [{"target_user": user_id}, {"target_role": role}]},
        {"$set": {"read_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}},
    )
    return {"ok": True}

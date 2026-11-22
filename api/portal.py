import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


def public(row):
    if not row:
        return None
    result = dict(row)
    result["id"] = str(result.pop("_id", result.pop("id", "")))
    return result


@app.get("/api/portal")
async def portal(request: Request):
    database = db()
    result = get_session(database, request)
    if not result:
        raise HTTPException(401, "Please sign in")
    user = result["user"]
    user_id = str(user["_id"])
    role = user.get("role", "user")

    requests = [
        public(row)
        for row in database.requests.find({"user_id": user_id}).sort("created_at", -1)
    ]
    notifications = [
        public(row)
        for row in database.notifications.find({
            "$or": [{"target_user": user_id}, {"target_role": role}]
        }).sort("created_at", -1).limit(80)
    ]
    unread = sum(1 for note in notifications if not note.get("read_at"))
    return {"requests": requests, "notifications": notifications, "unread": unread}

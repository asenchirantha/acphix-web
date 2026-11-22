import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


@app.get("/api/portal")
async def portal(request: Request):
    database = db()
    auth = get_session(database, request)
    if not auth or not auth["user"]:
        raise HTTPException(401, "Please sign in")
    user = auth["user"]
    user_id = str(user["_id"])
    requests = list(database.requests.find({"user_id": user_id}, {"_id": 0}))
    notifications = list(database.notifications.find({"$or": [{"target_user": user_id}, {"target_role": user.get("role", "user")}]}, {"_id": 0}))
    return {"requests": requests, "notifications": notifications}

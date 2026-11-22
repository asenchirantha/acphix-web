import os
import sys
import re
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request
from mongo_store import db, get_session

app = FastAPI()


@app.post("/api/apply")
async def apply(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    message = str(body.get("message", "")).strip()
    if len(name) < 2 or len(message) < 12:
        raise HTTPException(400, "Enter your name and a short introduction")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Invalid email")
    portfolio_url = str(body.get("portfolio_url", "")).strip()
    if portfolio_url and not portfolio_url.startswith(("https://", "http://")):
        raise HTTPException(400, "Use a complete http(s) portfolio link")

    database = db()
    auth = get_session(database, request)
    user_id = str(auth["user"]["_id"]) if auth and auth["user"] else None
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds")
    aid = str(uuid.uuid4())
    database.applications.insert_one({"id": aid, "user_id": user_id, "job_id": str(body.get("job_id", "")), "name": name, "email": email, "portfolio_url": portfolio_url, "message": message, "created_at": now, "status": "New"})
    database.notifications.insert_one({"id": str(uuid.uuid4()), "target_role": "admin", "title": "New career interest", "message": f"{name} submitted a career enquiry.", "kind": "career", "related_id": aid, "created_at": now, "read_at": None})
    return {"ok": True}

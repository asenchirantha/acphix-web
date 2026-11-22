import os
import sys
import re
import time
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
    company = str(body.get("company", "")).strip()
    phone = str(body.get("phone", "")).strip()
    service_id = str(body.get("service_id", "")).strip()
    budget = str(body.get("budget", "")).strip()
    details = str(body.get("details", "")).strip()

    if len(name) < 2 or len(name) > 110:
        raise HTTPException(400, "Enter your name")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Enter a valid email address")
    if len(details) < 12:
        raise HTTPException(400, "Please describe your project in more detail")

    database = db()
    session = get_session(database, request)
    user_id = str(session["user"]["_id"]) if session else None
    created = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    request_id = str(uuid.uuid4())

    database.requests.insert_one({
        "_id": request_id,
        "user_id": user_id,
        "name": name,
        "email": email,
        "company": company,
        "phone": phone,
        "service_id": service_id,
        "budget": budget,
        "details": details,
        "status": "New",
        "admin_note": "",
        "created_at": created,
        "updated_at": created,
    })

    database.notifications.insert_one({
        "_id": str(uuid.uuid4()),
        "target_role": "admin",
        "target_user": None,
        "kind": "request",
        "title": "New project enquiry",
        "message": f"{name} sent a new request.",
        "related_id": request_id,
        "created_at": created,
        "read_at": None,
    })
    if user_id:
        database.notifications.insert_one({
            "_id": str(uuid.uuid4()),
            "target_role": "user",
            "target_user": user_id,
            "kind": "request",
            "title": "Request received",
            "message": "Your enquiry reached Acphix. You can follow its status from your portal.",
            "related_id": request_id,
            "created_at": created,
            "read_at": None,
        })

    return {"ok": True, "id": request_id}

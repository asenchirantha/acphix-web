import os
import sys
import re
import uuid

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request, Response
from mongo_store import db, hash_password, create_session

app = FastAPI()


@app.post("/api/register")
async def register(request: Request, response: Response):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")

    name = str(body.get("name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    if len(name) < 2 or len(name) > 90:
        raise HTTPException(400, "Enter your full name")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(400, "Enter a valid email address")
    if len(password) < 10:
        raise HTTPException(400, "Password must be at least 10 characters")

    database = db()
    if database.users.find_one({"email": email}):
        raise HTTPException(409, "An account already uses this email")

    user_id = str(uuid.uuid4())
    database.users.insert_one({"_id": user_id, "name": name, "email": email, "password_hash": hash_password(password), "role": "user"})
    token, csrf = create_session(database, {"_id": user_id})
    secure = os.environ.get("ACPHIX_SECURE_COOKIE", "0") == "1"
    response.set_cookie("acphix_session", token, httponly=True, samesite="lax", secure=secure, max_age=604800, path="/")
    return {"ok": True, "user": {"id": user_id, "name": name, "email": email, "role": "user"}, "csrf": csrf}

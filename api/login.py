import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, HTTPException, Request, Response
from mongo_store import db, verify_password, create_session

app = FastAPI()


@app.post("/api/login")
async def login(request: Request, response: Response):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))

    database = db()
    user = database.users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(401, "Incorrect email or password")

    user_id = str(user["_id"])
    token, csrf = create_session(database, {"_id": user_id})
    secure = os.environ.get("ACPHIX_SECURE_COOKIE", "0") == "1"
    response.set_cookie("acphix_session", token, httponly=True, samesite="lax", secure=secure, max_age=604800, path="/")
    return {"ok": True, "user": {"id": user_id, "name": user["name"], "email": user["email"], "role": user["role"]}, "csrf": csrf}

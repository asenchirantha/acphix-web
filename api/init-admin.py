import base64
import hashlib
import json
import os
import secrets

from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient

app = FastAPI()


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 320_000)
    return "pbkdf2_sha256$320000$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


@app.post("/api/init-admin")
async def init_admin(request: Request):
    uri = os.environ.get("MONGODB_URI")
    bootstrap_password = os.environ.get("ADMIN_BOOTSTRAP_PASSWORD")
    if not uri or not bootstrap_password:
        raise HTTPException(500, "MongoDB or bootstrap configuration is missing")

    try:
        body = await request.json()
    except Exception:
        body = {}

    password = str(body.get("password", ""))
    email = str(body.get("email", "asen.chirantha@gmail.com")).strip().lower()
    name = str(body.get("name", "Acphix Admin")).strip()

    if password != bootstrap_password:
        raise HTTPException(403, "Invalid bootstrap password")
    if len(password) < 12:
        raise HTTPException(400, "Password must contain at least 12 characters")

    database = os.environ.get("MONGODB_DATABASE", "acphix")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client[database]
    db.users.update_one(
        {"email": email},
        {"$set": {"name": name, "email": email, "password_hash": hash_password(password), "role": "admin"}},
        upsert=True,
    )
    db.admin_bootstrap.update_one(
        {"name": "primary"},
        {"$set": {"email": email, "completed": True}},
        upsert=True,
    )
    return {"ok": True, "email": email, "role": "admin"}

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
import uuid

from pymongo import MongoClient


def db():
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not configured")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    return client[os.environ.get("MONGODB_DATABASE", "acphix")]


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 320000)
    return "pbkdf2_sha256$320000$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


def verify_password(password, encoded):
    try:
        mode, rounds, salt, expected = encoded.split("$")
        if mode != "pbkdf2_sha256":
            return False
        got = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt), int(rounds))
        return hmac.compare_digest(got, base64.urlsafe_b64decode(expected))
    except Exception:
        return False


def migrate_sqlite(database):
    if database.settings.count_documents({}) and database.services.count_documents({}) and database.portfolio.count_documents({}):
        return
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "data", "acphix.sqlite3")
    if not os.path.isfile(path):
        return
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    tables = {
        "settings": "site_settings",
        "services": "services",
        "portfolio": "portfolio",
        "requests": "requests",
        "jobs": "jobs",
        "applications": "applications",
        "notifications": "notifications",
        "users": "users",
    }
    for mongo_name, sqlite_name in tables.items():
        try:
            rows = [dict(row) for row in con.execute(f"SELECT * FROM {sqlite_name}")]
            for row in rows:
                key_field = "key" if mongo_name == "settings" else "id"
                mongo_id = str(row.get(key_field) or uuid.uuid4().hex)
                row["_id"] = mongo_id
                if mongo_name != "settings":
                    row.setdefault("id", mongo_id)
                database[mongo_name].replace_one({"_id": mongo_id}, row, upsert=True)
        except sqlite3.Error:
            pass
    con.close()


def get_session(database, request):
    token = request.cookies.get("acphix_session")
    if not token:
        return None
    session = database.sessions.find_one({"token_hash": hashlib.sha256(token.encode()).hexdigest()})
    if not session or session.get("expires_at", 0) <= int(time.time()):
        return None
    user = database.users.find_one({"_id": session.get("user_id")})
    if not user:
        user = database.users.find_one({"id": session.get("user_id")})
    return {"session": session, "user": user}


def create_session(database, user):
    token = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(30)
    database.sessions.update_one(
        {"user_id": str(user["_id"])},
        {"$set": {"token_hash": hashlib.sha256(token.encode()).hexdigest(), "csrf": csrf, "expires_at": int(time.time()) + 604800}},
        upsert=True,
    )
    return token, csrf

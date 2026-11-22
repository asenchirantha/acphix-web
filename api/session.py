import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, Request
from mongo_store import db, get_session

app = FastAPI()


@app.get("/api/session")
async def session(request: Request):
    database = db()
    result = get_session(database, request)
    if not result:
        return {"user": None}
    user = result["user"]
    session = result["session"]
    return {"user": {"id": str(user["_id"]), "name": user["name"], "email": user["email"], "role": user["role"]}, "csrf": session["csrf"]}

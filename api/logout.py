import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, Request, Response
from mongo_store import db, get_session

app = FastAPI()


@app.post("/api/logout")
async def logout(request: Request, response: Response):
    database = db()
    auth = get_session(database, request)
    if auth:
        database.sessions.delete_one({"token_hash": auth["session"]["token_hash"]})
    response.delete_cookie("acphix_session", path="/")
    return {"ok": True}

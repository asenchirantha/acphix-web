import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI, Request, Response
from mongo_store import db, get_session

app = FastAPI()


@app.post("/api/logout")
async def logout(request: Request, response: Response):
    database = db()
    result = get_session(database, request)
    if result:
        database.sessions.delete_one({"_id": result["session"]["_id"]})
        database.sessions.delete_many({"token_hash": result["session"]["token_hash"]})
    response.delete_cookie("acphix_session", path="/")
    return {"ok": True}

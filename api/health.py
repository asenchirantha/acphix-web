import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI
from mongo_store import db

app = FastAPI()


@app.get("/api/health")
async def health():
    database = db()
    database.command("ping")
    return {"ok": True, "database": os.environ.get("MONGODB_DATABASE", "acphix")}

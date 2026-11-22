import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fastapi import FastAPI
from mongo_store import db, migrate_sqlite

app = FastAPI()


@app.get("/api/bootstrap")
async def bootstrap():
    database = db()
    migrate_sqlite(database)
    settings = {}
    for row in database.settings.find({}, {"key": 1, "value": 1, "_id": 1}):
        key = row.get("key") or str(row.get("_id", ""))
        if key:
            settings[key] = str(row.get("value", ""))
    services = list(database.services.find({"published": {"$ne": 0}}, {"_id": 0}).sort("sort_order", 1))
    portfolio = list(database.portfolio.find({"published": {"$ne": 0}}, {"_id": 0}).sort("sort_order", 1))
    jobs = list(database.jobs.find({"active": {"$ne": 0}}, {"_id": 0}).sort("created_at", -1))
    return {"settings": settings, "services": services, "portfolio": portfolio, "jobs": jobs}

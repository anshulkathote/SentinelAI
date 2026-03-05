# backend/routers/config.py
import json
from fastapi import APIRouter
from pydantic import BaseModel
from backend.state import state

router = APIRouter(prefix="/config", tags=["config"])

class ConfigUpdate(BaseModel):
    risk_threshold: int | None = None

@router.get("/")
def get_config():
    """Return current zones and threshold config"""
    try:
        with open("data/zones.json") as f:
            zones = json.load(f)
    except Exception:
        zones = {}
    try:
        with open("data/config.json") as f:
            config = json.load(f)
    except Exception:
        config = {"risk_threshold": 60}

    return {**config, **zones}

@router.post("/")
def update_config(update: ConfigUpdate):
    """Update risk threshold"""
    try:
        with open("data/config.json") as f:
            config = json.load(f)
    except Exception:
        config = {}

    if update.risk_threshold is not None:
        config["risk_threshold"] = update.risk_threshold

    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)

    return {"message": "Config updated", "config": config}
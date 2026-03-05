# backend/routers/health.py
import time
import torch
from fastapi import APIRouter
from backend.state import state

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    """System status + GPU info"""
    uptime = int(time.time() - state.uptime_start)
    return {
        "status":          "running" if state.is_running else "stopped",
        "uptime_seconds":  uptime,
        "total_frames":    state.total_frames,
        "total_alerts":    len(state.alerts),
        "persons_now":     state.persons_now,
        "gpu_available":   torch.cuda.is_available(),
        "gpu_name":        torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
    }
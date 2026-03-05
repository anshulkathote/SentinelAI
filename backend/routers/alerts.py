# backend/routers/alerts.py
from fastapi import APIRouter, HTTPException
from backend.state import state

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/")
def get_alerts():
    """Return all alerts fired this session"""
    return {
        "total":  len(state.alerts),
        "alerts": list(reversed(state.alerts))  # newest first
    }

@router.delete("/{alert_id}")
def delete_alert(alert_id: str):
    """Dismiss/delete an alert by ID"""
    original = len(state.alerts)
    state.alerts = [a for a in state.alerts if a.get("id") != alert_id]
    if len(state.alerts) == original:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": f"Alert {alert_id} dismissed"}

@router.delete("/")
def clear_all_alerts():
    """Clear all alerts"""
    state.alerts = []
    return {"message": "All alerts cleared"}
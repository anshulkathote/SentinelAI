# backend/websocket.py — WebSocket connection manager
import json
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active)}")

    async def broadcast(self, data: dict):
        """Send JSON payload to all connected dashboard clients"""
        if not self.active:
            return
        message = json.dumps(data)
        dead    = []
        for ws in self.active:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

# Single shared instance
manager = ConnectionManager()
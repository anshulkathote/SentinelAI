# backend/main.py — FastAPI app entry point
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from backend.websocket       import manager
from backend.pipeline_runner import start_pipeline
from backend.routers         import alerts, stream, health, config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start pipeline in background thread on startup
    loop = asyncio.get_event_loop()
    start_pipeline(loop)
    yield
    # Cleanup on shutdown handled by daemon thread

app = FastAPI(
    title="SentinelAI API",
    description="Smart Threat Detection — Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# Allow React dev server to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve alert snapshots as static files
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")

# Routers
app.include_router(health.router)
app.include_router(alerts.router)
app.include_router(stream.router)
app.include_router(config.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive — pipeline thread does the broadcasting
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def root():
    return {
        "message": "SentinelAI API running",
        "docs":    "http://localhost:8000/docs",
        "stream":  "http://localhost:8000/stream",
        "ws":      "ws://localhost:8000/ws"
    }
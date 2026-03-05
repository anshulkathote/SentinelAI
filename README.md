# 🛡️ SentinelAI — Smart Threat Detection

AI-powered DVR with a 5-layer intelligent filtering pipeline that detects only genuine human threats, eliminates false triggers, and replaces manual monitoring with automated behavior-aware surveillance.

**Team CtrlZ — HackArena '26 | PS-01 ThreatSense AI-DVR**

## Tech Stack
- YOLOv8 — Person detection
- DeepSORT — Multi-person tracking  
- MediaPipe — Pose estimation (aggression, climbing, crouching)
- FastAPI — Backend + WebSocket
- React.js — Live dashboard
- PyTorch + CUDA — GPU acceleration

## How It Works
Video Stream → YOLOv8 Detection → DeepSORT Tracking → Behavior Analysis → Risk Scoring → Smart Alert

## Run
```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Dashboard
cd dashboard && npm install && npm start
```
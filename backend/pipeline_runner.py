# backend/pipeline_runner.py — Runs AI pipeline in background thread
import cv2
import json
import time
import threading
import asyncio

from pipeline.capture     import VideoCapture
from pipeline.detector    import PersonDetector
from pipeline.tracker     import PersonTracker
from pipeline.behavior    import BehaviorAnalyzer
from pipeline.risk_engine import RiskEngine
from pipeline.alert       import AlertHandler
from pipeline.pose        import PoseAnalyzer
from pipeline.visualizer  import draw

from backend.state     import state
from backend.websocket import manager

VIDEO_SOURCE = "demo/demo.mp4"   # change to 0 or rtsp://...
FRAME_SKIP   = 2

def load_zones():
    try:
        with open("data/zones.json") as f:
            return json.load(f).get("restricted_zones", [])
    except Exception:
        return []

def encode_frame(frame):
    """Convert OpenCV frame to JPEG bytes"""
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return buffer.tobytes()

def run_pipeline(loop: asyncio.AbstractEventLoop):
    """Runs in a background thread — feeds state + websocket"""
    cap      = VideoCapture(VIDEO_SOURCE)
    detector = PersonDetector()
    tracker  = PersonTracker()
    behavior = BehaviorAnalyzer()
    risk     = RiskEngine(threshold=60)
    alert    = AlertHandler()
    pose     = PoseAnalyzer()
    zones    = load_zones()

    frame_count  = 0
    last_tracks  = []
    last_scored  = []
    pose_results = {}

    state.is_running = True
    print("\n✅ Background pipeline started\n")

    while state.is_running:
        ret, frame = cap.read_frame()
        if not ret:
            # Loop video
            cap.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        alert.add_frame(frame)
        frame_count       += 1
        state.total_frames = frame_count

        if frame_count % FRAME_SKIP == 0:
            detections          = detector.detect(frame)
            last_tracks         = tracker.update(detections, frame)
            pose_results, frame = pose.analyze(frame, last_tracks)
            behavior_results    = behavior.update_with_pose(
                last_tracks, frame.shape, pose_results
            )
            last_scored  = risk.score(behavior_results)
            new_alerts   = alert.handle(frame, last_scored)

            # Update shared state
            state.current_tracks = last_scored
            state.persons_now    = len(last_tracks)
            if new_alerts:
                state.alerts.extend(new_alerts)

            # Build WebSocket payload
            payload = {
                "type":            "frame_update",
                "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%S"),
                "active_tracks":   last_scored,
                "new_alerts":      new_alerts,
                "total_alerts":    len(state.alerts),
                "persons_detected": len(last_tracks)
            }

            # Broadcast to all dashboard clients (thread-safe)
            asyncio.run_coroutine_threadsafe(
                manager.broadcast(payload), loop
            )

        # Draw annotations
        vis = draw(frame.copy(), last_tracks, last_scored, zones)

        # Pose labels
        for track in last_tracks:
            tid   = track["track_id"]
            x1, y1 = track["bbox"][0], track["bbox"][1]
            label = pose_results.get(tid, {}).get("pose_behavior", "")
            if label and label != "walking":
                cv2.putText(vis, f"[{label}]", (x1, y1 - 28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # HUD
        cv2.putText(vis, f"Persons: {len(last_tracks)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(vis, f"Alerts : {len(state.alerts)}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)

        # Store latest frame for MJPEG stream
        state.latest_frame = encode_frame(vis)

    cap.release()
    print("Pipeline stopped.")

def start_pipeline(loop: asyncio.AbstractEventLoop):
    t = threading.Thread(target=run_pipeline, args=(loop,), daemon=True)
    t.start()
    return t
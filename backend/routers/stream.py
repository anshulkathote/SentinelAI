# backend/routers/stream.py
import time
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.state import state

router = APIRouter(tags=["stream"])

def mjpeg_generator():
    """Yields MJPEG frames from the latest pipeline frame"""
    while True:
        frame = state.latest_frame
        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + frame +
                b"\r\n"
            )
        time.sleep(0.033)  # ~30fps

@router.get("/stream")
def video_stream():
    """MJPEG live stream — use as <img src='/stream' /> in React"""
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
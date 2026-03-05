# pipeline/capture.py
import cv2

class VideoCapture:
    def __init__(self, source=0):
        """
        source can be:
        - 0 for webcam
        - "demo/demo.mp4" for local video file
        - "rtsp://..." for IP camera
        """
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {source}")

        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 25
        print(f"[Capture] Source opened. FPS: {self.fps}")

    def read_frame(self):
        """Returns (success, frame)"""
        ret, frame = self.cap.read()
        if not ret:
            return False, None
        # Resize to 1280x720 for consistent processing
        frame = cv2.resize(frame, (1280, 720))
        return True, frame

    def release(self):
        self.cap.release()
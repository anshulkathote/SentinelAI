# pipeline/detector.py
from ultralytics import YOLO
import torch

class PersonDetector:
    def __init__(self, model_size="yolov8s.pt", confidence=0.45):
        self.model = YOLO(model_size)
        self.confidence = confidence
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Detector] Running on: {self.device}")

    def detect(self, frame):
        """
        Returns list of dicts:
        [{ 'bbox': [x1,y1,x2,y2], 'confidence': 0.87 }, ...]
        Only 'person' class (class_id=0 in COCO)
        """
        results = self.model(
            frame,
            device=self.device,
            conf=self.confidence,
            classes=[0],        # 0 = person only
            verbose=False
        )[0]

        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": round(conf, 3)
            })

        return detections
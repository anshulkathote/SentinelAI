# pipeline/tracker.py
from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(
            max_age=30,           # frames to keep lost track
            n_init=3,             # frames before track confirmed
            nms_max_overlap=0.7,
            max_cosine_distance=0.3,
        )
        print("[Tracker] DeepSORT initialized")

    def update(self, detections, frame):
        """
        detections: list of {'bbox': [x1,y1,x2,y2], 'confidence': float}
        Returns list of active tracks:
        [{'track_id': int, 'bbox': [x1,y1,x2,y2]}, ...]
        """
        if not detections:
            self.tracker.update_tracks([], frame=frame)
            return []

        # DeepSORT expects [[x1,y1,w,h], conf, class]
        raw = []
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            w, h = x2 - x1, y2 - y1
            raw.append(([x1, y1, w, h], d["confidence"], "person"))

        tracks = self.tracker.update_tracks(raw, frame=frame)

        active = []
        for track in tracks:
            if not track.is_confirmed():
                continue
            x1, y1, x2, y2 = map(int, track.to_ltrb())
            active.append({
                "track_id": int(track.track_id),
                "bbox": [x1, y1, x2, y2]
            })

        return active
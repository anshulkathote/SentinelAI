# pipeline/visualizer.py
import cv2
import numpy as np

RISK_COLORS = {
    (0, 30):   (0, 255, 0),    # Green - safe
    (30, 60):  (0, 165, 255),  # Orange - watch
    (60, 100): (0, 0, 255),    # Red - alert
}

def get_color(score):
    for (lo, hi), color in RISK_COLORS.items():
        if lo <= score < hi:
            return color
    return (0, 0, 255)

def draw(frame, tracks, scored_tracks, zones):
    score_map = {t["track_id"]: t for t in scored_tracks}

    # Draw zones
    for zone in zones:
        pts = np.array(zone["points"], dtype=np.int32)
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 0, 255))
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
        cv2.polylines(frame, [pts], True, (0, 0, 255), 2)

    # Draw tracks
    for track in tracks:
        tid = track["track_id"]
        x1, y1, x2, y2 = track["bbox"]
        scored = score_map.get(tid, {})
        risk = scored.get("risk_score", 0)
        color = get_color(risk)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        label = f"ID:{tid} Risk:{risk}"
        behaviors = scored.get("behaviors", [])
        if behaviors:
            label += f" [{', '.join(b.split(':')[0] for b in behaviors)}]"

        cv2.putText(frame, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

    return frame
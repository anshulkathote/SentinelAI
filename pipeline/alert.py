# pipeline/alert.py
import cv2
import os
import time
import json

SNAPSHOTS_DIR = "snapshots"
ALERTS_LOG = "snapshots/alerts.json"

os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

class AlertHandler:
    def __init__(self):
        self.alerts = []

    def handle(self, frame, scored_tracks):
        """Check scored tracks, save snapshot + log if alert=True"""
        new_alerts = []

        for track in scored_tracks:
            if not track["alert"]:
                continue

            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{SNAPSHOTS_DIR}/alert_{track['track_id']}_{ts}.jpg"
            cv2.imwrite(filename, frame)

            alert_data = {
                "timestamp": ts,
                "track_id": track["track_id"],
                "risk_score": track["risk_score"],
                "behaviors": track["behaviors"],
                "duration": track["duration"],
                "snapshot": filename
            }

            self.alerts.append(alert_data)
            new_alerts.append(alert_data)

            # Save log
            with open(ALERTS_LOG, "w") as f:
                json.dump(self.alerts, f, indent=2)

            print(f"🚨 ALERT! Track {track['track_id']} | "
                  f"Risk: {track['risk_score']} | "
                  f"Behaviors: {track['behaviors']}")

        return new_alerts
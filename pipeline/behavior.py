# pipeline/behavior.py
import time
import cv2
import json
import numpy as np

class BehaviorAnalyzer:
    def __init__(self, zones_path="data/zones.json"):
        # Track history per person: {track_id: {'first_seen': t, 'positions': []}}
        self.track_history = {}

        # Load restricted zones
        try:
            with open(zones_path) as f:
                data = json.load(f)
                self.zones = data.get("restricted_zones", [])
        except FileNotFoundError:
            self.zones = []
            print("[Behavior] No zones.json found — zone detection disabled")

        print(f"[Behavior] Loaded {len(self.zones)} restricted zones")

    def update(self, tracks, frame_shape):
        """
        Returns list of behavior flags per track:
        [{'track_id': int, 'behaviors': ['loitering', 'in_restricted_zone'], 'duration': float}, ...]
        """
        now = time.time()
        results = []

        active_ids = {t["track_id"] for t in tracks}

        # Clean up lost tracks older than 60s
        lost = [tid for tid in self.track_history
                if tid not in active_ids and
                now - self.track_history[tid]["last_seen"] > 60]
        for tid in lost:
            del self.track_history[tid]

        for track in tracks:
            tid = track["track_id"]
            bbox = track["bbox"]
            cx = (bbox[0] + bbox[2]) // 2
            cy = (bbox[1] + bbox[3]) // 2

            if tid not in self.track_history:
                self.track_history[tid] = {
                    "first_seen": now,
                    "last_seen": now,
                    "positions": [(cx, cy)]
                }
            else:
                self.track_history[tid]["last_seen"] = now
                self.track_history[tid]["positions"].append((cx, cy))
                # Keep last 150 positions (~30s at 5fps)
                self.track_history[tid]["positions"] = \
                    self.track_history[tid]["positions"][-150:]

            duration = now - self.track_history[tid]["first_seen"]
            behaviors = []

            # --- Loitering: in frame > 30 seconds ---
            if duration > 30:
                behaviors.append("loitering")

            # --- Restricted zone check ---
            for zone in self.zones:
                polygon = np.array(zone["points"], dtype=np.int32)
                if cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0:
                    behaviors.append(f"in_restricted_zone:{zone['name']}")
                    break

            # --- Rapid movement (aggression proxy) ---
            positions = self.track_history[tid]["positions"]
            if len(positions) >= 10:
                recent = positions[-10:]
                distances = [
                    np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                    for p1, p2 in zip(recent, recent[1:])
                ]
                avg_speed = np.mean(distances)
                if avg_speed > 25:
                    behaviors.append("rapid_movement")

            results.append({
                "track_id": tid,
                "behaviors": behaviors,
                "duration": round(duration, 1),
                "position": (cx, cy)
            })

        return results

    def update_with_pose(self, tracks, frame_shape, pose_results):
        """
        Same as update() but also merges in pose-detected behaviors.
        pose_results: dict of {track_id: {'pose_behavior': str, 'keypoints': dict}}
        """
        base_results = self.update(tracks, frame_shape)

        for result in base_results:
            tid = result["track_id"]

            # Safely get pose data
            pose_data = {}
            if isinstance(pose_results, dict):
                pose_data = pose_results.get(tid, {})

            # Safely get pose behavior
            pose_behavior = "unknown"
            if isinstance(pose_data, dict):
                pose_behavior = pose_data.get("pose_behavior", "unknown")

            # Only add notable/threatening behaviors
            if pose_behavior in ["aggression", "climbing", "crouching", "fallen"]:
                result["behaviors"].append(pose_behavior)

        return base_results
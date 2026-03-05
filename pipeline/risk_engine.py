# pipeline/risk_engine.py
import time

# Update BEHAVIOR_SCORES dict in risk_engine.py
BEHAVIOR_SCORES = {
    "loitering":          30,
    "rapid_movement":     40,
    "in_restricted_zone": 50,
    "aggression":         60,   # ← new
    "climbing":           55,   # ← new
    "crouching":          35,   # ← new
    "fallen":             45,   # ← new (person may need help)
    "running":            20,   # ← new
}

TIME_MULTIPLIER_NIGHT = 1.3     # 10pm - 6am
ALERT_THRESHOLD = 60            # fire alert above this

class RiskEngine:
    def __init__(self, threshold=ALERT_THRESHOLD):
        self.threshold = threshold
        self.alert_cooldown = {}   # track_id -> last alert time
        self.COOLDOWN_SECONDS = 30

    def _is_night(self):
        hour = time.localtime().tm_hour
        return hour >= 22 or hour < 6

    def score(self, behavior_results):
        """
        Returns list of scored tracks, fires alert if threshold exceeded.
        [{'track_id': int, 'risk_score': int, 'alert': bool, 'behaviors': list}, ...]
        """
        now = time.time()
        scored = []

        for result in behavior_results:
            tid = result["track_id"]
            risk = 0

            for behavior in result["behaviors"]:
                # Handle prefix-matched behaviors (restricted zones)
                for key, score in BEHAVIOR_SCORES.items():
                    if behavior.startswith(key):
                        risk += score

            # Duration bonus
            if result["duration"] > 120:  # 2 minutes
                risk += 20

            # Night multiplier
            if self._is_night():
                risk = int(risk * TIME_MULTIPLIER_NIGHT)

            # Cap at 100
            risk = min(risk, 100)

            # Alert logic with cooldown
            should_alert = False
            if risk >= self.threshold:
                last_alert = self.alert_cooldown.get(tid, 0)
                if now - last_alert > self.COOLDOWN_SECONDS:
                    should_alert = True
                    self.alert_cooldown[tid] = now

            scored.append({
                "track_id": tid,
                "risk_score": risk,
                "alert": should_alert,
                "behaviors": result["behaviors"],
                "duration": result["duration"]
            })

        return scored
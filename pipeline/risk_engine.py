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


# # pipeline/risk_engine.py

# import time
# from pipeline.alert import AlertHandler


# # Behavior risk scores
# BEHAVIOR_SCORES = {
#     "loitering": 30,
#     "rapid_movement": 40,
#     "in_restricted_zone": 50,
#     "aggression": 60,
#     "climbing": 55,
#     "crouching": 35,
#     "fallen": 45,
#     "running": 20,
# }

# TIME_MULTIPLIER_NIGHT = 1.3
# ALERT_THRESHOLD = 60


# class RiskEngine:

#     def __init__(self, threshold=ALERT_THRESHOLD):

#         self.threshold = threshold
#         self.alert_cooldown = {}
#         self.COOLDOWN_SECONDS = 30

#         # initialize alert handler
#         self.alert_handler = AlertHandler()

#     def _is_night(self):

#         hour = time.localtime().tm_hour
#         return hour >= 22 or hour < 6

#     def score(self, behavior_results):

#         """
#         Returns scored tracks.
#         """

#         now = time.time()
#         scored_tracks = []

#         for result in behavior_results:

#             track_id = result["track_id"]
#             behaviors = result["behaviors"]
#             duration = result["duration"]

#             risk = 0

#             # behavior score
#             for behavior in behaviors:
#                 for key, score in BEHAVIOR_SCORES.items():
#                     if behavior.startswith(key):
#                         risk += score

#             # duration bonus
#             if duration > 120:
#                 risk += 20

#             # night multiplier
#             if self._is_night():
#                 risk = int(risk * TIME_MULTIPLIER_NIGHT)

#             # cap risk
#             risk = min(risk, 100)

#             should_alert = False

#             if risk >= self.threshold:

#                 last_alert = self.alert_cooldown.get(track_id, 0)

#                 if now - last_alert > self.COOLDOWN_SECONDS:

#                     should_alert = True
#                     self.alert_cooldown[track_id] = now

#                     # Send WhatsApp alert
#                     self.alert_handler.send(
#                         track_id=track_id,
#                         risk_score=risk,
#                         behaviors=behaviors
#                     )

#             scored_tracks.append({

#                 "track_id": track_id,
#                 "risk_score": risk,
#                 "alert": should_alert,
#                 "behaviors": behaviors,
#                 "duration": duration

#             })

#         return scored_tracks
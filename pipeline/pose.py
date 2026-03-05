# pipeline/pose.py
import mediapipe as mp
import numpy as np
import cv2

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# MediaPipe landmark indices
NOSE         = 0
LEFT_SHOULDER  = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW     = 13
RIGHT_ELBOW    = 14
LEFT_WRIST     = 15
RIGHT_WRIST    = 16
LEFT_HIP       = 23
RIGHT_HIP      = 24
LEFT_KNEE      = 25
RIGHT_KNEE     = 26
LEFT_ANKLE     = 27
RIGHT_ANKLE    = 28

class PoseAnalyzer:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        # Store pose history per track: {track_id: [pose_snapshots]}
        self.pose_history = {}
        print("[Pose] MediaPipe Pose initialized")

    def _get_landmark(self, landmarks, index, frame_w, frame_h):
        """Returns (x, y) pixel coords of a landmark"""
        lm = landmarks[index]
        return (int(lm.x * frame_w), int(lm.y * frame_h))

    def _angle(self, a, b, c):
        """Angle at point B formed by A-B-C"""
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

    def analyze(self, frame, tracks):
        """
        For each tracked person, crop their bbox region,
        run MediaPipe pose, detect behavior from keypoints.

        Returns:
        {track_id: {'pose_behavior': str, 'keypoints': dict, 'draw_frame': frame}}
        """
        h, w = frame.shape[:2]
        results = {}

        for track in tracks:
            tid = track["track_id"]
            x1, y1, x2, y2 = track["bbox"]

            # Clamp bbox to frame
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x2 - x1 < 50 or y2 - y1 < 100:
                continue  # too small to analyze

            # Crop person region
            crop = frame[y1:y2, x1:x2]
            crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

            pose_result = self.pose.process(crop_rgb)

            if not pose_result.pose_landmarks:
                results[tid] = {"pose_behavior": "unknown", "keypoints": {}}
                continue

            lms = pose_result.pose_landmarks.landmark
            ch, cw = crop.shape[:2]

            # Get key points (relative to crop)
            def get(idx):
                return self._get_landmark(lms, idx, cw, ch)

            l_shoulder = get(LEFT_SHOULDER)
            r_shoulder = get(RIGHT_SHOULDER)
            l_wrist    = get(LEFT_WRIST)
            r_wrist    = get(RIGHT_WRIST)
            l_hip      = get(LEFT_HIP)
            r_hip      = get(RIGHT_HIP)
            l_knee     = get(LEFT_KNEE)
            r_knee     = get(RIGHT_KNEE)
            l_ankle    = get(LEFT_ANKLE)
            r_ankle    = get(RIGHT_ANKLE)
            l_elbow    = get(LEFT_ELBOW)
            r_elbow    = get(RIGHT_ELBOW)

            # Average points
            shoulder_y = (l_shoulder[1] + r_shoulder[1]) / 2
            hip_y      = (l_hip[1] + r_hip[1]) / 2
            knee_y     = (l_knee[1] + r_knee[1]) / 2
            ankle_y    = (l_ankle[1] + r_ankle[1]) / 2
            wrist_y    = (l_wrist[1] + r_wrist[1]) / 2

            # Store snapshot for history
            snapshot = {
                "shoulder_y": shoulder_y,
                "hip_y": hip_y,
                "wrist_y": wrist_y,
                "knee_y": knee_y
            }
            if tid not in self.pose_history:
                self.pose_history[tid] = []
            self.pose_history[tid].append(snapshot)
            self.pose_history[tid] = self.pose_history[tid][-30:]  # last 30 frames

            behavior = self._classify(
                shoulder_y, hip_y, knee_y, ankle_y,
                wrist_y, l_wrist, r_wrist,
                l_shoulder, r_shoulder,
                l_elbow, r_elbow, ch,
                tid
            )

            # Draw skeleton on original frame (mapped back to full frame)
            mp_draw.draw_landmarks(
                frame[y1:y2, x1:x2],
                pose_result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0,255,255), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(0,128,255), thickness=2)
            )

            results[tid] = {
                "pose_behavior": behavior,
                "keypoints": {
                    "shoulder_y": shoulder_y,
                    "hip_y": hip_y,
                    "wrist_y": wrist_y
                }
            }

        return results, frame

    def _classify(self, shoulder_y, hip_y, knee_y, ankle_y,
                  wrist_y, l_wrist, r_wrist,
                  l_shoulder, r_shoulder,
                  l_elbow, r_elbow, frame_h, tid):
        """
        Rule-based pose classification from keypoint geometry.
        Returns a string behavior label.
        """
        history = self.pose_history.get(tid, [])

        # --- FALLEN: shoulders near ankle level ---
        body_height = ankle_y - shoulder_y
        if body_height < frame_h * 0.25:
            return "fallen"

        # --- CROUCHING/SNEAKING: hip drops below knee level ---
        if hip_y > knee_y * 0.95:
            return "crouching"

        # --- CLIMBING: wrists above shoulders + knees bent ---
        knee_angle_l = self._angle(l_shoulder, (
            (l_shoulder[0] + r_shoulder[0])//2,
            int(hip_y)
        ), l_wrist)

        wrists_raised = wrist_y < shoulder_y  # smaller y = higher up
        knees_bent = knee_y > hip_y * 1.1

        if wrists_raised and knees_bent:
            return "climbing"

        # --- AGGRESSION: rapid wrist elevation changes ---
        if len(history) >= 10:
            recent_wrists = [s["wrist_y"] for s in history[-10:]]
            wrist_variance = np.var(recent_wrists)
            if wrist_variance > 800:
                return "aggression"

        # --- RUNNING: high vertical hip movement ---
        if len(history) >= 6:
            recent_hips = [s["hip_y"] for s in history[-6:]]
            hip_variance = np.var(recent_hips)
            if hip_variance > 300:
                return "running"

        return "walking"
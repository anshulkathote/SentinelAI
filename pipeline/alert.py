# pipeline/alert.py
import cv2
import os
import time
import json
import uuid
import threading
from collections import deque

SNAPSHOTS_DIR = "snapshots"
CLIPS_DIR     = "snapshots/clips"
ALERTS_LOG    = "snapshots/alerts.json"

os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
os.makedirs(CLIPS_DIR, exist_ok=True)

class AlertHandler:
    def __init__(self, fps=25, buffer_seconds=5):
        self.alerts       = []
        self.fps          = fps
        self.buffer_seconds = buffer_seconds

        # Rolling frame buffer — keeps last 5 seconds of frames
        maxlen = fps * buffer_seconds
        self.frame_buffer = deque(maxlen=maxlen)

        # Email config — set these
        self.email_enabled  = True
        self.sender_email   = "gskarale2006@gmail.com"
        self.app_password   = "akip aofi mqst mngv"
        self.receiver_email = "anshulkathote@gmail.com"

    def add_frame(self, frame):
        """Call this every frame to maintain rolling buffer"""
        self.frame_buffer.append(frame.copy())

    def handle(self, frame, scored_tracks):
        """Check scored tracks, save snapshot + clip + send email"""
        new_alerts = []

        for track in scored_tracks:
            if not track["alert"]:
                continue

            ts       = time.strftime("%Y%m%d_%H%M%S")
            alert_id = str(uuid.uuid4())[:8]

            # Save snapshot
            snapshot_file = f"{SNAPSHOTS_DIR}/alert_{track['track_id']}_{ts}.jpg"
            cv2.imwrite(snapshot_file, frame)

            # Save pre-alert clip (frames from buffer)
            clip_file = f"{CLIPS_DIR}/clip_{track['track_id']}_{ts}.avi"
            self._save_clip(clip_file)

            # Schedule post-alert clip capture (5 more seconds)
            post_clip_file = f"{CLIPS_DIR}/clip_post_{track['track_id']}_{ts}.avi"
            threading.Thread(
                target=self._capture_post_alert_clip,
                args=(post_clip_file,),
                daemon=True
            ).start()

            alert_data = {
                "id":         alert_id,
                "timestamp":  ts,
                "track_id":   track["track_id"],
                "risk_score": track["risk_score"],
                "behaviors":  track["behaviors"],
                "duration":   track["duration"],
                "snapshot":   snapshot_file,
                "clip":       clip_file,
                "post_clip":  post_clip_file
            }

            self.alerts.append(alert_data)
            new_alerts.append(alert_data)

            # Save log
            with open(ALERTS_LOG, "w") as f:
                json.dump(self.alerts, f, indent=2)

            # Send email in background thread (don't block pipeline)
            if self.email_enabled:
                threading.Thread(
                    target=self._send_email,
                    args=(alert_data, snapshot_file),
                    daemon=True
                ).start()

            print(f"🚨 ALERT! Track {track['track_id']} | "
                  f"Risk: {track['risk_score']} | "
                  f"Behaviors: {track['behaviors']}")

        return new_alerts

    def _save_clip(self, clip_file):
        """Save buffered pre-alert frames as video clip"""
        if not self.frame_buffer:
            return

        frames = list(self.frame_buffer)
        h, w   = frames[0].shape[:2]

        out = cv2.VideoWriter(
            clip_file,
            cv2.VideoWriter_fourcc(*"XVID"),
            self.fps, (w, h)
        )
        for f in frames:
            out.write(f)
        out.release()
        print(f"[Alert] Pre-alert clip saved: {clip_file}")

    def _capture_post_alert_clip(self, clip_file):
        """Wait 5 seconds, then save those frames too"""
        post_frames = []
        end_time    = time.time() + self.buffer_seconds

        while time.time() < end_time:
            time.sleep(1 / self.fps)
            if self.frame_buffer:
                post_frames.append(list(self.frame_buffer)[-1].copy())

        if not post_frames:
            return

        h, w = post_frames[0].shape[:2]
        out  = cv2.VideoWriter(
            clip_file,
            cv2.VideoWriter_fourcc(*"XVID"),
            self.fps, (w, h)
        )
        for f in post_frames:
            out.write(f)
        out.release()
        print(f"[Alert] Post-alert clip saved: {clip_file}")

    def _send_email(self, alert_data, snapshot_file):
        """Send email with snapshot attached"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders

            msg             = MIMEMultipart()
            msg["Subject"]  = f"🚨 SentinelAI Alert — Risk Score {alert_data['risk_score']}"
            msg["From"]     = self.sender_email
            msg["To"]       = self.receiver_email

            # Email body
            behaviors = ", ".join(alert_data["behaviors"])
            body = f"""
SentinelAI Threat Detection Alert

Time      : {alert_data['timestamp']}
Person ID : {alert_data['track_id']}
Risk Score: {alert_data['risk_score']} / 100
Behaviors : {behaviors}
Duration  : {alert_data['duration']} seconds in frame

Snapshot attached.
Clip saved at: {alert_data['clip']}

— SentinelAI Automated Alert System
            """
            msg.attach(MIMEText(body, "plain"))

            # Attach snapshot
            if os.path.exists(snapshot_file):
                with open(snapshot_file, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(snapshot_file)}"
                    )
                    msg.attach(part)

            # Send
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.app_password)
            server.send_message(msg)
            server.quit()
            print(f"[Alert] Email sent to {self.receiver_email}")

        except Exception as e:
            print(f"[Alert] Email failed: {e}")
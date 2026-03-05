# run.py - updated with pose
import cv2
import json
from pipeline.capture import VideoCapture
from pipeline.detector import PersonDetector
from pipeline.tracker import PersonTracker
from pipeline.behavior import BehaviorAnalyzer
from pipeline.risk_engine import RiskEngine
from pipeline.alert import AlertHandler
from pipeline.pose import PoseAnalyzer          # ← new
from pipeline.visualizer import draw

VIDEO_SOURCE = "demo/demo.mp4"
SHOW_WINDOW = True
FRAME_SKIP = 2

def load_zones():
    try:
        with open("data/zones.json") as f:
            return json.load(f).get("restricted_zones", [])
    except:
        return []

def main():
    cap = VideoCapture(VIDEO_SOURCE)
    detector = PersonDetector()
    tracker = PersonTracker()
    behavior = BehaviorAnalyzer()
    risk = RiskEngine(threshold=60)
    alert = AlertHandler()
    pose = PoseAnalyzer()                        # ← new
    zones = load_zones()

    frame_count = 0
    last_tracks = []
    last_scored = []

    print("\n✅ SentinelAI pipeline started. Press Q to quit.\n")

    while True:
        ret, frame = cap.read_frame()
        if not ret:
            break

        frame_count += 1

        if frame_count % FRAME_SKIP == 0:
            detections = detector.detect(frame)
            last_tracks = tracker.update(detections, frame)

            # Run pose on same frame                  ← new
            pose_results, frame = pose.analyze(frame, last_tracks)

            # Merge pose into behavior                ← new
            behavior_results = behavior.update_with_pose(
                last_tracks, frame.shape, pose_results
            )

            last_scored = risk.score(behavior_results)
            new_alerts = alert.handle(frame, last_scored)

        vis_frame = draw(frame.copy(), last_tracks, last_scored, zones)

        # Show pose behavior label on each person     ← new
        for track in last_tracks:
            tid = track["track_id"]
            x1, y1 = track["bbox"][0], track["bbox"][1]
            pose_label = pose_results.get(tid, {}).get("pose_behavior", "")
            if pose_label:
                cv2.putText(vis_frame, pose_label, (x1, y1 - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)

        cv2.putText(vis_frame, f"Persons: {len(last_tracks)}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        cv2.putText(vis_frame, f"Alerts: {len(alert.alerts)}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,100,255), 2)

        if SHOW_WINDOW:
            cv2.imshow("SentinelAI - Smart Threat Detection", vis_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n📊 Session ended. Total alerts: {len(alert.alerts)}")

if __name__ == "__main__":
    main()

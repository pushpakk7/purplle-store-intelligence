import cv2
import json
import sqlite3
from datetime import datetime
from ultralytics import YOLO

def setup_database():
    conn = sqlite3.connect("store_intelligence.db")
    cursor = conn.cursor()
    # Updated table architecture to support anomaly metrics natively
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            camera_id TEXT,
            tracking_id INTEGER,
            centroid_x INTEGER,
            centroid_y INTEGER,
            is_anomaly INTEGER,
            anomaly_type TEXT,
            raw_data TEXT
        )
    ''')
    conn.commit()
    return conn

def main():
    print("Setting up database storage engine...")
    db_conn = setup_database()
    db_cursor = db_conn.cursor()

    print("Loading AI Tracking Architecture...")
    model = YOLO("yolov8n.pt")

    video_path = "videos/CAM_2.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Video file not found at {video_path}")
        return

    # Spatial-Temporal tracking dictionary to calculate dwelling thresholds
    # Format: { tracking_id: {"start_frame": frame_idx, "start_x": x, "start_y": y} }
    dwell_tracker = {}
    LOITERING_FRAME_THRESHOLD = 150  # Number of frames to trigger loitering
    SPATIAL_RADIUS = 50              # Pixel movement tolerance bubble

    frame_count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        frame_count += 1
        results = model.track(frame, persist=True, classes=[0], verbose=False)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                timestamp = datetime.utcnow().isoformat() + "Z"

                # --- ANOMALY DETECTION ENGINE LOGIC ---
                is_anomaly = 0
                anomaly_type = "None"

                if track_id not in dwell_tracker:
                    # Initialize tracking track for new individual
                    dwell_tracker[track_id] = {
                        "start_frame": frame_count,
                        "start_x": center_x,
                        "start_y": center_y
                    }
                else:
                    spatial_data = dwell_tracker[track_id]
                    # Calculate spatial displacement from initial location bubble
                    distance = ((center_x - spatial_data["start_x"])**2 + (center_y - spatial_data["start_y"])**2)**0.5
                    
                    if distance < SPATIAL_RADIUS:
                        # Individual is dwelling inside the bubble. Check temporal threshold duration.
                        duration_frames = frame_count - spatial_data["start_frame"]
                        if duration_frames > LOITERING_FRAME_THRESHOLD:
                            is_anomaly = 1
                            anomaly_type = "Loitering / Suspicious Dwell"
                    else:
                        # Individual moved out of bubble, reset temporal spatial baseline anchor
                        dwell_tracker[track_id] = {
                            "start_frame": frame_count,
                            "start_x": center_x,
                            "start_y": center_y
                        }

                event_packet = {
                    "timestamp": timestamp,
                    "camera_id": "CAM_2",
                    "frame_index": frame_count,
                    "event_type": "person_tracking",
                    "is_anomaly": is_anomaly,
                    "anomaly_type": anomaly_type,
                    "data": {
                        "tracking_id": int(track_id),
                        "bounding_box": [int(x1), int(y1), int(x2), int(y2)],
                        "centroid": [center_x, center_y]
                    }
                }
                
                if is_anomaly:
                    print(f"⚠️  ALERT: Anomaly Detected for ID #{track_id} [{anomaly_type}]")

                # Insert directly into updated table ledger schema
                db_cursor.execute('''
                    INSERT INTO tracking_events (timestamp, camera_id, tracking_id, centroid_x, centroid_y, is_anomaly, anomaly_type, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, "CAM_2", int(track_id), center_x, center_y, is_anomaly, anomaly_type, json.dumps(event_packet)))

        db_conn.commit()
        annotated_frame = results[0].plot()
        cv2.imshow("Purplle Store Intelligence System", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    db_conn.close()
    print("AI Core Pipeline closed safely.")

if __name__ == "__main__":
    main()
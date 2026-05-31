from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="Purplle Store Intelligence API Upgrade")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect("store_intelligence.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"status": "Online"}

@app.get("/analytics/footfall")
def get_footfall():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT tracking_id) as total_visitors FROM tracking_events")
    result = cursor.fetchone()
    conn.close()
    return {"total_visitors": result["total_visitors"]}

# --- NEW ENDPOINT: Counts unique cameras currently streaming data ---
@app.get("/analytics/cameras")
def get_active_cameras():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT camera_id) as active_count FROM tracking_events")
    result = cursor.fetchone()
    conn.close()
    return {"active_count": result["active_count"]}

# Fetches all tracked coordinate clusters for heatmap compilation
@app.get("/analytics/heatmap")
def get_heatmap_coords():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Pulling sampled coordinates to keep transmission lightweight
    cursor.execute("SELECT centroid_x, centroid_y FROM tracking_events WHERE id % 2 = 0")
    rows = cursor.fetchall()
    conn.close()
    
    coords = [[row["centroid_x"], row["centroid_y"]] for row in rows]
    return {"coordinates": coords}

# Fetches identified critical anomalies list
@app.get("/analytics/anomalies")
def get_anomalies_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT tracking_id) as alert_count FROM tracking_events WHERE is_anomaly = 1")
    count_res = cursor.fetchone()
    
    cursor.execute("SELECT id, timestamp, tracking_id, anomaly_type FROM tracking_events WHERE is_anomaly = 1 ORDER BY id DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    conn.close()
    
    recent_alerts = []
    for row in recent_rows:
        recent_alerts.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "tracking_id": row["tracking_id"],
            "type": row["anomaly_type"]
        })
        
    return {
        "total_anomalies_count": count_res["alert_count"],
        "recent_alerts": recent_alerts
    }

@app.get("/events/recent")
def get_recent_events(limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tracking_events ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    events = []
    for row in rows:
        events.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "tracking_id": row["tracking_id"],
            "centroid": [row["centroid_x"], row["centroid_y"]],
            "camera_id": row["camera_id"]
        })
    return {"recent_events": events}
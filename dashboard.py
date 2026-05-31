import streamlit as st
import requests
import pandas as pd
import time

# 1. Setup the Look of the Dashboard
st.set_page_config(page_title="Purplle Store Intelligence", layout="wide")
st.title("🛍️ Purplle Store Intelligence Dashboard")
st.markdown("Real-time monitoring and analytics for store operations.")

# 2. Tell the Dashboard where our API is
API_URL = "http://127.0.0.1:8000"

# 3. Create a Refresh Button
if st.button("🔄 Refresh Data"):
    with st.spinner("Fetching real-time data..."):
        time.sleep(0.5)

# 4. Talk to the API (Window 1) to get the data
try:
    # Get Footfall
    footfall_res = requests.get(f"{API_URL}/analytics/footfall").json()
    total_visitors = footfall_res.get("total_visitors", 0)
    
    # Get Recent Events
    events_res = requests.get(f"{API_URL}/events/recent?limit=10").json()
    recent_events = events_res.get("recent_events", [])
    
except Exception as e:
    st.error("Error connecting to API. Is your first PowerShell window still running?")
    total_visitors = 0
    recent_events = []

# 5. Draw the KPI Cards
st.markdown("### 📊 Key Performance Indicators")
col1, col2, col3 = st.columns(3)

col1.metric(label="Total Unique Footfall", value=total_visitors, delta="Live")
col2.metric(label="Active Cameras", value="1 / 5", delta="Normal")
col3.metric(label="System Status", value="Online", delta="Stable", delta_color="normal")

st.markdown("---")

# 6. Draw the Data Table
st.markdown("### 🕒 Live Tracking Feed")
if recent_events:
    df = pd.DataFrame(recent_events)
    df = df.rename(columns={
        "id": "Database ID",
        "timestamp": "Time Detected",
        "tracking_id": "Person ID",
        "centroid": "Location (X, Y)"
    })
    st.dataframe(df, width="stretch", hide_index=True)
else:
    st.info("No tracking events found yet.")
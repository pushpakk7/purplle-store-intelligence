\# 🛍️ Purplle Store Intelligence System



!\[System Status](https://img.shields.io/badge/Status-Production\_Ready-success) 

!\[Version](https://img.shields.io/badge/Version-1.0.0-blue)

!\[Architecture](https://img.shields.io/badge/Architecture-Edge\_Compute-purple)



An end-to-end, edge-computing computer vision platform designed to provide retail store managers with real-time, actionable insights into foot traffic, customer dwelling, and security anomalies.



\---



\## 🎯 Problem Statement

Physical retail spaces generate massive amounts of visual data through CCTV, but store managers lack real-time, automated tools to translate this video into operational metrics. Traditional cloud-based video analytics suffer from high bandwidth costs, latency, and privacy concerns. \*\*The Purplle Store Intelligence System\*\* solves this by shifting the AI inference directly to the edge, processing video streams locally, and transmitting only lightweight JSON metadata to a centralized dashboard.



\---



\## 🏗️ Architecture

The system is built on a highly decoupled, asynchronous architecture to ensure the heavy AI compute pipeline does not block the web server or frontend rendering.



1\. \*\*Vision Engine (`vision\_pipeline.py`):\*\* Ingests raw video, runs YOLOv8 object detection, assigns unique tracking IDs, and calculates spatial-temporal logic (dwelling/loitering).

2\. \*\*Local Edge Ledger (`store\_intelligence.db`):\*\* An embedded SQLite database acts as the high-speed local memory buffer, logging event payloads instantly.

3\. \*\*RESTful API (`api\_server.py`):\*\* A FastAPI server exposes the ledger data securely via standard HTTP endpoints.

4\. \*\*Operations Terminal (`index.html`):\*\* A zero-dependency, vanilla HTML/JS frontend styled with Tailwind CSS polls the API to render dynamic metrics and HTML5 Canvas heatmaps.



\---



\## 💻 Tech Stack

\* \*\*AI \& Computer Vision:\*\* Python, OpenCV, Ultralytics YOLOv8n

\* \*\*Backend API:\*\* FastAPI, Uvicorn, Python `sqlite3`

\* \*\*Database:\*\* SQLite (Embedded Edge SQL)

\* \*\*Frontend:\*\* HTML5, Vanilla JavaScript, Tailwind CSS (via CDN)



\---



\## ✨ Core Features

\- \[x] \*\*Person Detection:\*\* Isolates humans from CCTV feeds in real-time.

\- \[x] \*\*Multi-Object Tracking:\*\* Maintains persistent identity assignment across frames.

\- \[x] \*\*Customer Counting:\*\* Generates accurate, unique footfall metrics.

\- \[x] \*\*Zone Heatmaps:\*\* Dynamic density rendering to identify high-traffic store areas.

\- \[x] \*\*Suspicious/Anomaly Detection:\*\* Temporal-spatial algorithms flag loitering behavior.

\- \[x] \*\*Real-Time Event Generation:\*\* Logs exact timestamps and coordinate vectors.

\- \[x] \*\*Decoupled Dashboard:\*\* Real-time analytics polling without page refreshes.

\- \[x] \*\*REST APIs:\*\* Extensible endpoints for future integration (e.g., POS systems).

\- \[x] \*\*Database Storage:\*\* Permanent, queryable historical ledger.



\---



\## 🔌 API Documentation

The FastAPI backend serves on `http://127.0.0.1:8000`.



| Endpoint | Method | Description | Response Type |

| :--- | :--- | :--- | :--- |

| `/analytics/footfall` | `GET` | Returns total unique visitors tracked. | JSON (`total\_visitors`) |

| `/analytics/cameras` | `GET` | Returns count of active camera streams. | JSON (`active\_count`) |

| `/analytics/heatmap` | `GET` | Returns sampled spatial \[X, Y] vectors. | JSON Array (`coordinates`) |

| `/analytics/anomalies`| `GET` | Returns security flags and critical alerts. | JSON (`recent\_alerts`) |

| `/events/recent` | `GET` | Returns raw, paginated tracking ingestion logs.| JSON (`recent\_events`) |



\---



\## ⚙️ Setup Instructions



\*\*1. Clone and Environment Setup\*\*

```bash

git clone \[https://github.com/yourusername/purplle-store-intelligence.git](https://github.com/yourusername/purplle-store-intelligence.git)

cd purplle-store-intelligence

python -m venv env

env\\Scripts\\activate  # Windows

pip install ultralytics opencv-python fastapi uvicorn





**2. Start the API Server (Terminal 1)**
```bash
uvicorn api_server:app --reload


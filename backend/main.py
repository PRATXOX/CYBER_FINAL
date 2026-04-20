from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import ml_engine

app = FastAPI(title="Traffic Congestion Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "traffic_data.json")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/traffic")
def get_traffic_data():
    if not os.path.exists(DATA_FILE):
        return {"error": "Data not found. Is the mock data generator running?"}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/predictions")
def get_predictions():
    if not os.path.exists(DATA_FILE):
        return {"error": "Data not found. Is the mock data generator running?"}
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        
        # Process through the Deep Learning Engine pipeline
        predictions = ml_engine.process_pipeline(data)
        return predictions
    except Exception as e:
        return {"error": str(e)}

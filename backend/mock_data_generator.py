import json
import os
import random
import time
from datetime import datetime

# Path for the data file
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "traffic_data.json")

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Sample locations
LOCATIONS = [
    {"name": "Connaught Place", "lat": 28.6304, "lon": 77.2177},
    {"name": "Gurugram Expressway", "lat": 28.4595, "lon": 77.0266},
    {"name": "Noida Sector 18", "lat": 28.5708, "lon": 77.3271},
    {"name": "Ashram Chowk", "lat": 28.5733, "lon": 77.2595},
]

def generate_mock_data():
    timestamp = datetime.now().isoformat()
    traffic_flow = []
    cctv_density = []

    for loc in LOCATIONS:
        # Simulate traffic flow (speeds in km/h)
        speed = random.uniform(5.0, 80.0)
        flow_status = "Free" if speed > 50 else ("Moderate" if speed > 20 else "Congested")
        
        traffic_flow.append({
            "location_name": loc["name"],
            "coordinates": {"lat": loc["lat"], "lon": loc["lon"]},
            "speed_kmh": round(speed, 2),
            "status": flow_status
        })

        # Simulate CCTV vehicle density
        count = random.randint(0, 150)
        density_level = "High" if count > 100 else ("Medium" if count > 50 else "Low")
        
        cctv_density.append({
            "location_name": loc["name"],
            "coordinates": {"lat": loc["lat"], "lon": loc["lon"]},
            "vehicle_count": count,
            "density": density_level
        })

    return {
        "timestamp": timestamp,
        "traffic_flow": traffic_flow,
        "cctv_density": cctv_density
    }

def main():
    print(f"Starting mock data generator. Writing to {DATA_FILE}")
    print("Updating every 10 seconds...")
    
    while True:
        try:
            data = generate_mock_data()
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"[{data['timestamp']}] Data updated successfully.")
        except Exception as e:
            print(f"Error generating data: {e}")
        
        # Wait for 10 seconds
        time.sleep(10)

if __name__ == "__main__":
    # Generate immediately on start
    data = generate_mock_data()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Initial data generated at {DATA_FILE}")
    main()

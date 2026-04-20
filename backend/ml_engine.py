import torch
import torch.nn as nn
import random

class CongestionLSTM(nn.Module):
    """
    LSTM model that takes historical flow and density data to predict 
    the probability of a 'Standstill Jam' (Level 5 congestion) 15-45 mins into the future.
    """
    def __init__(self, input_size=2, hidden_size=64, num_layers=2):
        super(CongestionLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        # Fully connected layer to output probability (0 to 1)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        out = self.sigmoid(out)
        return out

# Initialize a global model instance (with dummy weights for now)
# In a real scenario, we would load pre-trained weights here
model = CongestionLSTM(input_size=2)
model.eval()

def run_lstm_prediction(flow_speed, cctv_density):
    """
    Runs a mock forward pass using the LSTM model.
    Takes current flow_speed and cctv_density as a 1-step sequence.
    """
    # Normalize inputs somewhat arbitrarily for the dummy pass
    normalized_speed = flow_speed / 100.0
    normalized_density = cctv_density / 150.0
    
    # Create tensor: batch_size=1, seq_len=1, features=2
    input_tensor = torch.tensor([[[normalized_speed, normalized_density]]], dtype=torch.float32)
    
    with torch.no_grad():
        prediction = model(input_tensor)
        
    return prediction.item()

def yolo_cctv_extraction(cctv_data):
    """
    Simulates YOLO object detection on CCTV data.
    Detects the 'cause' and the 'exact density of vehicles'.
    """
    visual_results = []
    causes = ["clear", "stalled vehicle", "fender bender", "heavy traffic"]
    
    thumbnail_urls = [
        "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?q=80&w=400&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?q=80&w=400&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1566208573887-195b05777a83?q=80&w=400&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1506526131494-b203a3d2427a?q=80&w=400&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1543324675-7b56f8f53a5f?q=80&w=400&auto=format&fit=crop"
    ]
    
    for idx, item in enumerate(cctv_data):
        # Simulate exact vehicle count based on the mock data
        base_count = item.get("vehicle_count", 0)
        # Add slight variation to simulate "exact detection"
        exact_density = max(0, base_count + random.randint(-5, 5))
        
        # Determine cause based on density and randomness
        if exact_density > 100:
            cause = random.choice(["fender bender", "heavy traffic", "heavy traffic"])
        elif exact_density > 50:
            cause = random.choice(["stalled vehicle", "heavy traffic", "clear"])
        else:
            cause = random.choice(["clear", "clear", "stalled vehicle"])
            
        visual_results.append({
            "location_name": item["location_name"],
            "coordinates": item["coordinates"],
            "exact_density": exact_density,
            "cause": cause,
            "thumbnail_url": thumbnail_urls[idx % len(thumbnail_urls)]
        })
        
    return visual_results

def cross_modal_correlation(flow_pred_prob, visual_item):
    """
    Validates the flow feed (LSTM prediction) against the visual feed (YOLO extraction)
    to eliminate false positives.
    """
    # If LSTM predicts high jam probability but visual says clear and density is low -> false positive
    visual_cause = visual_item["cause"]
    visual_density = visual_item["exact_density"]
    
    validated_prob = flow_pred_prob
    
    if flow_pred_prob > 0.7:
        if visual_cause == "clear" and visual_density < 30:
            # Downgrade probability due to lack of visual evidence
            validated_prob = flow_pred_prob * 0.3
        elif visual_cause in ["fender bender", "stalled vehicle"]:
            # Upgrade probability due to confirming visual evidence
            validated_prob = min(1.0, flow_pred_prob * 1.2)
            
    return round(validated_prob, 4)

def process_pipeline(traffic_data):
    """
    Executes the full ML pipeline and returns a structured JSON for an Interactive GIS Dashboard.
    """
    traffic_flow = traffic_data.get("traffic_flow", [])
    cctv_data = traffic_data.get("cctv_density", [])
    
    # 1. Visual Feed (YOLO) Extraction
    visual_results = yolo_cctv_extraction(cctv_data)
    
    # Map visual results by location for easy lookup
    visual_map = {item["location_name"]: item for item in visual_results}
    
    predicted_hotspots = []
    
    for flow_item in traffic_flow:
        location = flow_item["location_name"]
        speed = flow_item.get("speed_kmh", 50)
        
        visual_item = visual_map.get(location)
        if not visual_item:
            continue
            
        cctv_density = visual_item["exact_density"]
        
        # 2. Prediction Engine (LSTM)
        raw_prob = run_lstm_prediction(speed, cctv_density)
        
        # 3. Cross-Modal Correlation
        validated_prob = cross_modal_correlation(raw_prob, visual_item)
        
        # Determine if it's a predicted hotspot (Level 5 jam threshold e.g. > 0.6)
        is_hotspot = validated_prob > 0.6
        
        predicted_hotspots.append({
            "location_name": location,
            "coordinates": flow_item["coordinates"],
            "prediction_15_45_min": {
                "jam_probability": validated_prob,
                "is_level_5_hotspot": is_hotspot
            },
            "visual_validation": {
                "cause": visual_item["cause"],
                "exact_density": visual_item["exact_density"],
                "thumbnail_url": visual_item["thumbnail_url"]
            }
        })
        
    return {
        "timestamp": traffic_data.get("timestamp"),
        "gis_dashboard_data": {
            "predicted_hotspots": predicted_hotspots
        }
    }

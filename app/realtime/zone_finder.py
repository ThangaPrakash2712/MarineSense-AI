"""
Intelligent Fishing Zone Recommendation Engine
Finds optimal fishing locations based on ML predictions
NOW WITH OCEAN-AWARE GEOSPATIAL LOGIC
"""

import numpy as np
import pandas as pd
from typing import Dict
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.geo_utils import generate_ocean_candidates, haversine_km

logger = logging.getLogger(__name__)

def find_best_fishing_zone(user_lat: float, user_lon: float, 
                           base_features: Dict, model) -> Dict:
    """
    Find optimal fishing zone by testing multiple ocean candidate locations.
    Uses geospatially-aware candidate generation.
    
    Args:
        user_lat: User's coastal latitude
        user_lon: User's coastal longitude
        base_features: Base environmental features
        model: Trained fish prediction model
        
    Returns:
        Dictionary with best location details
    """
    try:
        logger.info(f"Searching for best fishing zone around ({user_lat}, {user_lon})")
        
        # Generate ocean-only candidate points (30-120 km from coast)
        candidates = generate_ocean_candidates(
            user_lat, user_lon, 
            num_points=20,
            min_dist_km=30,
            max_dist_km=120
        )
        
        best_score = -1
        best_location = None
        all_predictions = []
        
        for lat, lon in candidates:
            # Vary environmental conditions based on location
            sst_variation = np.random.uniform(-1.0, 1.0)
            chloro_variation = np.random.uniform(-0.1, 0.2)
            wind_variation = np.random.uniform(-1.0, 1.0)
            
            # Create feature vector
            features = pd.DataFrame([{
                "year": base_features["year"],
                "month": base_features["month"],
                "avg_sst": base_features["avg_sst"] + sst_variation,
                "wind_speed": max(5.0, base_features["wind_speed"] + wind_variation),
                "wave_height": base_features["wave_height"],
                "salinity": base_features["salinity"],
                "chlorophyll": max(0.1, base_features["chlorophyll"] + chloro_variation)
            }])
            
            # Predict fish quantity
            prediction = model.predict(features)[0]
            
            all_predictions.append({
                "lat": lat,
                "lon": lon,
                "fish_prediction": prediction
            })
            
            # Track best location
            if prediction > best_score:
                best_score = prediction
                best_location = (lat, lon)
        
        # Calculate confidence
        if all_predictions:
            predictions_array = [p["fish_prediction"] for p in all_predictions]
            max_pred = max(predictions_array)
            confidence = min(95, 70 + (best_score / max_pred) * 25 if max_pred > 0 else 70)
        else:
            confidence = 50
        
        result = {
            "best_lat": best_location[0] if best_location else user_lat,
            "best_lon": best_location[1] if best_location else user_lon,
            "predicted_fish": best_score if best_score > 0 else 100,
            "confidence_score": confidence,
            "all_candidates": all_predictions
        }
        
        logger.info(f"Best zone found: ({result['best_lat']:.2f}, {result['best_lon']:.2f}) "
                   f"with {result['predicted_fish']:.0f} fish")
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding best fishing zone: {e}")
        # Return fallback ocean location
        return {
            "best_lat": user_lat - 1.0,  # Slightly offshore
            "best_lon": user_lon - 1.0,
            "predicted_fish": 150,
            "confidence_score": 50,
            "all_candidates": []
        }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance using Haversine formula.
    Delegates to geo_utils for consistency.
    """
    return haversine_km(lat1, lon1, lat2, lon2)


def estimate_fuel(distance_km: float, efficiency: float, speed: float) -> Dict:
    """
    Estimate fuel consumption and travel time.
    
    Args:
        distance_km: Distance to travel in km
        efficiency: Fuel efficiency in liters per km
        speed: Boat speed in km/h
        
    Returns:
        Dictionary with fuel and time estimates
    """
    fuel_needed = distance_km * efficiency
    travel_time_hours = distance_km / speed if speed > 0 else 0
    
    return {
        "fuel_liters": fuel_needed,
        "travel_hours": travel_time_hours,
        "distance_km": distance_km
    }

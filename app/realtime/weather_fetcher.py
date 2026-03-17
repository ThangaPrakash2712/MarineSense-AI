"""
Real-Time Marine Weather Data Fetcher
Uses Open-Meteo Marine API (free, no API key required)
"""

import requests
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_realtime_marine_weather(lat: float, lon: float, timeout: int = 10) -> Optional[Dict]:
    """
    Fetch real-time marine weather data from Open-Meteo Marine API.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with marine parameters or None if failed
    """
    try:
        # Open-Meteo Marine API (free, no key needed)
        marine_url = "https://marine-api.open-meteo.com/v1/marine"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "wave_height,wave_period,wind_wave_height",
            "timezone": "auto"
        }
        
        logger.info(f"Fetching marine data for lat={lat}, lon={lon}")
        marine_response = requests.get(marine_url, params=params, timeout=timeout)
        marine_response.raise_for_status()
        marine_data = marine_response.json()
        
        # Open-Meteo Weather API for additional parameters
        weather_url = "https://api.open-meteo.com/v1/forecast"
        
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m",
            "timezone": "auto"
        }
        
        weather_response = requests.get(weather_url, params=weather_params, timeout=timeout)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Extract and structure data
        current_marine = marine_data.get("current", {})
        current_weather = weather_data.get("current", {})
        
        # Build feature dictionary
        features = {
            "avg_sst": current_weather.get("temperature_2m", 27.0),  # Approximate SST from air temp
            "wind_speed": current_weather.get("wind_speed_10m", 12.0),
            "wave_height": current_marine.get("wave_height", 1.5),
            "salinity": 34.5,  # Fallback - not available in free API
            "chlorophyll": 0.8,  # Fallback - not available in free API
            "source": "realtime",
            "timestamp": current_weather.get("time", "unknown")
        }
        
        logger.info(f"Successfully fetched real-time data: {features}")
        return features
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching marine data for lat={lat}, lon={lon}")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching marine data: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error fetching marine data: {e}")
        return None


def build_prediction_features(source_mode: str, manual_inputs: Dict, 
                              realtime_data: Optional[Dict] = None) -> Dict:
    """
    Build feature dictionary for model prediction based on data source.
    
    Args:
        source_mode: "realtime" or "manual"
        manual_inputs: Dictionary of manual input values
        realtime_data: Dictionary of real-time fetched data (optional)
        
    Returns:
        Dictionary with all required features for prediction
    """
    if source_mode == "realtime" and realtime_data is not None:
        # Use real-time data, fill missing with manual fallbacks
        features = {
            "year": manual_inputs.get("year", 2024),
            "month": manual_inputs.get("month", 6),
            "avg_sst": realtime_data.get("avg_sst", manual_inputs.get("avg_sst", 27.0)),
            "wind_speed": realtime_data.get("wind_speed", manual_inputs.get("wind_speed", 12.0)),
            "wave_height": realtime_data.get("wave_height", manual_inputs.get("wave_height", 1.5)),
            "salinity": realtime_data.get("salinity", manual_inputs.get("salinity", 34.5)),
            "chlorophyll": realtime_data.get("chlorophyll", manual_inputs.get("chlorophyll", 0.8)),
            "source": "realtime",
            "timestamp": realtime_data.get("timestamp", "unknown")
        }
    else:
        # Use manual inputs
        features = {
            "year": manual_inputs.get("year", 2024),
            "month": manual_inputs.get("month", 6),
            "avg_sst": manual_inputs.get("avg_sst", 27.0),
            "wind_speed": manual_inputs.get("wind_speed", 12.0),
            "wave_height": manual_inputs.get("wave_height", 1.5),
            "salinity": manual_inputs.get("salinity", 34.5),
            "chlorophyll": manual_inputs.get("chlorophyll", 0.8),
            "source": "manual",
            "timestamp": "manual"
        }
    
    return features

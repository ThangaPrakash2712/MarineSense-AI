"""
Real-Time Marine Intelligence Module
"""

from .weather_fetcher import fetch_realtime_marine_weather, build_prediction_features
from .zone_finder import find_best_fishing_zone, calculate_distance, estimate_fuel
from .advisory import generate_marine_advisory

__all__ = [
    'fetch_realtime_marine_weather',
    'build_prediction_features',
    'find_best_fishing_zone',
    'calculate_distance',
    'estimate_fuel',
    'generate_marine_advisory'
]

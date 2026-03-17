"""
Utility modules for MarineSense AI
"""

from .geo_utils import (
    haversine_km,
    snap_to_nearest_coast,
    is_ocean_point,
    generate_ocean_candidates
)

__all__ = [
    'haversine_km',
    'snap_to_nearest_coast',
    'is_ocean_point',
    'generate_ocean_candidates'
]

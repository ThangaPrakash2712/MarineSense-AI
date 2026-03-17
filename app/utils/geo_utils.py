"""
Geospatial Utilities for MarineSense AI
Handles coastline snapping, distance calculations, and ocean validation
"""

import numpy as np
from typing import Tuple

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in km
    
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c


def snap_to_nearest_coast(lat: float, lon: float) -> Tuple[float, float]:
    """
    Snap inland/deep-ocean point to nearest coastline.
    Uses heuristic approach for Indian Ocean region.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        (snapped_lat, snapped_lon) tuple
    """
    # Indian Ocean coastal boundaries (approximate)
    # West coast of India, Sri Lanka, Southeast Asia
    
    coastal_points = [
        # West coast India
        (8.5, 76.9),   # Kerala coast
        (10.0, 76.2),  # Kerala
        (11.0, 75.8),  # Karnataka
        (12.9, 74.8),  # Goa
        (15.5, 73.8),  # Maharashtra
        (19.0, 72.8),  # Mumbai
        # East coast India
        (13.0, 80.3),  # Chennai
        (17.7, 83.3),  # Visakhapatnam
        (20.3, 85.8),  # Odisha
        # Sri Lanka
        (6.9, 79.9),   # Colombo
        (9.7, 80.0),   # Trincomalee
        # Southeast Asia
        (3.1, 101.7),  # Malaysia
        (1.3, 103.8),  # Singapore
        # Arabian Sea
        (23.0, 69.0),  # Gujarat
        (24.8, 67.0),  # Pakistan coast
    ]
    
    # Find nearest coastal point
    min_dist = float('inf')
    nearest_point = (lat, lon)
    
    for coast_lat, coast_lon in coastal_points:
        dist = haversine_km(lat, lon, coast_lat, coast_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_point = (coast_lat, coast_lon)
    
    # If point is very close to coast (<5km), use original
    if min_dist < 5:
        return lat, lon
    
    # If point is far inland (>100km), snap to nearest coast
    if min_dist > 100:
        return nearest_point
    
    # For moderate distances, interpolate toward coast
    # Move 80% toward coast to ensure shore proximity
    interp_factor = 0.8
    snapped_lat = lat + interp_factor * (nearest_point[0] - lat)
    snapped_lon = lon + interp_factor * (nearest_point[1] - lon)
    
    return snapped_lat, snapped_lon


def is_ocean_point(lat: float, lon: float) -> bool:
    """
    Check if point is in ocean (simple heuristic for Indian Ocean).
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if likely in ocean, False otherwise
    """
    # Indian Ocean bounds
    if not (0 <= lat <= 30 and 55 <= lon <= 100):
        return False
    
    # Exclude major land masses (rough approximation)
    # India mainland
    if 8 <= lat <= 35 and 68 <= lon <= 88:
        # Check if in coastal waters (simplified)
        if lon < 72 or lon > 85:  # West or East coast waters
            return True
        return False
    
    # Sri Lanka
    if 6 <= lat <= 10 and 79 <= lon <= 82:
        return False
    
    # Southeast Asia mainland
    if lat < 7 and lon > 95:
        return False
    
    # Default: assume ocean
    return True


def generate_ocean_candidates(center_lat: float, center_lon: float, 
                              num_points: int = 20,
                              min_dist_km: float = 30,
                              max_dist_km: float = 120) -> list:
    """
    Generate candidate fishing locations in ocean waters.
    
    Args:
        center_lat: Center latitude (coastal point)
        center_lon: Center longitude (coastal point)
        num_points: Number of candidates to generate
        min_dist_km: Minimum distance from coast
        max_dist_km: Maximum distance from coast
        
    Returns:
        List of (lat, lon) tuples in ocean
    """
    candidates = []
    km_to_deg = 1 / 111.0
    
    attempts = 0
    max_attempts = num_points * 5  # Allow multiple attempts
    
    while len(candidates) < num_points and attempts < max_attempts:
        attempts += 1
        
        # Random distance and angle
        distance_km = np.random.uniform(min_dist_km, max_dist_km)
        angle = np.random.uniform(0, 2 * np.pi)
        
        # Calculate offset
        distance_deg = distance_km * km_to_deg
        lat_offset = distance_deg * np.cos(angle)
        lon_offset = distance_deg * np.sin(angle) / np.cos(np.radians(center_lat))
        
        candidate_lat = center_lat + lat_offset
        candidate_lon = center_lon + lon_offset
        
        # Validate: must be in ocean and within bounds
        if (-90 <= candidate_lat <= 90 and 
            -180 <= candidate_lon <= 180 and
            is_ocean_point(candidate_lat, candidate_lon)):
            candidates.append((candidate_lat, candidate_lon))
    
    # If not enough ocean points found, generate some guaranteed ocean points
    if len(candidates) < num_points:
        # Add points in known ocean areas
        for _ in range(num_points - len(candidates)):
            # Arabian Sea / Bay of Bengal
            if center_lon < 80:  # West coast - Arabian Sea
                ocean_lat = center_lat + np.random.uniform(-2, 2)
                ocean_lon = center_lon - np.random.uniform(2, 5)  # West into ocean
            else:  # East coast - Bay of Bengal
                ocean_lat = center_lat + np.random.uniform(-2, 2)
                ocean_lon = center_lon + np.random.uniform(2, 5)  # East into ocean
            
            if -90 <= ocean_lat <= 90 and -180 <= ocean_lon <= 180:
                candidates.append((ocean_lat, ocean_lon))
    
    return candidates[:num_points]

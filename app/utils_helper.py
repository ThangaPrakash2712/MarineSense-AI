"""
MarineSense AI - Helper Utilities Module
Contains reusable functions for feature engineering, visualization, and analysis
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def engineer_features(df):
    """
    Apply feature engineering transformations to input data.
    
    Features added:
    - SST anomaly: Deviation from mean temperature
    - Wind-wave interaction: Product of wind speed and wave height
    - Seasonal encoding: Sin/cos transformation of month
    
    Args:
        df (pd.DataFrame): Input dataframe with marine parameters
        
    Returns:
        pd.DataFrame: Enhanced dataframe with engineered features
    """
    df_enhanced = df.copy()
    
    # SST Anomaly (deviation from mean)
    if 'avg_sst' in df_enhanced.columns:
        sst_mean = 27.5  # Approximate mean for Indian Ocean
        df_enhanced['sst_anomaly'] = df_enhanced['avg_sst'] - sst_mean
    
    # Wind-Wave Interaction
    if 'wind_speed' in df_enhanced.columns and 'wave_height' in df_enhanced.columns:
        df_enhanced['wind_wave_interaction'] = df_enhanced['wind_speed'] * df_enhanced['wave_height']
    
    # Seasonal Encoding (sin/cos transformation)
    if 'month' in df_enhanced.columns:
        df_enhanced['month_sin'] = np.sin(2 * np.pi * df_enhanced['month'] / 12)
        df_enhanced['month_cos'] = np.cos(2 * np.pi * df_enhanced['month'] / 12)
    
    return df_enhanced


def fishing_advisory(risk_label):
    """
    Convert weather risk label to fishing recommendation.
    
    Args:
        risk_label (str): Weather risk level ('Safe', 'Moderate', 'Dangerous')
        
    Returns:
        tuple: (recommendation_text, color)
    """
    advisory_map = {
        "Safe": ("Safe to Go Fishing", "green"),
        "Moderate": ("Go With Caution", "orange"),
        "Dangerous": ("Not Safe for Fishing", "red")
    }
    return advisory_map.get(risk_label, ("Unknown Risk", "gray"))


def classify_fishing_zone(fish_quantity):
    """
    Classify fishing zone based on predicted fish quantity.
    
    Thresholds:
    - High: > 250 fish
    - Medium: 150-250 fish
    - Low: < 150 fish
    
    Args:
        fish_quantity (float): Predicted fish quantity
        
    Returns:
        tuple: (zone_label, color)
    """
    if fish_quantity > 250:
        return "High Potential", "red"
    elif fish_quantity >= 150:
        return "Medium Potential", "yellow"
    else:
        return "Low Potential", "green"


def create_hotspot_map(lat, lon, fish_quantity):
    """
    Create interactive fishing zone map using Plotly ScatterGeo.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        fish_quantity (float): Predicted fish quantity
        
    Returns:
        plotly.graph_objects.Figure: Interactive map figure
    """
    zone_label, zone_color = classify_fishing_zone(fish_quantity)
    
    # Color mapping for plotly
    color_map = {"red": "#FF0000", "yellow": "#FFD700", "green": "#00FF00"}
    marker_color = color_map.get(zone_color, "#0000FF")
    
    fig = go.Figure(data=go.Scattergeo(
        lon=[lon],
        lat=[lat],
        mode='markers+text',
        marker=dict(
            size=20,
            color=marker_color,
            line=dict(width=2, color='white')
        ),
        text=[f"{zone_label}<br>{fish_quantity:.0f} fish"],
        textposition="top center",
        textfont=dict(size=12, color='black', family='Arial Black')
    ))
    
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="lightgray",
        coastlinecolor="black",
        center=dict(lat=lat, lon=lon),
        projection_scale=3
    )
    
    fig.update_layout(
        title=dict(
            text=f"Potential Fishing Zone: {zone_label}",
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f77b4')
        ),
        height=400,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig


def validate_coordinates(lat, lon):
    """
    Validate latitude and longitude coordinates.
    
    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not (-90 <= lat <= 90):
        return False, "Latitude must be between -90 and 90"
    
    if not (-180 <= lon <= 180):
        return False, "Longitude must be between -180 and 180"
    
    return True, ""


def calculate_risk_score(risk_label):
    """
    Convert risk label to numerical score for gauge visualization.
    
    Args:
        risk_label (str): Risk level label
        
    Returns:
        int: Risk score (0-100)
    """
    risk_mapping = {
        "Safe": 20,
        "Moderate": 60,
        "Dangerous": 90
    }
    return risk_mapping.get(risk_label, 50)


# ===============================
# Future-Ready Integration Hooks
# ===============================

def sonar_fish_detection(image):
    """
    TODO: Integrate YOLOv7 sonar-based fish detection.
    
    This function will:
    1. Load the YOLOv7 model from sonar_detection/
    2. Process sonar images
    3. Detect and count fish
    4. Return species classification
    
    Args:
        image: Sonar image (numpy array or file path)
        
    Returns:
        dict: Detection results with count and species
    """
    # Placeholder for future implementation
    raise NotImplementedError("Sonar detection integration pending")


def fetch_realtime_weather_api(lat, lon):
    """
    TODO: Integrate real-time weather API.
    
    Suggested APIs:
    - OpenWeatherMap Marine API
    - NOAA Marine Weather
    - Windy API
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        dict: Real-time weather data
    """
    # Placeholder for future implementation
    raise NotImplementedError("Real-time weather API integration pending")


def model_retraining_pipeline(new_data_path):
    """
    TODO: Implement automated model retraining pipeline.
    
    This function will:
    1. Load new training data
    2. Validate data quality
    3. Retrain models with updated data
    4. Evaluate performance metrics
    5. Save updated models if performance improves
    
    Args:
        new_data_path (str): Path to new training data
        
    Returns:
        dict: Retraining results and metrics
    """
    # Placeholder for future MLOps pipeline
    raise NotImplementedError("Model retraining pipeline pending")


def export_prediction_report(predictions, filename="report.pdf"):
    """
    TODO: Export predictions as PDF report.
    
    Args:
        predictions (dict): Prediction results
        filename (str): Output filename
    """
    # Placeholder for future implementation
    raise NotImplementedError("Report export feature pending")

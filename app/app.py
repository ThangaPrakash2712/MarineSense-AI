import streamlit as st
import streamlit.components.v1 as components
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from datetime import datetime
import time
import sys

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import real-time modules
from realtime import (
    fetch_realtime_marine_weather,
    build_prediction_features,
    find_best_fishing_zone,
    calculate_distance,
    estimate_fuel,
    generate_marine_advisory
)

# Import geospatial utilities
from utils.geo_utils import snap_to_nearest_coast, haversine_km

st.set_page_config(page_title="MarineSense AI - Live", layout="wide", initial_sidebar_state="expanded")

# Premium Theme & Styling
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); background-attachment: fixed; }
    .stApp { background: linear-gradient(to bottom, rgba(11,61,145,0.05), rgba(0,168,232,0.05)); }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #0B3D91; }
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,248,255,0.9));
        backdrop-filter: blur(10px); border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 4px solid;
        transition: transform 0.3s, box-shadow 0.3s; margin: 10px 0;
    }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
    .hero-banner {
        background: linear-gradient(135deg, #0B3D91, #00A8E8); color: white;
        padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); margin-bottom: 30px;
    }
    .status-badge {
        display: inline-block; padding: 8px 20px; border-radius: 20px;
        font-weight: bold; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    .live-indicator {
        display: inline-block; width: 12px; height: 12px; background: #2ECC71;
        border-radius: 50%; animation: blink 1.5s infinite; margin-right: 8px;
    }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .insight-box {
        background: linear-gradient(135deg, #667eea, #764ba2); color: white;
        padding: 20px; border-radius: 12px; box-shadow: 0 6px 20px rgba(102,126,234,0.4); margin: 20px 0;
    }
    h1, h2, h3 { color: #0B3D91; }
    .stButton>button {
        background: linear-gradient(135deg, #00A8E8, #0B3D91); color: white;
        border-radius: 8px; border: none; padding: 10px 25px; font-weight: 600; transition: all 0.3s;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,168,232,0.4); }
    
    /* Chart container styling */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(240,248,255,0.92));
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent.parent
fish_model_path = BASE_DIR / "models" / "fish_prediction_model.pkl"
weather_model_path = BASE_DIR / "models" / "weather_risk_model.pkl"
sst_path = BASE_DIR / "data" / "processed" / "sst_indian_ocean.csv"

@st.cache_resource
def load_models():
    """Load ML models with caching"""
    with st.spinner("🔄 Loading AI models..."):
        try:
            fish_model = joblib.load(fish_model_path)
            weather_model = joblib.load(weather_model_path)
            return fish_model, weather_model
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return None, None

@st.cache_data
def load_sst():
    """Load SST data with caching"""
    try:
        return pd.read_csv(sst_path)
    except Exception as e:
        st.error(f"Error loading SST data: {e}")
        return pd.DataFrame()

fish_model, weather_model = load_models()
sst_data = load_sst()

def classify_fishing_zone(fish_quantity):
    """Classify fishing zone by fish quantity"""
    if fish_quantity > 250:
        return "High Potential", "red"
    elif fish_quantity >= 150:
        return "Medium Potential", "yellow"
    else:
        return "Low Potential", "green"

def create_route_map(user_lat, user_lon, dest_lat, dest_lon, fish_pred, safety_status, data_source="Manual"):
    """Create premium route map with coastal-aware routing"""
    
    # FIX 1: Snap user location to nearest coast
    shore_lat, shore_lon = snap_to_nearest_coast(user_lat, user_lon)
    
    # Calculate actual distance from shore to fishing zone
    actual_distance = haversine_km(shore_lat, shore_lon, dest_lat, dest_lon)
    
    # Create route line from shore to fishing zone
    route_lats = [shore_lat, dest_lat]
    route_lons = [shore_lon, dest_lon]
    
    fig = go.Figure()
    
    # Route line
    fig.add_trace(go.Scattergeo(
        lon=route_lons,
        lat=route_lats,
        mode='lines',
        line=dict(width=3, color='#00A8E8', dash='dash'),
        name='Sea Route',
        hoverinfo='skip'
    ))
    
    # Departure point (shore)
    fig.add_trace(go.Scattergeo(
        lon=[shore_lon],
        lat=[shore_lat],
        mode='markers+text',
        marker=dict(size=15, color='#0B3D91', symbol='circle', 
                   line=dict(width=2, color='white')),
        text=['Departure'],
        textposition='top center',
        name='Departure (Shore)',
        hovertemplate=f"<b>Departure Point (Shore)</b><br>" +
                     f"Lat: {shore_lat:.2f}<br>Lon: {shore_lon:.2f}<br>" +
                     f"Distance: {actual_distance:.1f} km<extra></extra>"
    ))
    
    # Fishing zone marker
    zone_label, zone_color = classify_fishing_zone(fish_pred)
    color_map = {"red": "#E74C3C", "yellow": "#F39C12", "green": "#2ECC71"}
    marker_color = color_map.get(zone_color, "#0000FF")
    
    fig.add_trace(go.Scattergeo(
        lon=[dest_lon],
        lat=[dest_lat],
        mode='markers+text',
        marker=dict(size=20, color=marker_color, symbol='star',
                   line=dict(width=3, color='white')),
        text=['Fishing Zone'],
        textposition='top center',
        name='Fishing Zone',
        hovertemplate=f"<b>Optimal Fishing Zone</b><br>" +
                     f"Fish: {fish_pred:.0f}<br>" +
                     f"Safety: {safety_status}<br>" +
                     f"Data: {data_source}<br>" +
                     f"Lat: {dest_lat:.2f}<br>Lon: {dest_lon:.2f}<extra></extra>"
    ))
    
    fig.update_geos(
        projection_type="natural earth",
        showcountries=True,
        showcoastlines=True,
        showland=True,
        landcolor="#2C3E50",
        oceancolor="#34495E",
        coastlinecolor="#ECF0F1",
        bgcolor="#1C2833",
        center=dict(lat=(shore_lat+dest_lat)/2, lon=(shore_lon+dest_lon)/2),
        projection_scale=2.5
    )
    
    fig.update_layout(
        title=dict(text="🗺️ Optimal Fishing Route", x=0.5, xanchor='center',
                  font=dict(size=20, color='#0B3D91', family='Arial Black')),
        height=500,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=True,
        legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)')
    )
    
    return fig

# LIVE MONITORING SETUP
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False
    st.warning("⚠️ Install streamlit-autorefresh for live monitoring: pip install streamlit-autorefresh")

# Sidebar Configuration
st.sidebar.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #0B3D91, #00A8E8); 
            border-radius: 10px; margin-bottom: 20px;'>
    <h2 style='color: white; margin: 0;'>⚙️ Control Panel</h2>
</div>
""", unsafe_allow_html=True)

# Real-Time Data Toggle
use_realtime = st.sidebar.checkbox("🌐 Use Real-Time Ocean Data", value=False,
                                   help="Fetch live marine weather data from Open-Meteo API")

# Live Monitoring Toggle
if AUTOREFRESH_AVAILABLE:
    enable_live = st.sidebar.checkbox("📡 Enable Live Monitoring", value=False,
                                     help="Auto-refresh dashboard with latest data")
    
    if enable_live:
        refresh_interval = st.sidebar.slider("Refresh Interval (minutes)", 1, 30, 5)
        # Auto-refresh
        st_autorefresh(interval=refresh_interval * 60 * 1000, key="live_refresh")
        st.sidebar.success(f"🔄 Auto-refreshing every {refresh_interval} min")
else:
    enable_live = False

st.sidebar.markdown("---")

# Location Settings
with st.sidebar.expander("📍 Location Settings", expanded=True):
    latitude = st.number_input("Latitude", -90.0, 90.0, 10.0, 0.1)
    longitude = st.number_input("Longitude", -180.0, 180.0, 75.0, 0.1)

# Ocean Conditions (disabled if real-time mode)
with st.sidebar.expander("🌊 Ocean Conditions", expanded=not use_realtime):
    year = st.number_input("Year", 2010, 2035, 2024)
    month = st.slider("Month", 1, 12, 6)
    
    if use_realtime:
        st.info("📡 Using real-time data. Manual inputs disabled.")
        avg_sst = 27.0
        wind_speed = 12.0
        wave_height = 1.5
    else:
        avg_sst = st.slider("Sea Surface Temperature (°C)", 20.0, 35.0, 27.0, 0.1)
        wind_speed = st.slider("Wind Speed (m/s)", 5.0, 25.0, 12.0, 0.1)
        wave_height = st.slider("Wave Height (m)", 0.5, 4.0, 1.5, 0.1)

# Advanced Parameters
with st.sidebar.expander("⚙️ Advanced Parameters", expanded=False):
    if use_realtime:
        salinity = 34.5
        chlorophyll = 0.8
        st.info("Using default values for unavailable parameters")
    else:
        salinity = st.slider("Salinity (PSU)", 33.0, 36.0, 34.5, 0.1)
        chlorophyll = st.slider("Chlorophyll (mg/m³)", 0.1, 2.0, 0.8, 0.01)

# Boat Configuration
with st.sidebar.expander("⛵ Boat Configuration", expanded=False):
    boat_speed = st.number_input("Boat Speed (km/h)", 5.0, 50.0, 20.0, 1.0)
    fuel_efficiency = st.number_input("Fuel Efficiency (L/km)", 0.1, 5.0, 0.8, 0.1)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset to Defaults"):
    st.rerun()

# Fetch Real-Time Data if enabled
realtime_data = None
data_source = "Manual"

if use_realtime:
    with st.spinner("🌐 Fetching real-time marine data..."):
        realtime_data = fetch_realtime_marine_weather(latitude, longitude, timeout=10)
        
        if realtime_data:
            data_source = "Real-Time"
            st.sidebar.success("✅ Real-time data loaded")
            # Update variables with real-time data
            avg_sst = realtime_data.get("avg_sst", avg_sst)
            wind_speed = realtime_data.get("wind_speed", wind_speed)
            wave_height = realtime_data.get("wave_height", wave_height)
        else:
            st.sidebar.warning("⚠️ Real-time fetch failed. Using manual inputs.")
            data_source = "Manual (Fallback)"

# Build prediction features
manual_inputs = {
    "year": year, "month": month, "avg_sst": avg_sst,
    "wind_speed": wind_speed, "wave_height": wave_height,
    "salinity": salinity, "chlorophyll": chlorophyll
}

features = build_prediction_features(
    "realtime" if use_realtime and realtime_data else "manual",
    manual_inputs,
    realtime_data
)

# Prepare model input
model_input = pd.DataFrame([{
    "year": features["year"],
    "month": features["month"],
    "avg_sst": features["avg_sst"],
    "wind_speed": features["wind_speed"],
    "wave_height": features["wave_height"],
    "salinity": features["salinity"],
    "chlorophyll": features["chlorophyll"]
}])

# Make Predictions
if fish_model and weather_model:
    try:
        fish_prediction = fish_model.predict(model_input)[0]
        weather_prediction = weather_model.predict(model_input)[0]
        
        risk_mapping = {"Safe": 20, "Moderate": 60, "Dangerous": 90}
        risk_score = risk_mapping.get(weather_prediction, 50)
        
    except Exception as e:
        st.error(f"Prediction error: {e}")
        fish_prediction = 0
        weather_prediction = "Unknown"
        risk_score = 50
else:
    st.error("Models not loaded")
    st.stop()

# Find Best Fishing Zone with coastal snapping
@st.cache_data(ttl=600)
def cached_find_best_zone(lat, lon, features_dict, _model):
    """Cached zone finding (10 min TTL) - uses coastal point"""
    # Snap to coast for realistic departure point
    shore_lat, shore_lon = snap_to_nearest_coast(lat, lon)
    return find_best_fishing_zone(shore_lat, shore_lon, features_dict, _model)

with st.spinner("🎯 Finding optimal fishing zone..."):
    best_zone = cached_find_best_zone(latitude, longitude, features, fish_model)

best_lat = best_zone["best_lat"]
best_lon = best_zone["best_lon"]
best_fish = best_zone["predicted_fish"]

# Calculate distance from shore to fishing zone
shore_lat, shore_lon = snap_to_nearest_coast(latitude, longitude)
distance = calculate_distance(shore_lat, shore_lon, best_lat, best_lon)
fuel_est = estimate_fuel(distance, fuel_efficiency, boat_speed)

# Generate Advisory
advisory = generate_marine_advisory(
    weather_prediction, best_fish, distance,
    features["wave_height"], features["wind_speed"]
)

# Hero Header with LIVE indicator
status_colors = {"Safe": "#2ECC71", "Moderate": "#F39C12", "Dangerous": "#E74C3C"}
status_color = status_colors.get(weather_prediction, "#95A5A6")

live_badge = ""
if enable_live and AUTOREFRESH_AVAILABLE:
    live_badge = "<span class='live-indicator'></span><span style='color: #2ECC71;'>LIVE</span>"

# CHANGE 3: Replace emoji with professional icon
st.markdown(f"""
<div class='hero-banner'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h1 style='margin: 0; color: white; font-size: 42px;'>〰️ MarineSense AI {live_badge}</h1>
            <p style='margin: 5px 0; font-size: 18px; opacity: 0.9;'>Real-Time Marine Intelligence & Decision Platform</p>
            <p style='margin: 5px 0; font-size: 14px; opacity: 0.7;'>
                Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Source: {data_source}
            </p>
        </div>
        <div>
            <span class='status-badge' style='background: {status_color}; font-size: 20px;'>
                {weather_prediction.upper()}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# KPI Cards
zone_label, _ = classify_fishing_zone(best_fish)
confidence_score = best_zone["confidence_score"]

col1, col2, col3, col4 = st.columns(4)

# CHANGE 3: Replace emojis with professional icons in KPI cards
with col1:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: #00A8E8;'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>◉ Best Zone Fish</div>
        <div style='font-size: 36px; font-weight: bold; color: #0B3D91;'>{best_fish:.0f}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Predicted Quantity</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: {status_color};'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>⚠ Safety Status</div>
        <div style='font-size: 36px; font-weight: bold; color: {status_color};'>{weather_prediction}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Current Risk</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: #F39C12;'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>◆ Distance</div>
        <div style='font-size: 36px; font-weight: bold; color: #F39C12;'>{distance:.1f}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Kilometers</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: #2ECC71;'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>◎ Confidence</div>
        <div style='font-size: 36px; font-weight: bold; color: #2ECC71;'>{confidence_score:.0f}%</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Prediction Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Two-column layout: Marine Advisory | Weather Risk Assessment
col1, col2 = st.columns([4, 6])

# COLUMN 1: Marine Advisory (40%)
with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0B3D91, #00A8E8); color: white;
                padding: 12px 18px; border-radius: 10px; box-shadow: 0 6px 20px rgba(102,126,234,0.4);'>
        <h3 style='color: white; margin-top: 0; font-size: 22px;'>Marine Advisory</h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 18px;'><b>Rating:</b> {advisory['overall_rating']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 17px;'>{advisory['safety_assessment']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 17px;'>{advisory['fishing_opportunity']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 17px;'>{advisory['distance_assessment']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 18px;'><b>{advisory['recommended_action']}</b></p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# COLUMN 2: Weather Risk Assessment Section
with col2:
    st.markdown("<h3 style='margin-bottom: 10px;'>Weather Risk Assessment</h3>", unsafe_allow_html=True)
    
    # Two columns for gauge and telemetry
    gauge_col, telemetry_col = st.columns([1, 1])
    
    # Container 1: Gauge Chart
    with gauge_col:
        with st.container():
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": weather_prediction, "font": {"size": 16, "color": "#0B3D91"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": status_color, "thickness": 0.8},
                    "steps": [
                        {"range": [0, 40], "color": "rgba(46,204,113,0.3)"},
                        {"range": [40, 75], "color": "rgba(243,156,18,0.3)"},
                        {"range": [75, 100], "color": "rgba(231,76,60,0.3)"}
                    ],
                    "threshold": {"line": {"color": "white", "width": 4}, "thickness": 0.8, "value": risk_score}
                }
            ))
            fig_gauge.update_layout(
                height=250, 
                paper_bgcolor='rgba(0,0,0,0)', 
                font={'color': "#0B3D91"},
                margin=dict(t=60, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Container 2: Telemetry Panel
    with telemetry_col:
        with st.container():
            # Normalize values for progress bars (0-100%)
            sst_norm = min(max((features['avg_sst'] - 20) / (35 - 20) * 100, 0), 100)
            wind_norm = min(max(features['wind_speed'] / 25 * 100, 0), 100)
            chloro_norm = min(max(features['chlorophyll'] / 2 * 100, 0), 100)
            
            # Vertical telemetry panel
            telemetry_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: transparent; }}
                    .telemetry-panel {{
                        background: transparent;
                        border-radius: 12px;
                        padding: 10px;
                        box-shadow: none;
                    }}
                    .panel-title {{
                        font-size: 20px;
                        font-weight: 700;
                        color: #0B3D91;
                        margin-bottom: 14px;
                        text-align: center;
                    }}
                    .metrics-grid {{
                        display: flex;
                        flex-direction: column;
                        gap: 12px;
                    }}
                    .metric-card {{
                        text-align: left;
                    }}
                    .row-header {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 6px;
                    }}
                    .metric-icon {{
                        font-size: 14px;
                        margin-right: 6px;
                        display: inline-block;
                    }}
                    .metric-label {{
                        font-size: 16px;
                        font-weight: 600;
                        color: #5a6c7d;
                        display: inline-block;
                    }}
                    .metric-value {{
                        font-size: 20px;
                        font-weight: 700;
                        color: #0B3D91;
                    }}
                    .progress-container {{
                        width: 100%;
                        height: 8px;
                        background: rgba(0,0,0,0.08);
                        border-radius: 8px;
                        overflow: hidden;
                        margin-bottom: 4px;
                    }}
                    .progress-bar {{
                        height: 100%;
                        border-radius: 10px;
                        transition: width 0.6s ease;
                    }}
                    .trend-text {{
                        font-size: 13px;
                        color: #6b7280;
                        font-style: italic;
                        line-height: 1.3;
                    }}
                </style>
            </head>
            <body>
                <div class="telemetry-panel">
                    <div class="panel-title">Current Marine Conditions</div>
                    <div class="metrics-grid">
                        <!-- SST Metric -->
                        <div class="metric-card">
                            <div class="row-header">
                                <div>
                                    <span class="metric-icon" style="color: #f59e0b;">🌡️</span>
                                    <span class="metric-label">Sea Surface Temp</span>
                                </div>
                                <div class="metric-value">{features['avg_sst']:.1f}°C</div>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {sst_norm}%; background: linear-gradient(90deg, #f59e0b, #fb923c);"></div>
                            </div>
                            <div class="trend-text">Above 25°C indicates warmer waters</div>
                        </div>
                        
                        <!-- Wind Metric -->
                        <div class="metric-card">
                            <div class="row-header">
                                <div>
                                    <span class="metric-icon" style="color: #3b82f6;">💨</span>
                                    <span class="metric-label">Wind Speed</span>
                                </div>
                                <div class="metric-value">{features['wind_speed']:.1f} m/s</div>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {wind_norm}%; background: linear-gradient(90deg, #3b82f6, #38bdf8);"></div>
                            </div>
                            <div class="trend-text">Windy with moderate gusts</div>
                        </div>
                        
                        <!-- Chlorophyll Metric -->
                        <div class="metric-card">
                            <div class="row-header">
                                <div>
                                    <span class="metric-icon" style="color: #10b981;">🍃</span>
                                    <span class="metric-label">Chlorophyll</span>
                                </div>
                                <div class="metric-value">{features['chlorophyll']:.2f} mg/m³</div>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {chloro_norm}%; background: linear-gradient(90deg, #10b981, #22c55e);"></div>
                            </div>
                            <div class="trend-text">Moderate levels present</div>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Render telemetry panel
            components.html(telemetry_html, height=320, scrolling=False)

st.markdown("---")

# CHANGE 3: Replace emojis with professional icons
st.markdown("### ◆ Optimal Fishing Route")
route_map = create_route_map(latitude, longitude, best_lat, best_lon, best_fish, weather_prediction, data_source)
st.plotly_chart(route_map, use_container_width=True)

st.markdown("---")

# CHANGE 3: Replace emojis with professional icons
st.markdown("### ◇ Trip Planning")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("◆ Fuel Required", f"{fuel_est['fuel_liters']:.1f} L",
             help="Estimated fuel consumption for round trip")

with col2:
    hours = int(fuel_est['travel_hours'])
    minutes = int((fuel_est['travel_hours'] - hours) * 60)
    st.metric("◎ Travel Time", f"{hours}h {minutes}m",
             help="Estimated one-way travel time")

with col3:
    st.metric("◆ Total Distance", f"{distance:.1f} km",
             help="Distance to optimal fishing zone")

st.markdown("---")

# CHANGE 3: Replace emojis with professional icons
st.markdown("### ■ Model Explainability")

with st.expander("View SHAP Analysis (Feature Importance)", expanded=False):
    st.markdown("SHAP shows how each feature contributes to the fish prediction.")
    
    try:
        import shap
        
        @st.cache_data
        def compute_shap(_model, input_data):
            explainer = shap.TreeExplainer(_model)
            shap_values = explainer.shap_values(input_data)
            return explainer, shap_values
        
        explainer, shap_values = compute_shap(fish_model, model_input)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0],
                base_values=explainer.expected_value,
                data=model_input.iloc[0].values,
                feature_names=model_input.columns.tolist()
            ),
            show=False
        )
        st.pyplot(fig)
        plt.close()
    except:
        st.info("SHAP explainability not available. Install shap library for model insights.")

st.markdown("---")

# CHANGE 3: Replace emoji with professional icon
st.markdown("### □ Indian Ocean SST Heatmap")

if not sst_data.empty:
    try:
        india_data = sst_data[
            (sst_data["lat"] >= 0) & (sst_data["lat"] <= 30) &
            (sst_data["lon"] >= 55) & (sst_data["lon"] <= 100)
        ]
        
        if not india_data.empty:
            latest_time = india_data["time"].max()
            latest_data = india_data[india_data["time"] == latest_time]
            pivot = latest_data.pivot_table(index="lat", columns="lon", values="sst")
            
            lat_vals = pivot.index.values
            lon_vals = pivot.columns.values
            sst_grid = pivot.values
            lon2d, lat2d = np.meshgrid(lon_vals, lat_vals)
            
            fig = plt.figure(figsize=(12, 8))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_extent([55, 100, 0, 30], crs=ccrs.PlateCarree())
            
            contour = ax.contourf(lon2d, lat2d, sst_grid, levels=20, cmap="turbo",
                                  transform=ccrs.PlateCarree(), zorder=1)
            ax.contour(lon2d, lat2d, sst_grid, levels=10, colors="black",
                      linewidths=0.5, transform=ccrs.PlateCarree(), zorder=2)
            
            ax.add_feature(cfeature.LAND, facecolor="lightgray", zorder=10)
            ax.add_feature(cfeature.COASTLINE, linewidth=1, zorder=11)
            ax.add_feature(cfeature.BORDERS, linestyle=":", zorder=11)
            
            cbar = plt.colorbar(contour, ax=ax, orientation="horizontal", pad=0.05)
            cbar.set_label("Sea Surface Temperature (°C)", fontsize=12)
            ax.set_title("Indian Ocean SST Distribution", fontsize=14, fontweight='bold')
            
            st.pyplot(fig)
            plt.close()
        else:
            st.warning("No SST data available for the selected region.")
    except Exception as e:
        st.error(f"Error rendering SST heatmap: {e}")
else:
    st.warning("SST data not loaded.")

st.markdown("---")

# Professional Footer
st.markdown(f"""
<div style='background: linear-gradient(135deg, #0B3D91, #00A8E8); color: white; padding: 30px; 
            border-radius: 15px; text-align: center; margin-top: 40px;'>
    <h3 style='color: white; margin-top: 0;'>MarineSense AI v3.0 - Real-Time Edition</h3>
    <p style='margin: 10px 0;'>Advanced Marine Intelligence & Live Monitoring Platform</p>
    <p style='margin: 5px 0; font-size: 14px;'>Data Sources: Open-Meteo Marine API, NOAA, Satellite Imagery</p>
    <p style='margin: 5px 0; font-size: 14px;'>
        <span style='color: #2ECC71; font-size: 20px;'>●</span> System Status: {'LIVE' if enable_live else 'Online'}
    </p>
    <p style='margin: 15px 0; font-size: 12px; opacity: 0.8;'>
        © 2024 MarineSense AI | Real-Time Marine Decision Platform
    </p>
</div>
""", unsafe_allow_html=True)

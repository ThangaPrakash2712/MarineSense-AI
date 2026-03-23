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

# ── Page state init ───────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "dashboard"

# Import sonar detection module
from sonar import (
    detect_fish_with_model,
    update_route_decision,
    fuse_sonar_with_ai,
    run_detection_loop,
    summarise_session,
)

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

# ── Hide default Streamlit chrome ─────────────────────────────────────────────
st.markdown("""
<style>
    header { visibility: hidden; }
    .stToolbar { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container { padding-top: 0rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Top Navigation Bar ────────────────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
    /* Push Streamlit content below the fixed navbar */
    .block-container { padding-top: 80px !important; }
    section[data-testid="stSidebar"] { top: 56px !important; }

    .topnav {
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 9999;
        height: 56px;
        background: linear-gradient(90deg, #0B3D91 0%, #0d4fa8 60%, #00A8E8 100%);
        display: flex;
        align-items: center;
        padding: 0 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.25);
        gap: 4px;
    }
    .topnav-brand {
        color: white;
        font-weight: 700;
        font-size: 16px;
        letter-spacing: 0.5px;
        margin-right: 28px;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .topnav-brand i { font-size: 18px; color: #00A8E8; }
    .nav-item {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 7px 16px;
        border-radius: 8px;
        cursor: pointer;
        color: rgba(255,255,255,0.75);
        font-size: 13.5px;
        font-weight: 500;
        text-decoration: none;
        transition: background 0.2s, color 0.2s;
        border: none;
        background: transparent;
        white-space: nowrap;
    }
    .nav-item:first-of-type { margin-left: auto; }
    .nav-item i { font-size: 15px; }
    .nav-item:hover {
        background: rgba(255,255,255,0.15);
        color: #ffffff;
    }
    .nav-item.active {
        background: rgba(255,255,255,0.2);
        color: #ffffff;
        box-shadow: inset 0 -2px 0 #00e5ff;
    }
</style>
""", unsafe_allow_html=True)

# Render navbar buttons using Streamlit columns (zero-gap trick)
nav_cols = st.columns([2, 1, 1, 1, 1, 8])

page = st.session_state["page"]


# Styled navbar overlay (purely visual, buttons above handle clicks)
_active = st.session_state["page"]
st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<div class="topnav">
    <div class="topnav-brand">
        <i class="fa-solid fa-water"></i> MarineSense AI
    </div>
    <span class="nav-item {'active' if _active == 'dashboard' else ''}">
        <i class="fa-solid fa-chart-line"></i> Dashboard
    </span>
    <span class="nav-item {'active' if _active == 'route' else ''}">
        <i class="fa-solid fa-route"></i> Route
    </span>
    <span class="nav-item {'active' if _active == 'sonar' else ''}">
        <i class="fa-solid fa-satellite-dish"></i> Sonar
    </span>
    <span class="nav-item {'active' if _active == 'profile' else ''}">
        <i class="fa-solid fa-circle-user"></i> Profile
    </span>
</div>
""", unsafe_allow_html=True)

# ── Hide the raw Streamlit nav buttons (they're replaced by the overlay above) ──
st.markdown("""
<style>
    div[data-testid="column"]:nth-child(2) button,
    div[data-testid="column"]:nth-child(3) button,
    div[data-testid="column"]:nth-child(4) button,
    div[data-testid="column"]:nth-child(5) button {
        visibility: hidden;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        min-height: 0 !important;
    }
    div[data-testid="column"]:nth-child(1) { visibility: hidden; height: 0 !important; }
</style>
""", unsafe_allow_html=True)

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
        height=400,
        autosize=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(
            x=0.98, y=0.02,
            xanchor='right', yanchor='bottom',
            bgcolor='rgba(0,0,0,0.55)',
            borderwidth=0,
            font=dict(color='white', size=10)
        )
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

# ── Sonar Sidebar Controls ─────────────────────────────────────────────────
st.sidebar.markdown("---")
with st.sidebar.expander("Sonar Detection", expanded=False):
    sonar_enabled = st.checkbox("Enable Sonar Scanning", value=False,
                                help="Simulate real-time sonar fish detection")
    sonar_steps = st.slider("Scan Steps", 5, 30, 10,
                            help="Number of sonar pings per session")
    sonar_use_yolo = st.checkbox("Enable YOLO Stub", value=False,
                                 help="Layer YOLO-style detection on sonar signal")
    sonar_run = st.button("Run Sonar Scan", disabled=not sonar_enabled)

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

# ── Route Page ────────────────────────────────────────────────────────────────
def show_route_page():
    st.markdown("## Route & Map Planning")
    st.markdown("### Optimal Fishing Route")
    route_map = create_route_map(latitude, longitude, best_lat, best_lon, best_fish, weather_prediction, data_source)
    st.plotly_chart(route_map, use_container_width=True)
    st.markdown("### Trip Planning")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fuel Required", f"{fuel_est['fuel_liters']:.1f} L", help="Estimated fuel for round trip")
    with col2:
        _h = int(fuel_est['travel_hours'])
        _m = int((fuel_est['travel_hours'] - _h) * 60)
        st.metric("Travel Time", f"{_h}h {_m}m", help="Estimated one-way travel time")
    with col3:
        st.metric("Total Distance", f"{distance:.1f} km", help="Distance to optimal fishing zone")


# ── Sonar Page ────────────────────────────────────────────────────────────────
def show_sonar_page():
    st.markdown("## Sonar Detection Panel")
    if not sonar_enabled:
        st.info("Enable Sonar Detection in the sidebar to activate real-time scanning.")
        return
    if sonar_run or "sonar_results" not in st.session_state:
        with st.spinner("Running sonar scan..."):
            st.session_state.sonar_results = run_detection_loop(
                num_steps=sonar_steps, base_sst=features["avg_sst"],
                base_chlorophyll=features["chlorophyll"],
                zone_confidence=confidence_score, use_yolo=sonar_use_yolo,
            )
            st.session_state.sonar_summary = summarise_session(st.session_state.sonar_results)
    results = st.session_state.sonar_results
    summary = st.session_state.sonar_summary
    latest = results[-1]
    fused_conf, fusion_label = fuse_sonar_with_ai(
        ai_confidence=confidence_score, sonar_confidence=latest["confidence"],
        fish_detected=latest["fish_detected"], density_label=latest["density_label"],
    )
    route_decision = update_route_decision(
        detection=latest, current_lat=shore_lat, current_lon=shore_lon,
        predicted_lat=best_lat, predicted_lon=best_lon, distance_to_target_km=distance,
    )
    action_color = {"REROUTE": "#E74C3C", "CONFIRM": "#2ECC71", "CONTINUE": "#F39C12"}.get(route_decision["action"], "#95A5A6")
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#0B3D91,#00A8E8);padding:14px 20px;border-radius:12px;
                margin-bottom:16px;display:flex;justify-content:space-between;align-items:center;'>
        <div style='color:white;'><span style='font-size:13px;opacity:0.8;'>SONAR STATUS</span><br>
        <span style='font-size:18px;font-weight:700;'>Active &mdash; {summary['total_steps']} pings</span></div>
        <span style='background:{action_color};color:white;padding:6px 14px;border-radius:20px;
                     font-weight:700;font-size:14px;'>{route_decision['action']}</span>
    </div>""", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"<div class='kpi-card' style='border-top-color:#00A8E8;'><div style='font-size:13px;color:#7F8C8D;'>Detection Rate</div><div style='font-size:30px;font-weight:bold;color:#0B3D91;'>{summary['detection_rate_pct']:.0f}%</div></div>", unsafe_allow_html=True)
    with s2:
        st.markdown(f"<div class='kpi-card' style='border-top-color:#2ECC71;'><div style='font-size:13px;color:#7F8C8D;'>Fused Confidence</div><div style='font-size:30px;font-weight:bold;color:#2ECC71;'>{fused_conf:.0f}%</div><div style='font-size:12px;color:#95A5A6;'>{fusion_label}</div></div>", unsafe_allow_html=True)
    with s3:
        st.markdown(f"<div class='kpi-card' style='border-top-color:#E74C3C;'><div style='font-size:13px;color:#7F8C8D;'>Fish Depth</div><div style='font-size:30px;font-weight:bold;color:#E74C3C;'>{latest['depth_m']:.0f} m</div></div>", unsafe_allow_html=True)
    with s4:
        st.markdown(f"<div class='kpi-card' style='border-top-color:#F39C12;'><div style='font-size:13px;color:#7F8C8D;'>Est. Fish Count</div><div style='font-size:30px;font-weight:bold;color:#F39C12;'>{summary['peak_count']}</div><div style='font-size:12px;color:#95A5A6;'>{summary['dominant_density']} density</div></div>", unsafe_allow_html=True)


# ── Profile Page ──────────────────────────────────────────────────────────────
def show_profile_page():
    st.markdown("## User Profile")
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("""
        <div style='width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,#0B3D91,#00A8E8);
                    display:flex;align-items:center;justify-content:center;margin:10px auto;'>
            <i class='fa-solid fa-circle-user' style='font-size:60px;color:white;'></i>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("### Marine Operator")
        st.markdown("**Platform:** MarineSense AI v3.0  \n**Role:** Fisheries Intelligence Analyst")
        st.markdown(f"**Session Started:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.markdown("---")
    st.markdown("### Current Session Parameters")
    i1, i2 = st.columns(2)
    with i1:
        st.info(f"**Location:** {latitude:.2f}°N, {longitude:.2f}°E");
        st.info(f"**Data Source:** {data_source}")
    with i2:
        st.info(f"**Weather Status:** {weather_prediction}")
        st.info(f"**Best Zone Fish:** {best_fish:.0f} units")


# ── Page Router (non-dashboard pages stop here) ───────────────────────────────
_cur_page = st.session_state["page"]
if _cur_page == "route":
    show_route_page()
    st.stop()
elif _cur_page == "sonar":
    show_sonar_page()
    st.stop()
elif _cur_page == "profile":
    show_profile_page()
    st.stop()

# ── Dashboard content (only reached when page == "dashboard") ─────────────────
# Hero Header with LIVE indicator
status_colors = {"Safe": "#2ECC71", "Moderate": "#F39C12", "Dangerous": "#E74C3C"}
status_color = status_colors.get(weather_prediction, "#95A5A6")

live_badge = ""
if enable_live and AUTOREFRESH_AVAILABLE:
    live_badge = "<span class='live-indicator'></span><span style='color: #2ECC71;'>LIVE</span>"

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
        <h3 style='color: white; margin-top: 0; font-size: 24px;'>Marine Advisory</h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 20px;'><b>Rating:</b> {advisory['overall_rating']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 18px;'>{advisory['safety_assessment']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 18px;'>{advisory['fishing_opportunity']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 18px;'>{advisory['distance_assessment']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: black; margin: 8px 0; font-size: 20px;'><b>{advisory['recommended_action']}</b></p>", unsafe_allow_html=True)
    
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

# ── Route + Trip Planning + AI Model (self-contained grid) ──────────────────
# Render map and SHAP to portable HTML/image strings so the entire
# grid lives inside ONE components.html call — the only way to guarantee
# CSS grid placement in Streamlit (st widgets always escape HTML flow).

import io, base64

_h = int(fuel_est['travel_hours'])
_m = int((fuel_est['travel_hours'] - _h) * 60)

# 1. Map → Plotly full HTML string (self-contained, no external CDN needed)
route_map = create_route_map(
    latitude, longitude, best_lat, best_lon,
    best_fish, weather_prediction, data_source
)
map_html = route_map.to_html(full_html=False, include_plotlyjs='cdn')

# 2. SHAP / AI panel → PNG base64 embedded image
ai_panel_html = ""
try:
    import shap

    @st.cache_data
    def compute_shap(_model, input_data):
        explainer = shap.TreeExplainer(_model)
        return explainer, explainer.shap_values(input_data)

    explainer, shap_values = compute_shap(fish_model, model_input)
    fig_shap, _ = plt.subplots(figsize=(5, 8))
    shap.waterfall_plot(
        shap.Explanation(
            values=shap_values[0],
            base_values=explainer.expected_value,
            data=model_input.iloc[0].values,
            feature_names=model_input.columns.tolist()
        ),
        show=False
    )
    buf = io.BytesIO()
    fig_shap.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    plt.close(fig_shap)
    buf.seek(0)
    shap_b64 = base64.b64encode(buf.read()).decode()
    ai_panel_html = f"<img src='data:image/png;base64,{shap_b64}' style='width:100%;height:auto;display:block;' />"
except Exception:
    ai_panel_html = "<p style='color:#7F8C8D;font-size:13px;padding:12px;'>Loading model insights...</p>"

# 3. Build the complete self-contained grid HTML
grid_html = f"""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: transparent; }}

  /* ── MAIN GRID ── */
  .dashboard {{
    display: grid;
    grid-template-columns: 2fr 1fr;
    grid-template-rows: auto auto;
    gap: 20px;
    width: 100%;
  }}

  /* ── SECTION HEADINGS ── */
  .section-heading {{
    font-size: 15px;
    font-weight: 600;
    color: #0B3D91;
    margin-bottom: 12px;
    margin-top: 0;
    letter-spacing: 0.2px;
  }}

  /* ── MAP WRAPPER: grid-column 1, grid-row 1 ── */
  .map-wrapper {{
    grid-column: 1;
    grid-row: 1;
    display: flex;
    flex-direction: column;
  }}
  .map-container {{
    width: 100%;
    height: 420px;
    padding: 0;
    margin: 0;
    overflow: hidden;
    border-radius: 10px;
    background: #1C2833;
  }}
  .map-container iframe {{
    width: 100%;
    height: 100%;
    border: none;
    display: block;
  }}

  /* ── CARDS WRAPPER: grid-column 1, grid-row 2 ── */
  .cards-wrapper {{
    grid-column: 1;
    grid-row: 2;
    display: flex;
    flex-direction: column;
  }}
  .cards {{
    display: flex;
    gap: 20px;
  }}
  .card {{
    flex: 1;
    padding: 18px 20px;
    border-radius: 10px;
    background: linear-gradient(135deg, #0B3D91, #00A8E8);
    color: white;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .card-icon {{
    font-size: 24px;
    opacity: 0.95;
    flex-shrink: 0;
  }}
  .card-content {{
    text-align: left;
  }}
  .card .c-label {{
    font-size: 11px;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 5px;
  }}
  .card .c-value {{
    font-size: 22px;
    font-weight: 700;
  }}

  /* ── AI PANEL WRAPPER: grid-column 2, grid-row 1 / span 2 ── */
  .ai-wrapper {{
    grid-column: 2;
    grid-row: 1 / span 2;
    display: flex;
    flex-direction: column;
  }}
  .ai-panel {{
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    display: flex;
    flex-direction: column;
    flex: 1;
  }}
  .ai-panel-inner {{
    flex: 1;
    overflow-y: auto;
  }}

  /* ── Responsive ── */
  @media (max-width: 768px) {{
    .dashboard {{ grid-template-columns: 1fr; }}
    .map-wrapper   {{ grid-column: 1; grid-row: 1; }}
    .cards-wrapper {{ grid-column: 1; grid-row: 2; }}
    .ai-wrapper    {{ grid-column: 1; grid-row: 3; }}
    .cards {{ flex-direction: column; }}
  }}
</style>
</head>
<body>
<div class="dashboard">

  <!-- MAP: col 1, row 1 -->
  <div class="map-wrapper">
    <div class="section-heading">Optimal Fishing Zone</div>
    <div class="map-container">
      {map_html}
    </div>
  </div>

  <!-- CARDS: col 1, row 2 -->
  <div class="cards-wrapper">
    <div class="section-heading">Trip Planning</div>
    <div class="cards">
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-gas-pump"></i></div>
        <div class="card-content">
          <div class="c-label">Fuel Required</div>
          <div class="c-value">{fuel_est['fuel_liters']:.1f} L</div>
        </div>
      </div>
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-clock"></i></div>
        <div class="card-content">
          <div class="c-label">Travel Time</div>
          <div class="c-value">{_h}h {_m}m</div>
        </div>
      </div>
      <div class="card">
        <div class="card-icon"><i class="fa-solid fa-route"></i></div>
        <div class="card-content">
          <div class="c-label">Total Distance</div>
          <div class="c-value">{distance:.1f} km</div>
        </div>
      </div>
    </div>
  </div>

  <!-- AI PANEL: col 2, row 1 / span 2 -->
  <div class="ai-wrapper">
    <div class="section-heading">AI Model (Explainability)</div>
    <div class="ai-panel">
      <div class="ai-panel-inner">
        {ai_panel_html}
      </div>
    </div>
  </div>

</div>
</body>
</html>
"""

components.html(grid_html, height=700, scrolling=False)

st.markdown("---")

# ── Sonar Detection Panel ────────────────────────────────────────────────────
st.markdown("### ◈ Sonar Fish Detection")

if not sonar_enabled:
    st.info("Enable Sonar Detection in the sidebar to activate real-time scanning.")
else:
    if sonar_run or "sonar_results" not in st.session_state:
        with st.spinner("Running sonar scan..."):
            st.session_state.sonar_results = run_detection_loop(
                num_steps=sonar_steps,
                base_sst=features["avg_sst"],
                base_chlorophyll=features["chlorophyll"],
                zone_confidence=confidence_score,
                use_yolo=sonar_use_yolo,
            )
            st.session_state.sonar_summary = summarise_session(st.session_state.sonar_results)

    results = st.session_state.sonar_results
    summary = st.session_state.sonar_summary
    latest = results[-1]

    fused_conf, fusion_label = fuse_sonar_with_ai(
        ai_confidence=confidence_score,
        sonar_confidence=latest["confidence"],
        fish_detected=latest["fish_detected"],
        density_label=latest["density_label"],
    )

    route_decision = update_route_decision(
        detection=latest,
        current_lat=shore_lat,
        current_lon=shore_lon,
        predicted_lat=best_lat,
        predicted_lon=best_lon,
        distance_to_target_km=distance,
    )

    action_colors = {"REROUTE": "#E74C3C", "CONFIRM": "#2ECC71", "CONTINUE": "#F39C12"}
    action_color = action_colors.get(route_decision["action"], "#95A5A6")

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0B3D91, #00A8E8); padding: 14px 20px;
                border-radius: 12px; margin-bottom: 16px; display: flex;
                justify-content: space-between; align-items: center;'>
        <div style='color: white;'>
            <span style='font-size: 13px; opacity: 0.8;'>SONAR STATUS</span><br>
            <span style='font-size: 18px; font-weight: 700;'>Active &mdash; {summary['total_steps']} pings</span>
        </div>
        <div style='text-align: right;'>
            <span style='background: {action_color}; color: white; padding: 6px 14px;
                         border-radius: 20px; font-weight: 700; font-size: 14px;'>
                {route_decision['action']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    alert_bg = "#fef9e7" if latest["fish_detected"] else "#f8f9fa"
    alert_border = "#F39C12" if latest["fish_detected"] else "#BDC3C7"
    st.markdown(f"""
    <div style='background: {alert_bg}; border-left: 4px solid {alert_border};
                padding: 12px 16px; border-radius: 8px; margin-bottom: 16px;
                font-size: 14px; color: #2C3E50;'>
        <b>Latest Alert:</b> {latest['alert']}<br>
        <span style='font-size: 12px; color: #7F8C8D; margin-top: 4px; display: block;'>
            {route_decision['reason']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        st.markdown(f"""
        <div class='kpi-card' style='border-top-color: #00A8E8;'>
            <div style='font-size: 13px; color: #7F8C8D;'>Detection Rate</div>
            <div style='font-size: 30px; font-weight: bold; color: #0B3D91;'>{summary['detection_rate_pct']:.0f}%</div>
            <div style='font-size: 12px; color: #95A5A6;'>of {summary['total_steps']} pings</div>
        </div>""", unsafe_allow_html=True)
    with s_col2:
        st.markdown(f"""
        <div class='kpi-card' style='border-top-color: #2ECC71;'>
            <div style='font-size: 13px; color: #7F8C8D;'>Fused Confidence</div>
            <div style='font-size: 30px; font-weight: bold; color: #2ECC71;'>{fused_conf:.0f}%</div>
            <div style='font-size: 12px; color: #95A5A6;'>{fusion_label}</div>
        </div>""", unsafe_allow_html=True)
    with s_col3:
        st.markdown(f"""
        <div class='kpi-card' style='border-top-color: #E74C3C;'>
            <div style='font-size: 13px; color: #7F8C8D;'>Fish Depth</div>
            <div style='font-size: 30px; font-weight: bold; color: #E74C3C;'>{latest['depth_m']:.0f} m</div>
            <div style='font-size: 12px; color: #95A5A6;'>Latest ping</div>
        </div>""", unsafe_allow_html=True)
    with s_col4:
        st.markdown(f"""
        <div class='kpi-card' style='border-top-color: #F39C12;'>
            <div style='font-size: 13px; color: #7F8C8D;'>Est. Fish Count</div>
            <div style='font-size: 30px; font-weight: bold; color: #F39C12;'>{summary['peak_count']}</div>
            <div style='font-size: 12px; color: #95A5A6;'>{summary['dominant_density']} density</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    chart_col1, chart_col2 = st.columns([3, 2])

    with chart_col1:
        steps = [r["step"] for r in results]
        confs = [r["confidence"] for r in results]
        echoes = [r["echo_intensity"] * 100 for r in results]
        depths = [r["depth_m"] for r in results]

        fig_sonar = go.Figure()
        fig_sonar.add_trace(go.Scatter(
            x=steps, y=confs, name="Confidence %",
            line=dict(color="#2ECC71", width=2),
            fill="tozeroy", fillcolor="rgba(46,204,113,0.1)"
        ))
        fig_sonar.add_trace(go.Scatter(
            x=steps, y=echoes, name="Echo Intensity %",
            line=dict(color="#00A8E8", width=2, dash="dot")
        ))
        fig_sonar.add_hline(
            y=28, line_dash="dash", line_color="#E74C3C",
            annotation_text="Detection threshold",
            annotation_position="bottom right"
        )
        fig_sonar.update_layout(
            title="Sonar Signal — Confidence & Echo",
            height=260, margin=dict(t=40, b=30, l=40, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,249,250,0.8)",
            legend=dict(orientation="h", y=1.12),
            yaxis=dict(range=[0, 105], title="%"),
            xaxis=dict(title="Scan Step"),
        )
        st.plotly_chart(fig_sonar, use_container_width=True)

    with chart_col2:
        dist = summary["density_distribution"]
        labels = [k for k, v in dist.items() if v > 0]
        values = [v for v in dist.values() if v > 0]
        donut_colors = {
            "High": "#E74C3C", "Medium": "#F39C12",
            "Low": "#3498DB", "None": "#BDC3C7"
        }
        fig_donut = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker_colors=[donut_colors.get(l, "#95A5A6") for l in labels],
            textinfo="label+percent",
            textfont_size=11,
        ))
        fig_donut.update_layout(
            title="Density Distribution",
            height=260, margin=dict(t=40, b=10, l=10, r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with st.expander("Fish Depth Heatmap", expanded=False):
        fig_heat = go.Figure(go.Heatmap(
            z=[depths],
            x=steps,
            y=["Depth (m)"],
            colorscale=[
                [0.0, "#EBF5FB"], [0.3, "#3498DB"],
                [0.6, "#1A5276"], [1.0, "#0B3D91"]
            ],
            text=[[f"{d:.0f} m" for d in depths]],
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Depth m", thickness=12),
        ))
        fig_heat.update_layout(
            title="Fish Detection Depth per Scan Step",
            height=160, margin=dict(t=40, b=30, l=60, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# ── End Sonar Panel ───────────────────────────────────────────────────────────


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

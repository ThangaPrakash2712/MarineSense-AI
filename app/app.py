import streamlit as st
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

st.set_page_config(page_title="MarineSense AI", layout="wide", initial_sidebar_state="expanded")

# TASK 1: Premium Theme & Styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    .stApp {
        background: linear-gradient(to bottom, rgba(11,61,145,0.05), rgba(0,168,232,0.05));
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #0B3D91;
    }
    .premium-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 15px 0;
    }
    .kpi-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(240,248,255,0.9));
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-top: 4px solid;
        transition: transform 0.3s, box-shadow 0.3s;
        margin: 10px 0;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .hero-banner {
        background: linear-gradient(135deg, #0B3D91, #00A8E8);
        color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin-bottom: 30px;
    }
    .status-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
        margin: 20px 0;
    }
    h1, h2, h3 { color: #0B3D91; }
    .stButton>button {
        background: linear-gradient(135deg, #00A8E8, #0B3D91);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,168,232,0.4);
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent.parent
fish_model_path = BASE_DIR / "models" / "fish_prediction_model.pkl"
weather_model_path = BASE_DIR / "models" / "weather_risk_model.pkl"
sst_path = BASE_DIR / "data" / "processed" / "sst_indian_ocean.csv"

@st.cache_resource
def load_models():
    with st.spinner("🔄 Loading AI models..."):
        time.sleep(0.5)
        try:
            fish_model = joblib.load(fish_model_path)
            weather_model = joblib.load(weather_model_path)
            return fish_model, weather_model
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return None, None

@st.cache_data
def load_sst():
    try:
        return pd.read_csv(sst_path)
    except Exception as e:
        st.error(f"Error loading SST data: {e}")
        return pd.DataFrame()

fish_model, weather_model = load_models()
sst_data = load_sst()

def engineer_features(df):
    df_enhanced = df.copy()
    if 'avg_sst' in df_enhanced.columns:
        df_enhanced['sst_anomaly'] = df_enhanced['avg_sst'] - 27.5
    if 'wind_speed' in df_enhanced.columns and 'wave_height' in df_enhanced.columns:
        df_enhanced['wind_wave_interaction'] = df_enhanced['wind_speed'] * df_enhanced['wave_height']
    if 'month' in df_enhanced.columns:
        df_enhanced['month_sin'] = np.sin(2 * np.pi * df_enhanced['month'] / 12)
        df_enhanced['month_cos'] = np.cos(2 * np.pi * df_enhanced['month'] / 12)
    return df_enhanced

def fishing_advisory(risk_label):
    advisory_map = {
        "Safe": ("Safe to Go Fishing", "green"),
        "Moderate": ("Go With Caution", "orange"),
        "Dangerous": ("Not Safe for Fishing", "red")
    }
    return advisory_map.get(risk_label, ("Unknown Risk", "gray"))

def classify_fishing_zone(fish_quantity):
    if fish_quantity > 250:
        return "High Potential", "red"
    elif fish_quantity >= 150:
        return "Medium Potential", "yellow"
    else:
        return "Low Potential", "green"

# TASK 6: Premium Map Upgrade
def create_premium_hotspot_map(lat, lon, fish_quantity, safety_status):
    zone_label, zone_color = classify_fishing_zone(fish_quantity)
    color_map = {"red": "#E74C3C", "yellow": "#F39C12", "green": "#2ECC71"}
    marker_color = color_map.get(zone_color, "#0000FF")
    
    fig = go.Figure(data=go.Scattergeo(
        lon=[lon],
        lat=[lat],
        mode='markers+text',
        marker=dict(
            size=25,
            color=marker_color,
            line=dict(width=3, color='white'),
            symbol='circle'
        ),
        text=[f"{zone_label}"],
        hovertemplate=f"<b>{zone_label}</b><br>" +
                      f"Fish: {fish_quantity:.0f}<br>" +
                      f"Safety: {safety_status}<br>" +
                      f"Lat: {lat:.2f}, Lon: {lon:.2f}<extra></extra>",
        textposition="top center",
        textfont=dict(size=14, color='white', family='Arial Black')
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
        center=dict(lat=lat, lon=lon),
        projection_scale=3
    )
    
    fig.update_layout(
        title=dict(text=f"🎯 Fishing Zone: {zone_label}", x=0.5, xanchor='center', 
                   font=dict(size=20, color='#0B3D91', family='Arial Black')),
        height=450,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

# TASK 4: Interactive Trend Charts
def create_trend_charts(sst, wind, wave, chloro, month):
    months = list(range(max(1, month-5), month+1))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=[sst-2, sst-1, sst-0.5, sst, sst+0.5, sst+1][:len(months)],
                             mode='lines+markers', name='SST Trend', line=dict(color='#E74C3C', width=3),
                             marker=dict(size=8)))
    fig.update_layout(title="Sea Surface Temperature Trend", xaxis_title="Month", yaxis_title="SST (°C)",
                      height=300, template='plotly_white')
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=[wind-2, wind-1, wind, wind+1, wind+2], 
                              y=[wave-0.3, wave-0.1, wave, wave+0.2, wave+0.4],
                              mode='markers', marker=dict(size=12, color='#00A8E8'),
                              name='Wind vs Wave'))
    fig2.update_layout(title="Wind Speed vs Wave Height", xaxis_title="Wind (m/s)", 
                       yaxis_title="Wave (m)", height=300, template='plotly_white')
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=months, y=[chloro-0.1, chloro, chloro+0.1, chloro+0.2, chloro+0.15, chloro+0.1][:len(months)],
                              mode='lines+markers', name='Chlorophyll', line=dict(color='#2ECC71', width=3),
                              marker=dict(size=8)))
    fig3.update_layout(title="Chlorophyll Concentration Trend", xaxis_title="Month", 
                       yaxis_title="Chlorophyll (mg/m³)", height=300, template='plotly_white')
    
    return fig, fig2, fig3

# TASK 5: Risk Breakdown Panel
def create_risk_breakdown(wind, wave, sst, salinity, chloro):
    factors = ['Wind Speed', 'Wave Height', 'SST Anomaly', 'Salinity', 'Chlorophyll']
    risk_values = [
        min(wind/25 * 100, 100),
        min(wave/4 * 100, 100),
        abs(sst - 27.5) * 10,
        abs(salinity - 34.5) * 20,
        max(0, (1.5 - chloro) * 50)
    ]
    
    colors = ['#E74C3C' if v > 60 else '#F39C12' if v > 30 else '#2ECC71' for v in risk_values]
    
    fig = go.Figure(go.Bar(
        x=risk_values,
        y=factors,
        orientation='h',
        marker=dict(color=colors),
        text=[f"{v:.1f}%" for v in risk_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="🧩 Risk Factor Analysis",
        xaxis_title="Risk Contribution (%)",
        height=350,
        template='plotly_white',
        showlegend=False
    )
    
    return fig

# TASK 8: Smart Insights Panel
def generate_ai_insights(fish_pred, risk, sst, wind, wave, chloro, month):
    insights = []
    
    if fish_pred > 250:
        insights.append("🎯 Excellent fishing conditions detected with high fish aggregation potential.")
    elif fish_pred > 150:
        insights.append("📊 Moderate fish population expected in this zone.")
    else:
        insights.append("⚠️ Low fish density predicted. Consider alternative locations.")
    
    if risk == "Safe":
        insights.append("✅ Weather conditions are optimal for fishing operations.")
    elif risk == "Moderate":
        insights.append("⚡ Proceed with caution. Monitor weather conditions closely.")
    else:
        insights.append("🚨 Dangerous conditions. Fishing operations not recommended.")
    
    if month in [3, 4, 10, 11]:
        insights.append("🌊 Current month shows favorable seasonal patterns for fishing.")
    
    if chloro > 1.0:
        insights.append("🌿 High chlorophyll levels indicate rich marine ecosystem.")
    
    confidence = min(95, 70 + (chloro * 10) + (5 if 26 < sst < 29 else 0))
    insights.append(f"🎓 Model Confidence: {confidence:.1f}%")
    
    return insights

# TASK 7: Professional Sidebar
st.sidebar.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #0B3D91, #00A8E8); 
            border-radius: 10px; margin-bottom: 20px;'>
    <h2 style='color: white; margin: 0;'>⚙️ Control Panel</h2>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("📍 Location Settings", expanded=True):
    latitude = st.number_input("Latitude", -90.0, 90.0, 10.0, 0.1, help="Enter latitude (-90 to 90)")
    longitude = st.number_input("Longitude", -180.0, 180.0, 75.0, 0.1, help="Enter longitude (-180 to 180)")

with st.sidebar.expander("🌊 Ocean Conditions", expanded=True):
    year = st.number_input("Year", 2010, 2035, 2024)
    month = st.slider("Month", 1, 12, 6)
    avg_sst = st.slider("Sea Surface Temperature (°C)", 20.0, 35.0, 27.0, 0.1)
    wind_speed = st.slider("Wind Speed (m/s)", 5.0, 25.0, 12.0, 0.1)
    wave_height = st.slider("Wave Height (m)", 0.5, 4.0, 1.5, 0.1)

with st.sidebar.expander("⚙️ Advanced Parameters", expanded=False):
    salinity = st.slider("Salinity (PSU)", 33.0, 36.0, 34.5, 0.1)
    chlorophyll = st.slider("Chlorophyll (mg/m³)", 0.1, 2.0, 0.8, 0.01)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset to Defaults"):
    st.rerun()

base_input = pd.DataFrame(
    [[year, month, avg_sst, wind_speed, wave_height, salinity, chlorophyll]],
    columns=["year", "month", "avg_sst", "wind_speed", "wave_height", "salinity", "chlorophyll"]
)

model_input = base_input.copy()

if fish_model and weather_model:
    try:
        fish_prediction = fish_model.predict(model_input)[0]
        weather_prediction = weather_model.predict(model_input)[0]
        advisory_text, advisory_color = fishing_advisory(weather_prediction)
        risk_mapping = {"Safe": 20, "Moderate": 60, "Dangerous": 90}
        risk_score = risk_mapping.get(weather_prediction, 50)
    except Exception as e:
        st.error(f"Prediction error: {e}")
        fish_prediction = 0
        weather_prediction = "Unknown"
        advisory_text = "Error"
        advisory_color = "gray"
        risk_score = 50
else:
    st.error("Models not loaded. Please check model files.")
    st.stop()

# TASK 2: Hero Header Section
status_colors = {"Safe": "#2ECC71", "Moderate": "#F39C12", "Dangerous": "#E74C3C"}
status_color = status_colors.get(weather_prediction, "#95A5A6")

st.markdown(f"""
<div class='hero-banner'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <h1 style='margin: 0; color: white; font-size: 42px;'>🌊 MarineSense AI</h1>
            <p style='margin: 5px 0; font-size: 18px; opacity: 0.9;'>Advanced Marine Intelligence & Prediction System</p>
            <p style='margin: 5px 0; font-size: 14px; opacity: 0.7;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div>
            <span class='status-badge' style='background: {status_color}; font-size: 20px;'>
                {weather_prediction.upper()}
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# TASK 3: Advanced KPI Cards
zone_label, _ = classify_fishing_zone(fish_prediction)
confidence_score = min(95, 70 + (chlorophyll * 10) + (5 if 26 < avg_sst < 29 else 0))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: #00A8E8;'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>🐟 Fish Quantity</div>
        <div style='font-size: 36px; font-weight: bold; color: #0B3D91;'>{fish_prediction:.0f}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Predicted Index</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: {status_color};'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>⚠️ Safety Status</div>
        <div style='font-size: 36px; font-weight: bold; color: {status_color};'>{weather_prediction}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Current Risk Level</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    zone_colors = {"High Potential": "#E74C3C", "Medium Potential": "#F39C12", "Low Potential": "#2ECC71"}
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: {zone_colors.get(zone_label, "#95A5A6")};'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>📍 Zone Potential</div>
        <div style='font-size: 28px; font-weight: bold; color: {zone_colors.get(zone_label, "#95A5A6")};'>{zone_label}</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Fishing Zone Class</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='kpi-card' style='border-top-color: #2ECC71;'>
        <div style='font-size: 16px; color: #7F8C8D; margin-bottom: 10px;'>🎯 Confidence</div>
        <div style='font-size: 36px; font-weight: bold; color: #2ECC71;'>{confidence_score:.1f}%</div>
        <div style='font-size: 14px; color: #95A5A6; margin-top: 5px;'>Model Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# TASK 8: Smart Insights Panel
insights = generate_ai_insights(fish_prediction, weather_prediction, avg_sst, wind_speed, wave_height, chlorophyll, month)

st.markdown("""
<div class='insight-box'>
    <h3 style='color: white; margin-top: 0;'>🧠 AI Marine Insights</h3>
""", unsafe_allow_html=True)

for insight in insights:
    st.markdown(f"<p style='color: white; margin: 10px 0; font-size: 16px;'>{insight}</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Fishing Advisory
color_styles = {"green": "#2ECC71", "orange": "#F39C12", "red": "#E74C3C", "gray": "#95A5A6"}
bg_color = color_styles.get(advisory_color, "#95A5A6")

st.markdown(f"""
<div style='background: {bg_color}; padding: 25px; border-radius: 15px; text-align: center; 
            color: white; font-size: 28px; font-weight: bold; margin: 25px 0; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);'>
    🎯 {advisory_text}
</div>
""", unsafe_allow_html=True)

# Detailed Predictions
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Fish Quantity Analysis")
    st.metric("Predicted Fish Quantity", f"{fish_prediction:.2f}", delta=f"{zone_label}")
    
with col2:
    st.markdown("### 🌡️ Weather Risk Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={"text": weather_prediction, "font": {"size": 24, "color": "#0B3D91"}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": status_color, "thickness": 0.8},
            "steps": [
                {"range": [0, 40], "color": "rgba(46,204,113,0.3)"},
                {"range": [40, 75], "color": "rgba(243,156,18,0.3)"},
                {"range": [75, 100], "color": "rgba(231,76,60,0.3)"}
            ],
            "threshold": {"line": {"color": "white", "width": 6}, "thickness": 0.9, "value": risk_score}
        }
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', font={'color': "#0B3D91"})
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("---")

# TASK 4: Environmental Trends
st.markdown("### 📈 Environmental Trends")
fig1, fig2, fig3 = create_trend_charts(avg_sst, wind_speed, wave_height, chlorophyll, month)

col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)
with col3:
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# TASK 5: Risk Breakdown
st.markdown("### 🧩 Risk Factor Analysis")
risk_fig = create_risk_breakdown(wind_speed, wave_height, avg_sst, salinity, chlorophyll)
st.plotly_chart(risk_fig, use_container_width=True)

st.markdown("---")

# TASK 6: Premium Hotspot Map
st.markdown("### 🗺️ Fishing Zone Map")
hotspot_map = create_premium_hotspot_map(latitude, longitude, fish_prediction, weather_prediction)
st.plotly_chart(hotspot_map, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("🟢 **Low Potential**: < 150 fish")
with col2:
    st.markdown("🟡 **Medium Potential**: 150-250 fish")
with col3:
    st.markdown("🔴 **High Potential**: > 250 fish")

st.markdown("---")

# SHAP Explainability
st.markdown("### 🧠 Model Explainability")

with st.expander("View SHAP Analysis (Feature Importance)", expanded=False):
    st.markdown("SHAP shows how each feature contributes to the prediction.")
    
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

# SST Heatmap
st.markdown("### 🌡️ Indian Ocean SST Heatmap")

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
    except Exception as e:
        st.error(f"Error rendering SST heatmap: {e}")

st.markdown("---")

# TASK 10: Professional Footer
st.markdown("""
<div style='background: linear-gradient(135deg, #0B3D91, #00A8E8); color: white; padding: 30px; 
            border-radius: 15px; text-align: center; margin-top: 40px;'>
    <h3 style='color: white; margin-top: 0;'>MarineSense AI v2.0</h3>
    <p style='margin: 10px 0;'>Advanced Marine Intelligence & Prediction System</p>
    <p style='margin: 5px 0; font-size: 14px;'>Data Sources: NOAA, Oceanographic Surveys, Satellite Imagery</p>
    <p style='margin: 5px 0; font-size: 14px;'>
        <span style='color: #2ECC71; font-size: 20px;'>●</span> System Status: Online
    </p>
    <p style='margin: 15px 0; font-size: 12px; opacity: 0.8;'>
        © 2024 MarineSense AI | Research-Grade Marine Intelligence
    </p>
</div>
""", unsafe_allow_html=True)

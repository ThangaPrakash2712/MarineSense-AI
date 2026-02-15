import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Load trained models
fish_model = joblib.load("models/fish_prediction_model.pkl")
weather_model = joblib.load("models/weather_risk_model.pkl")

st.set_page_config(page_title="MarineSense AI", layout="wide")

st.title("🌊 MarineSense AI")
st.subheader("AI-Based Fish Prediction & Marine Weather Risk System")

st.markdown("---")

# Sidebar Inputs
st.sidebar.header("Enter Marine Conditions")

avg_sst = st.sidebar.slider("Sea Surface Temperature (°C)", 20.0, 35.0, 27.0)
wind_speed = st.sidebar.slider("Wind Speed (m/s)", 5.0, 25.0, 12.0)
wave_height = st.sidebar.slider("Wave Height (m)", 0.5, 4.0, 1.5)
salinity = st.sidebar.slider("Salinity (PSU)", 33.0, 36.0, 34.5)
chlorophyll = st.sidebar.slider("Chlorophyll (mg/m³)", 0.1, 2.0, 0.8)

# Prepare input
fish_input = pd.DataFrame([[
    avg_sst,
    wind_speed,
    wave_height,
    salinity,
    chlorophyll
]], columns=['avg_sst', 'wind_speed', 'wave_height', 'salinity', 'chlorophyll'])

weather_input = pd.DataFrame([[
    wind_speed,
    wave_height
]], columns=['wind_speed', 'wave_height'])

# Predict
fish_prediction = fish_model.predict(fish_input)[0]
weather_prediction = weather_model.predict(weather_input)[0]

# Convert risk category to numerical score
risk_mapping = {
    "Safe": 20,
    "Moderate": 60,
    "Dangerous": 90
}

risk_score = risk_mapping[weather_prediction]



st.markdown("---")
st.header("📊 Prediction Results")

col1, col2 = st.columns(2)

with col1:
    st.metric("🐟 Predicted Fish Quantity", f"{fish_prediction:.2f}")

with col2:
    st.subheader("🌪 Weather Risk Level")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={'text': weather_prediction},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "green"},
                {'range': [40, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "red"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)


st.markdown("---")

st.info("""
MarineSense AI uses machine learning models trained on sea surface temperature and environmental parameters 
to predict fish population and marine safety levels.
""")

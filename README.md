# 🌊 MarineSense AI v2.0

**AI-Based Fish Prediction & Marine Weather Risk System**

A production-ready, research-grade machine learning system for predicting fish aggregation and marine safety conditions.

---

## 🎯 Features

### Core Capabilities
- ✅ **Fish Quantity Prediction**: ML-based fish aggregation forecasting
- ✅ **Weather Risk Assessment**: Marine safety classification (Safe/Moderate/Dangerous)
- ✅ **Intelligent Fishing Advisory**: Clear recommendations for fishing operations
- ✅ **Hotspot Zone Mapping**: Interactive visualization of fishing potential zones
- ✅ **SST Heatmap**: Indian Ocean sea surface temperature visualization
- ✅ **Model Explainability**: SHAP-based feature importance analysis

### Advanced Features
- 🔧 **Feature Engineering Pipeline**: SST anomaly, wind-wave interaction, seasonal encoding
- 📍 **Location-Based Inputs**: Latitude/longitude coordinate support
- 📊 **Professional Dashboard**: Clean, intuitive UI with metric cards
- 🧠 **Explainable AI**: Understand model predictions with SHAP

---

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd MarineSense-AI
```

2. **Create virtual environment**
```bash
python -m venv marine_env
source marine_env/bin/activate  # On Windows: marine_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app/app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
MarineSense-AI/
├── app/
│   ├── app.py              # Main Streamlit application
│   └── utils_helper.py     # Helper functions and utilities
├── models/
│   ├── fish_prediction_model.pkl
│   └── weather_risk_model.pkl
├── data/
│   ├── processed/
│   │   ├── final_marine_dataset.csv
│   │   └── sst_indian_ocean.csv
│   └── raw/
├── notebooks/
│   ├── 01_data_analysis.ipynb
│   ├── 02_fish_model_training.ipynb
│   └── 03_weather_model_training.ipynb
├── sonar_detection/        # YOLOv7 integration (future)
├── src/                    # Source modules
├── requirements.txt
└── README.md
```

---

## 🎮 Usage Guide

### 1. Input Parameters

**Location:**
- Latitude: -90 to 90 (default: 10.0)
- Longitude: -180 to 180 (default: 75.0)

**Environmental Parameters:**
- Year: 2010-2035
- Month: 1-12
- Sea Surface Temperature: 20-35°C
- Wind Speed: 5-25 m/s
- Wave Height: 0.5-4.0 m
- Salinity: 33-36 PSU
- Chlorophyll: 0.1-2.0 mg/m³

### 2. Understanding Outputs

**Fish Prediction:**
- Numerical value representing fish quantity index
- Zone classification: Low (<150), Medium (150-250), High (>250)

**Weather Risk:**
- Safe: Ideal conditions for fishing
- Moderate: Proceed with caution
- Dangerous: Not recommended for fishing

**Fishing Advisory:**
- 🟢 Safe to Go Fishing
- 🟡 Go With Caution
- 🔴 Not Safe for Fishing

### 3. Interpreting Maps

**Hotspot Zone Map:**
- Shows selected location with color-coded potential
- Green: Low potential
- Yellow: Medium potential
- Red: High potential

**SST Heatmap:**
- Displays Indian Ocean temperature distribution
- Warmer colors = higher temperatures
- Helps identify thermal fronts and productive zones

---

## 🧠 Model Information

### Fish Prediction Model
- **Algorithm**: Random Forest Regressor
- **Features**: Year, Month, SST, Wind Speed, Wave Height, Salinity, Chlorophyll
- **Target**: Fish Quantity (continuous)

### Weather Risk Model
- **Algorithm**: Random Forest Classifier
- **Features**: Same as fish model
- **Target**: Risk Level (Safe/Moderate/Dangerous)

### Feature Engineering
- **SST Anomaly**: Deviation from mean temperature
- **Wind-Wave Interaction**: Product of wind speed and wave height
- **Seasonal Encoding**: Sin/cos transformation of month

---

## 📊 SHAP Explainability

The system uses SHAP (SHapley Additive exPlanations) to explain predictions:

- **Positive values**: Feature increases prediction
- **Negative values**: Feature decreases prediction
- **Magnitude**: Strength of feature impact

To view SHAP analysis, expand the "Model Explainability" section in the app.

---

## 🔮 Future Enhancements

### Planned Features (Hooks Ready)

1. **Sonar Fish Detection**
   - YOLOv7-based fish detection from sonar images
   - Real-time species classification
   - Integration with existing predictions

2. **Real-Time Weather API**
   - Live marine weather data
   - Automatic parameter updates
   - API integration (OpenWeatherMap, NOAA)

3. **Model Retraining Pipeline**
   - Automated retraining with new data
   - Performance monitoring
   - MLOps integration

4. **PDF Report Export**
   - Downloadable prediction reports
   - Historical analysis
   - Custom visualizations

---

## 🛠️ Technical Details

### Dependencies
- **Python**: 3.8+
- **Streamlit**: Web interface
- **Scikit-learn**: ML models
- **Plotly**: Interactive visualizations
- **Cartopy**: Geospatial mapping
- **SHAP**: Model explainability

### Performance
- **Model Loading**: Cached with `@st.cache_resource`
- **Data Loading**: Cached with `@st.cache_data`
- **SHAP Computation**: Cached to avoid recomputation

### Code Quality
- Modular architecture
- Error handling throughout
- Type hints and docstrings
- PEP 8 compliant
- Production-ready

---

## 📝 Data Sources

- **SST Data**: NOAA OISST (Optimum Interpolation Sea Surface Temperature)
- **Marine Parameters**: Synthetic/historical oceanographic data
- **Fish Data**: Historical catch records and surveys

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Authors

MarineSense AI Development Team

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- NOAA for SST data
- Streamlit for the amazing framework
- Scikit-learn for ML tools
- SHAP for explainability framework

---

**MarineSense AI v2.0** - Empowering sustainable fishing through AI 🐟🌊

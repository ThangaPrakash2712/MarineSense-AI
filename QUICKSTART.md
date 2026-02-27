# 🚀 MarineSense AI - Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- pip package manager
- 5GB free disk space

## Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd MarineSense-AI
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv marine_env
marine_env\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv marine_env
source marine_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If you encounter issues with cartopy, install it separately:
```bash
pip install cartopy --no-binary cartopy
```

### Step 4: Verify Installation
```bash
python -c "import streamlit; import pandas; import plotly; print('All dependencies installed!')"
```

### Step 5: Run the Application
```bash
streamlit run app/app.py
```

The app will automatically open in your browser at: `http://localhost:8501`

---

## First Time Usage

### 1. Default View
When you first open the app, you'll see:
- Default location: Latitude 10.0, Longitude 75.0 (Indian Ocean)
- Default environmental parameters
- Predictions based on default values

### 2. Adjust Parameters
Use the sidebar to modify:
- **Location**: Enter your target fishing coordinates
- **Environmental Data**: Adjust SST, wind speed, wave height, etc.
- **Time**: Select year and month

### 3. View Results
The app displays:
- **Dashboard Overview**: Quick metrics at the top
- **Fishing Advisory**: Color-coded recommendation card
- **Detailed Predictions**: Fish quantity and weather risk
- **Hotspot Map**: Interactive zone visualization
- **SST Heatmap**: Regional temperature distribution
- **SHAP Analysis**: Model explainability (expand section)

---

## Common Issues & Solutions

### Issue 1: Cartopy Installation Fails
**Solution:**
```bash
# Windows
conda install -c conda-forge cartopy

# Mac/Linux
pip install cartopy --no-binary cartopy
```

### Issue 2: Models Not Found
**Error:** "FileNotFoundError: models/fish_prediction_model.pkl"

**Solution:**
- Ensure you're in the MarineSense-AI directory
- Check that models/ folder contains .pkl files
- Run model training notebooks if models are missing

### Issue 3: SHAP Not Available
**Warning:** "SHAP library not installed"

**Solution:**
```bash
pip install shap
```

### Issue 4: Port Already in Use
**Error:** "Port 8501 is already in use"

**Solution:**
```bash
streamlit run app/app.py --server.port 8502
```

---

## Testing the App

### Test Case 1: Safe Conditions
Set these parameters:
- SST: 27°C
- Wind Speed: 10 m/s
- Wave Height: 1.0 m
- Chlorophyll: 0.9 mg/m³

**Expected:** Safe fishing advisory, moderate fish prediction

### Test Case 2: Dangerous Conditions
Set these parameters:
- Wind Speed: 22 m/s
- Wave Height: 3.5 m

**Expected:** Dangerous advisory, red warning card

### Test Case 3: High Fish Potential
Set these parameters:
- SST: 28°C
- Chlorophyll: 1.5 mg/m³
- Month: 3 or 4

**Expected:** High potential zone (red marker on map)

---

## Performance Tips

1. **First Load**: Initial load may take 10-15 seconds (model loading)
2. **Subsequent Predictions**: Instant (models are cached)
3. **SHAP Analysis**: May take 2-3 seconds on first computation
4. **Map Rendering**: SST heatmap may take 3-5 seconds

---

## Next Steps

1. ✅ Explore different parameter combinations
2. ✅ Check SHAP explainability for insights
3. ✅ Test various locations across the Indian Ocean
4. ✅ Compare predictions across different months
5. ✅ Review the README.md for advanced features

---

## Getting Help

- **Documentation**: See README.md
- **Configuration**: Edit config/config.json
- **Issues**: Check GitHub issues or create a new one

---

## Keyboard Shortcuts (Streamlit)

- `R`: Rerun the app
- `C`: Clear cache
- `S`: Open settings
- `?`: Show keyboard shortcuts

---

**You're all set! Happy fishing with MarineSense AI! 🐟🌊**

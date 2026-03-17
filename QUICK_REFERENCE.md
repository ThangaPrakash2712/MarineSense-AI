# 🚀 MarineSense AI v3.0 - Quick Reference Card

## ⚡ Quick Start (30 seconds)

```bash
# Install
pip install -r requirements.txt

# Run
streamlit run app/app.py

# Open browser
http://localhost:8501
```

---

## 🎮 Essential Controls

### Sidebar Toggles
- **🌐 Use Real-Time Ocean Data** - Fetch live marine conditions
- **📡 Enable Live Monitoring** - Auto-refresh dashboard
- **📍 Location Settings** - Set your coordinates
- **⛵ Boat Configuration** - Speed & fuel efficiency

### Quick Actions
- **🔄 Reset to Defaults** - Restore default settings
- **Refresh Interval Slider** - Adjust auto-refresh (1-30 min)

---

## 📊 Dashboard Sections (Top to Bottom)

1. **Hero Banner** - Status, timestamp, data source
2. **KPI Cards** - Fish, safety, distance, confidence
3. **Marine Advisory** - Professional guidance
4. **Route Map** - Navigation to optimal zone
5. **Trip Planning** - Fuel, time, distance
6. **Risk Gauge** - Weather safety assessment
7. **Current Conditions** - Environmental parameters
8. **SHAP Analysis** - Model explainability
9. **SST Heatmap** - Regional temperature map

---

## 🌐 Real-Time Mode

### How to Enable
1. Check "🌐 Use Real-Time Ocean Data"
2. Wait 5-10 seconds for data fetch
3. Manual sliders auto-disable
4. Data source shows "Real-Time"

### What It Does
- Fetches live SST, wind, waves
- Updates every refresh
- Falls back to manual if fails
- Free API (no key needed)

### When to Use
- Planning actual fishing trips
- Current condition monitoring
- Real-world decision making
- Live weather tracking

---

## 📡 Live Monitoring

### How to Enable
1. Install: `pip install streamlit-autorefresh`
2. Check "📡 Enable Live Monitoring"
3. Set refresh interval (default 5 min)
4. Green dot indicates LIVE mode

### What It Does
- Auto-refreshes dashboard
- Re-fetches real-time data
- Updates all predictions
- Continuous monitoring

### When to Use
- Long-term monitoring
- Weather watch
- Condition tracking
- Automated updates

---

## 🎯 Zone Finder

### How It Works
1. Searches 20 locations around you
2. Tests fish prediction for each
3. Recommends best zone
4. Shows confidence score

### Results
- **Best Zone Fish** - Predicted quantity
- **Confidence** - Accuracy estimate
- **Location** - Lat/Lon coordinates
- **Route** - Navigation path

### Performance
- First search: 5-10 seconds
- Cached: Instant (10 min)

---

## 🗺️ Route Map

### Features
- **Blue Circle** - Your location
- **Colored Star** - Fishing zone
- **Dashed Line** - Route
- **Tooltips** - Hover for details

### Colors
- 🔴 Red Star - High potential (>250 fish)
- 🟡 Yellow Star - Medium (150-250)
- 🟢 Green Star - Low (<150)

### Interactions
- Zoom in/out
- Pan around
- Hover markers
- Click legend

---

## ⛽ Fuel Estimation

### Inputs (Sidebar)
- **Boat Speed** - km/h
- **Fuel Efficiency** - L/km

### Outputs (Dashboard)
- **Fuel Required** - Liters
- **Travel Time** - Hours:Minutes
- **Total Distance** - Kilometers

### Formula
```
Fuel = Distance × Efficiency
Time = Distance / Speed
```

---

## 🧠 Marine Advisory

### Components
1. **Overall Rating** - Excellent/Good/Fair/Poor
2. **Safety Assessment** - Sailing conditions
3. **Fishing Opportunity** - Fish potential
4. **Distance Assessment** - Trip length
5. **Risk Explanation** - Key factors
6. **Recommended Action** - Go/Caution/Abort

### Action Colors
- 🟢 Green - PROCEED
- 🟡 Yellow - CAUTION
- 🔴 Red - ABORT

---

## 🔧 Troubleshooting

### Real-time not working?
- Check internet connection
- Verify coordinates valid
- System auto-falls back to manual

### Live monitoring unavailable?
```bash
pip install streamlit-autorefresh
```

### Slow performance?
- First zone search takes time
- Results cached for 10 minutes
- Subsequent searches instant

### API timeout?
- Automatic fallback to manual
- Check open-meteo.com status
- Increase timeout if needed

---

## 📱 Mobile Tips

- Use landscape mode
- Zoom for better view
- Sidebar auto-collapses
- All features work

---

## ⌨️ Keyboard Shortcuts

- **R** - Rerun app
- **C** - Clear cache
- **S** - Settings
- **?** - Help

---

## 🎯 Best Practices

### For Accuracy
✅ Use real-time data when available
✅ Verify coordinates carefully
✅ Configure boat parameters correctly
✅ Check advisory before departure

### For Performance
✅ Enable caching
✅ Use reasonable refresh intervals
✅ Close unused browser tabs
✅ Clear cache if issues

### For Safety
✅ Always check weather advisory
✅ Monitor conditions continuously
✅ Have backup plans
✅ Follow recommended actions

---

## 📞 Quick Help

### Installation Issues
See: QUICKSTART.md

### Feature Documentation
See: REALTIME_FEATURES.md

### Testing Guide
See: REALTIME_TESTING.md

### Deployment
See: DEPLOYMENT.md

---

## 🔢 Default Values

| Parameter | Default | Range |
|-----------|---------|-------|
| Latitude | 10.0 | -90 to 90 |
| Longitude | 75.0 | -180 to 180 |
| Year | 2024 | 2010-2035 |
| Month | 6 | 1-12 |
| SST | 27.0°C | 20-35 |
| Wind | 12.0 m/s | 5-25 |
| Wave | 1.5 m | 0.5-4.0 |
| Salinity | 34.5 PSU | 33-36 |
| Chlorophyll | 0.8 mg/m³ | 0.1-2.0 |
| Boat Speed | 20 km/h | 5-50 |
| Fuel Eff. | 0.8 L/km | 0.1-5.0 |

---

## 🎓 Pro Tips

💡 **Tip 1:** Enable real-time + live monitoring for continuous tracking

💡 **Tip 2:** Compare multiple locations by changing coordinates

💡 **Tip 3:** Use SHAP to understand what drives predictions

💡 **Tip 4:** Check SST heatmap for regional patterns

💡 **Tip 5:** Plan trips during favorable months (Mar-Apr, Oct-Nov)

💡 **Tip 6:** Cache results by keeping same inputs for 10 min

💡 **Tip 7:** Test offline mode before going to sea

💡 **Tip 8:** Screenshot advisory for reference

---

## 📊 Status Indicators

### Data Source
- **Real-Time** - Live API data
- **Manual** - User inputs
- **Manual (Fallback)** - API failed

### System Status
- **🟢 Online** - Normal mode
- **🟢 LIVE** - Auto-refresh active
- **🔴 Offline** - No internet

### Safety Status
- **Safe** - Green badge
- **Moderate** - Orange badge
- **Dangerous** - Red badge

---

## 🚀 Power User Commands

### Force Refresh
Press **R** in browser

### Clear All Cache
Press **C** in browser

### Reset Everything
Click "🔄 Reset to Defaults"

### Quick Test
1. Enable real-time
2. Enable live (1 min)
3. Watch auto-updates

---

## 📝 Quick Checklist

Before Fishing Trip:
- [ ] Set correct location
- [ ] Enable real-time data
- [ ] Check marine advisory
- [ ] Note fuel requirements
- [ ] Screenshot route map
- [ ] Verify safety status
- [ ] Check weather forecast
- [ ] Plan departure time

---

**MarineSense AI v3.0 - Your Real-Time Marine Intelligence Partner** 🌊🐟📡

**Need Help?** Check documentation files or contact support.

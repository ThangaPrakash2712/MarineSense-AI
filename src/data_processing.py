import pandas as pd
import numpy as np

# Load monthly SST
df = pd.read_csv("data/processed/sst_monthly_avg.csv")

np.random.seed(42)

# Generate realistic synthetic features

# Wind speed (m/s)
df['wind_speed'] = np.random.normal(loc=12, scale=3, size=len(df))

# Wave height (meters)
df['wave_height'] = np.random.normal(loc=1.5, scale=0.5, size=len(df))

# Salinity (PSU)
df['salinity'] = np.random.normal(loc=34.5, scale=0.3, size=len(df))

# Chlorophyll concentration (mg/m3)
df['chlorophyll'] = np.random.normal(loc=0.8, scale=0.2, size=len(df))

# Create fish quantity correlated with SST and chlorophyll
df['fish_quantity'] = (
    (df['avg_sst'] - 26) * 40 +       # temperature effect
    df['chlorophyll'] * 400 -         # strong food effect
    df['wave_height'] * 80 -          # rough sea reduces fish
    df['wind_speed'] * 5 +            # mild negative effect
    np.random.normal(0, 15, len(df))  # reduced noise
)

# Create weather risk classification

def classify_risk(row):
    if row['wave_height'] > 2.0 or row['wind_speed'] > 18:
        return "Dangerous"
    elif row['wave_height'] > 1.5 or row['wind_speed'] > 14:
        return "Moderate"
    else:
        return "Safe"

df['weather_risk'] = df.apply(classify_risk, axis=1)


# Save final dataset
df.to_csv("data/processed/final_marine_dataset.csv", index=False)

print("Final marine dataset created!")

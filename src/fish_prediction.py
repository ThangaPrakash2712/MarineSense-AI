import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("data/processed/final_marine_dataset.csv")

# Features & target
X = df[['avg_sst', 'wind_speed', 'wave_height', 'salinity', 'chlorophyll']]
y = df['fish_quantity']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Build pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestRegressor(random_state=42))
])

# Hyperparameter tuning
param_grid = {
    'model__n_estimators': [200, 500],
    'model__max_depth': [None, 10, 20],
    'model__min_samples_split': [2, 5]
}

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=5,
    scoring='r2',
    n_jobs=-1
)

# Train
grid_search.fit(X_train, y_train)

# Best model
best_model = grid_search.best_estimator_

# Predictions
y_pred = best_model.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Best Parameters:", grid_search.best_params_)
print("Test MSE:", mse)
print("Test R2 Score:", r2)

# Cross-validation score
cv_scores = cross_val_score(best_model, X, y, cv=5, scoring='r2')
print("Cross Validation R2 Scores:", cv_scores)
print("Average CV R2:", np.mean(cv_scores))

# Save model
joblib.dump(best_model, "models/fish_prediction_model.pkl")
print("Improved model saved successfully!")

import matplotlib.pyplot as plt

model = best_model.named_steps['model']
importances = model.feature_importances_
features = X.columns

plt.figure(figsize=(8,5))
plt.barh(features, importances)
plt.xlabel("Feature Importance")
plt.title("Feature Importance in Fish Prediction")
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt

plt.figure(figsize=(6,6))
plt.scatter(y_test, y_pred)
plt.xlabel("Actual Fish Quantity")
plt.ylabel("Predicted Fish Quantity")
plt.title("Actual vs Predicted Fish Quantity")
plt.plot([y_test.min(), y_test.max()],
         [y_test.min(), y_test.max()],
         color='red')  # perfect prediction line
plt.tight_layout()
plt.show()

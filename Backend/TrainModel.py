# train_model_with_history.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
import joblib

# List of CSV files to use for training
training_files = [
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Bold_v2_5_with_history.csv',
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Steadfast_v2_5_with_history.csv',
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Courageous_v2_5_with_history.csv',
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Ruthless_v2_5_with_history.csv',
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Valiant_v2_5_with_history.csv',
    f'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Resolute_v2_5_with_history.csv'
]

# Combine data from all files
dataframes = [pd.read_csv(file) for file in training_files]
data = pd.concat(dataframes, ignore_index=True)

# Add historical features
data['Instantaneous_t-1'] = data['Inj Gas Meter Volume Instantaneous'].shift(1)
data['Instantaneous_t-2'] = data['Inj Gas Meter Volume Instantaneous'].shift(2)
data['Valve_t-1'] = data['Inj Gas Valve Percent Open'].shift(1)
data['Valve_t-2'] = data['Inj Gas Valve Percent Open'].shift(2)

# Drop rows with NaN values introduced by shifting
data = data.dropna().reset_index(drop=True)

# Prepare features and target
X = data[['Inj Gas Meter Volume Instantaneous', 'Inj Gas Meter Volume Setpoint',
          'Inj Gas Valve Percent Open', 'Instantaneous_t-1', 'Instantaneous_t-2',
          'Valve_t-1', 'Valve_t-2']].apply(pd.to_numeric, errors='coerce')
y = data['IsHydrate']

# Handle missing values and scale features
X.fillna(X.mean(), inplace=True)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Train the Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight={0: 1, 1: 15})
rf_model.fit(X_scaled, y)

# Save the trained model and scaler
joblib.dump(rf_model, "trained_rf_model_with_history.pkl")
joblib.dump(scaler, "scaler_with_history.pkl")

print("Training completed with historical features. Model and scaler saved successfully.")

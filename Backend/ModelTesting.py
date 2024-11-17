# test_model_with_history.py

import pandas as pd
import joblib

# Load the trained model and scaler
rf_model = joblib.load("trained_rf_model_with_history.pkl")
scaler = joblib.load("scaler_with_history.pkl")

# Specify the test file
test_file = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Fearless_v2_5_with_history.csv'

# Load the test data
test_data = pd.read_csv(test_file)

# Add historical features
test_data['Instantaneous_t-1'] = test_data['Inj Gas Meter Volume Instantaneous'].shift(1)
test_data['Instantaneous_t-2'] = test_data['Inj Gas Meter Volume Instantaneous'].shift(2)
test_data['Valve_t-1'] = test_data['Inj Gas Valve Percent Open'].shift(1)
test_data['Valve_t-2'] = test_data['Inj Gas Valve Percent Open'].shift(2)

# Drop rows with NaN values introduced by shifting
test_data = test_data.dropna().reset_index(drop=True)

# Prepare features for prediction
X_t = test_data[['Inj Gas Meter Volume Instantaneous', 'Inj Gas Meter Volume Setpoint',
                 'Inj Gas Valve Percent Open', 'Instantaneous_t-1', 'Instantaneous_t-2',
                 'Valve_t-1', 'Valve_t-2']].apply(pd.to_numeric, errors='coerce')
X_t.fillna(X_t.mean(), inplace=True)

# Scale features using the loaded scaler
X_t_scaled = scaler.transform(X_t)

# Predict confidence scores
confidence_scores = rf_model.predict_proba(X_t_scaled)[:, 1]

# Add confidence scores to the test dataset
test_data['Confidence_Score'] = confidence_scores
test_data['Confidence_Score'] = test_data['Confidence_Score'].shift(-1)
average_confidence = test_data['Confidence_Score'].mean()

# Save the modified test dataset
output_file = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/Fearless_v3_with_history.csv'
test_data.to_csv(output_file, index=False)

print(f"Confidence scores with historical features added and saved to {output_file}.")
print(average_confidence)

import pandas as pd
import joblib
import os
from pathlib import Path


def test_model_with_history(name ,file_path, output_path):
    """
    Process the given CSV file, predict confidence scores using the trained model with historical features, 
    and save the updated file with predictions.

    Args:
        file_path (str): Path to the input CSV file.

    Returns:
        str: Path to the processed CSV file with confidence scores.
    """
    # Load the trained model and scaler
    model_path = str(Path("C:/Users/noele/Documents/GitHub/HackUTD2024/trained_rf_model_with_history.pkl").expanduser())
    model_scalar = str(Path("C:/Users/noele/Documents/GitHub/HackUTD2024/scaler_with_history.pkl").expanduser())
    rf_model = joblib.load(model_path)
    scaler = joblib.load(model_scalar)

    # Load the test data
    test_data = pd.read_csv(file_path)

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
    test_data['Confidence_Score'] = test_data['Confidence_Score'].shift(-1)  # Shift confidence score up by one row
    average_confidence = test_data['Confidence_Score'].mean()

    # Generate output file path
    base_name, ext = os.path.splitext(file_path)
    output_file = output_path

    # Save the modified dataset
    test_data.to_csv(output_file, index=False)

    # Print confirmation messages
    print(f"Confidence scores with historical features added and saved to {output_file}.")
    print(f"Average confidence score: {average_confidence:.4f}")

    # Return the path to the processed file
    return average_confidence



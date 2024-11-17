import pandas as pd
import os

def process_csv2(file_path):

    # Load the CSV file
    data = pd.read_csv(file_path)

    # Initial count of rows where IsHydrate is 0
    initial_zeros_count = (data['IsHydrate'] == 0).sum()

    # Iterate through rows and apply the condition
    changed_count = 0
    for i in range(1, len(data)):
        if data.loc[i - 1, 'Inj Gas Meter Volume Instantaneous'] > data.loc[i, 'Inj Gas Meter Volume Instantaneous']:
            if data.loc[i - 1, 'Inj Gas Valve Percent Open'] <= data.loc[i, 'Inj Gas Valve Percent Open']:
                if data.loc[i, 'IsHydrate'] == 0:  # Change only if it's 0
                    data.loc[i, 'IsHydrate'] = 1
                    changed_count += 1

    # Add historical features
    data['Instantaneous_t-1'] = data['Inj Gas Meter Volume Instantaneous'].shift(1)
    data['Instantaneous_t-2'] = data['Inj Gas Meter Volume Instantaneous'].shift(2)
    data['Valve_t-1'] = data['Inj Gas Valve Percent Open'].shift(1)
    data['Valve_t-2'] = data['Inj Gas Valve Percent Open'].shift(2)

    # Drop rows with NaN values introduced by shifting
    data = data.dropna().reset_index(drop=True)

    # Simulate adding Confidence_Score for demonstration (replace with actual model output in real usage)
    data['Confidence_Score'] = 0.5  # Placeholder values
    data['Confidence_Score'] = data['Confidence_Score'].shift(-1)  # Shift confidence score up by one row

    # Generate output file path in the same directory as the input file
    base_name, ext = os.path.splitext(file_path)
    output_path = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_vf2.csv'

    # Save the modified dataset
    data.to_csv(output_path, index=False)

    # Final counts for reporting (optional)
    final_zeros_count = (data['IsHydrate'] == 0).sum()
    total_changes = initial_zeros_count - final_zeros_count

    print(f"Modified CSV saved to {output_path}")
    print(f"Total 'IsHydrate' values changed: {total_changes}")
    print(f"Changed count during loop: {changed_count}")

    return output_path



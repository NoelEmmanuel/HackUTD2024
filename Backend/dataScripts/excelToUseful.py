import pandas as pd

def process_csv(file_path, output_path):
    # Load the dataset
    data = pd.read_csv(file_path)
    
    # Convert 'Time' column to datetime
    data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

    
    # Save the processed data to a new file
    data.to_csv(output_path, index=False)
    print(f"Processed file saved to: {output_path}")

# File paths
input_file = r"C:\Users\ramgu\Downloads\Valiant_v2.csv"
output_file = r'C:\Users\ramgu\OneDrive\Desktop\HydraSense\HackUTD2024-1\Backend\Datasets\Valiant_v2.csv'

# Process the file
process_csv(input_file, output_file)

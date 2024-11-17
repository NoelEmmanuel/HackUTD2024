import pandas as pd

def process_csv(file_path, output_path):
    # Load the dataset
    data = pd.read_csv(file_path)
    
    # Convert 'Time' column to datetime
    data['Time'] = pd.to_datetime(data['Time'],format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    
    #This is whether the hydrate is forming or not (manually input)
    # data['IsHydrate'] = 0

    # Drop the original 'Time' column (optional)
    # data = data.drop(columns=['Time'])
    
    # Handle missing data
    # For numeric columns, fill missing values with column meanS
    for col in data.select_dtypes(include=['float64', 'int64']).columns:
        data[col] = data[col].fillna(data[col].mean())
    
    # Save the processed data to a new file
    data.to_csv(output_path, index=False)
    print(f"Processed file saved to: {output_path}")

# # File paths
# input_file = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Bold_744H-10_31-11_07.csv'
# output_file = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Boldv2.csv'

# # Process the file
# process_csv(input_file, output_file)

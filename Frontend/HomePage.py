import sys
import os

# Add the parent directory of Backend to sys.path
parent_dir = os.path.abspath("C:/Users/noele/Documents/GitHub/HackUTD2024")
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import streamlit as st
import pandas as pd
import time
import plotly.graph_objs as go
import importlib.util
from Backend import csvToUsable

# Title of the app
st.title("Live Data Streaming with Single File Upload and External Script Call")

# Streamlit slider for chunk size
chunk_size = st.slider(
    "Select the number of rows to process at a time",
    min_value=1,
    max_value=25,
    value=10,
    step=1
)

# Slider for max number of entries to display
max_entries = st.slider(
    "Select the maximum number of data points to display in the graph",
    min_value=10,
    max_value=100,
    value=20,
    step=10
)

# Threshold slider
threshold = st.slider("Set Confidence Score Threshold", min_value=0.0, max_value=1.0, value=0.7, step=0.01)

# Initialize session state
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}
if 'current_indices' not in st.session_state:
    st.session_state.current_indices = {}
if 'run' not in st.session_state:
    st.session_state.run = False

# External script path
external_script_path = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/csvToUsable.py'

# File uploader for a single CSV file
uploaded_file = st.file_uploader(
    "Upload a single CSV file",
    type=["csv"],
    accept_multiple_files=False
)

# Process the uploaded file
if uploaded_file:
    # Save uploaded file to a temporary location
    temp_file_path = os.path.join('C:/Users/noele/Documents/GitHub/HackUTD2024/Backend', uploaded_file.name)
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
    print(uploaded_file.name)
    average = csvToUsable.process_uploaded_file(uploaded_file.name, temp_file_path)

    # Call the external script
    temp_file_path = 'C:/Users/noele/Documents/GitHub/HackUTD2024/Backend/Datasets/{name}_FINAL.csv'

    # Load data
    print(temp_file_path)
    data = pd.read_csv(temp_file_path)

    # Ensure the selected columns exist in the dataset
    required_columns = ['Time', 'Inj Gas Meter Volume Instantaneous', 'Confidence_Score']
    if not all(col in data.columns for col in required_columns):
        st.error(
            f"The file '{uploaded_file.name}' must contain the following columns: {', '.join(required_columns)}"
        )
    else:
        # Filter for the required columns
        data = data[required_columns]

        # Convert 'Time' column to datetime for better plotting
        data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

        # Store data in session state
        st.session_state.file_data[uploaded_file.name] = data
        st.session_state.current_indices[uploaded_file.name] = 0

        # Confirm file upload
        st.success(f"File '{uploaded_file.name}' has been uploaded and processed.")

# Start/Stop button
if st.button('Start/Stop Data Streaming'):
    st.session_state.run = not st.session_state.run

if st.session_state.file_data:
    # Layout to organize multiple graphs
    max_columns = 2  # Maximum number of graphs per row
    col_index = 0    # To track column position in the current row
    cols = st.columns(max_columns)  # Create initial column placeholders

    # Dictionary to hold graph placeholders
    graph_placeholders = {}

    # Display graphs for each uploaded file
    for file_name, data in st.session_state.file_data.items():
        current_index = st.session_state.current_indices[file_name]

        # Create new row of columns if the current row is full
        if col_index == 0:
            cols = st.columns(max_columns)

        # Assign each graph to a column in the row
        with cols[col_index]:
            st.subheader(f"Live Graph for: {file_name}")
            graph_placeholder = st.empty()  # Create a unique placeholder for each graph
            graph_placeholders[file_name] = graph_placeholder

        # Update column index and wrap to the next row if needed
        col_index += 1
        if col_index >= max_columns:
            col_index = 0

    # Continuous update while `st.session_state.run` is True
    while st.session_state.run:
        for file_name, data in st.session_state.file_data.items():
            current_index = st.session_state.current_indices[file_name]
            next_index = current_index + chunk_size
            next_index = min(next_index, len(data))  # Stop at the end

            # Update session state
            st.session_state.current_indices[file_name] = next_index

            # Subset data for the graph
            chunk_data = data.iloc[:next_index].tail(max_entries)

            # Plot using Plotly
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=chunk_data["Time"],
                    y=chunk_data["Inj Gas Meter Volume Instantaneous"],
                    mode="lines",
                    line=dict(color="blue"),
                )
            )

            exceeded_points = chunk_data[chunk_data['Confidence_Score'] > threshold]
            if not exceeded_points.empty:
                fig.add_trace(
                    go.Scatter(
                        x=exceeded_points["Time"],
                        y=exceeded_points["Inj Gas Meter Volume Instantaneous"],
                        mode="markers",
                        marker=dict(color="red", size=10),
                    )
                )

            fig.update_layout(
                title="Inj Gas Volume vs Time with Threshold Markers",
                xaxis_title="Time",
                yaxis_title="Inj Gas Meter Volume Instantaneous",
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                showlegend=False,
            )

            # Update the graph
            graph_placeholders[file_name].plotly_chart(fig, use_container_width=True, key=f"{file_name}_{current_index}")

        time.sleep(1.0)  # Simulate real-time streaming
else:
    st.write("Please upload a CSV file to begin.")

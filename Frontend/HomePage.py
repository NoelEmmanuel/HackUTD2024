import streamlit as st
import pandas as pd
import time
import plotly.graph_objs as go
from Samba import check_hydrate_formation

# Title of the app
st.title("Simultaneous Live Data Streaming with Threshold Markers and Start/Stop Feature")

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
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'file_data' not in st.session_state:
    st.session_state.file_data = {}
if 'current_indices' not in st.session_state:
    st.session_state.current_indices = {}
if 'run' not in st.session_state:
    st.session_state.run = False
if 'confidence_sum' not in st.session_state:
    st.session_state.confidence_sum = {}
if 'confidence_count' not in st.session_state:
    st.session_state.confidence_count = {}
if 'highest_confidence' not in st.session_state:
    st.session_state.highest_confidence = {}

# File uploaders for multiple CSV files
uploaded_files = st.file_uploader(
    "Upload your CSV files",
    type=["csv"],
    accept_multiple_files=True
)

# If new files are uploaded, update session state
if uploaded_files:
    new_files = [
        file for file in uploaded_files if file not in st.session_state.uploaded_files
    ]
    if new_files:
        for file in new_files:
            # Load data
            data = pd.read_csv(file)

            # Ensure the selected columns exist in the dataset
            required_columns = ['Time', 'Inj Gas Meter Volume Instantaneous', 'Confidence_Score']
            if not all(col in data.columns for col in required_columns):
                st.error(
                    f"The file '{file.name}' must contain the following columns: {', '.join(required_columns)}"
                )
                continue

            # Filter for the required columns
            data = data[required_columns]

            # Convert 'Time' column to datetime for better plotting
            data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

            # Store data in session state
            st.session_state.file_data[file.name] = data
            st.session_state.current_indices[file.name] = 0

        # Update the list of uploaded files
        st.session_state.uploaded_files = uploaded_files

# Start/Stop button
if st.button('Start/Stop Data Streaming'):
    st.session_state.run = not st.session_state.run

if st.session_state.uploaded_files:
    # Layout to organize multiple graphs
    max_columns = 2  # Maximum number of graphs per row
    col_index = 0    # To track column position in the current row
    cols = st.columns(max_columns)  # Create initial column placeholders

    # Dictionary to hold graph placeholders
    graph_placeholders = {}

    # Display graphs for each uploaded file
    for idx, file in enumerate(st.session_state.uploaded_files):
        file_name = file.name

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

    # For each file, display/update the graph
    for file_name in st.session_state.file_data:
        data = st.session_state.file_data[file_name]
        current_index = st.session_state.current_indices[file_name]

        if st.session_state.run:
            # Update the current index
            next_index = current_index + chunk_size
            if next_index >= len(data):
                next_index = len(data)  # Stop at the end
            st.session_state.current_indices[file_name] = next_index
        else:
            next_index = current_index  # Keep current index when paused

        # Subset the data up to the current index
        chunk_data = data.iloc[:next_index]

        # Limit to the last max_entries data points
        chunk_data = chunk_data.tail(max_entries)

        # **Update Running Metrics**
        if file_name not in st.session_state.confidence_sum:
            # Initialize for each file
            st.session_state.confidence_sum[file_name] = 0
            st.session_state.confidence_count[file_name] = 0
            st.session_state.highest_confidence[file_name] = 0

        # Get current confidence score (from current chunk)
        if not chunk_data.empty:
            current_confidence = chunk_data['Confidence_Score'].iloc[-1]
        
            # Update running sum and count
            st.session_state.confidence_sum[file_name] += chunk_data['Confidence_Score'].sum()
            st.session_state.confidence_count[file_name] += len(chunk_data)

            # Calculate Metrics
            if st.session_state.confidence_count[file_name] > 0:
                average_confidence = st.session_state.confidence_sum[file_name] / st.session_state.confidence_count[file_name]
                
                # Update highest confidence score
                max_confidence_in_chunk = chunk_data['Confidence_Score'].max()
                st.session_state.highest_confidence[file_name] = max(
                    st.session_state.highest_confidence[file_name],
                    max_confidence_in_chunk
                )
                highest_confidence = st.session_state.highest_confidence[file_name]

                # Check if current confidence exceeds average/highest ratio
                if highest_confidence > 0 and current_confidence > (average_confidence / highest_confidence):
                    hydrate_status = check_hydrate_formation(current_confidence)
                    st.warning(f"Hydrate Formation Alert for {file_name}: {hydrate_status}")

        # Plot using Plotly with threshold markers
        exceeded_points = chunk_data[chunk_data['Confidence_Score'] > threshold]
        fig = go.Figure()

        # Add the main line chart
        fig.add_trace(
            go.Scatter(
                x=chunk_data["Time"],
                y=chunk_data["Inj Gas Meter Volume Instantaneous"],
                mode="lines",
                line=dict(color="blue"),
            )
        )

        # Add red markers for threshold exceedances
        if not exceeded_points.empty:
            fig.add_trace(
                go.Scatter(
                    x=exceeded_points["Time"],
                    y=exceeded_points["Inj Gas Meter Volume Instantaneous"],
                    mode="markers",
                    marker=dict(color="red", size=10, symbol="circle"),
                )
            )

        fig.update_layout(
            title="Inj Gas Volume vs Time with Threshold Markers",
            xaxis_title="Time",
            yaxis_title="Inj Gas Meter Volume Instantaneous",
            height=300,  # Reduced height to make graphs more compact
            margin=dict(l=20, r=20, t=30, b=20),  # Adjusted margins for a cleaner layout
            showlegend=False,  # Remove legend
        )

        # Update the graph with a unique key
        graph_placeholders[file_name].plotly_chart(fig, use_container_width=True, key=file_name)

    if st.session_state.run:
        # Pause for a short duration to simulate real-time updates
        time.sleep(1.0)
        st.rerun()
    else:
        st.write("Click 'Start/Stop Data Streaming' to resume or pause the live graphs.")
else:
    st.write("Please upload CSV files to begin.")

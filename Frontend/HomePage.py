import streamlit as st
import pandas as pd
import asyncio


async def live_stream_graph(data, chunk_size, graph_placeholder):
    """
    Asynchronous function to live stream data from a dataframe and update a graph dynamically.

    Args:
        data (pd.DataFrame): The dataframe to display.
        chunk_size (int): Number of rows to display per update.
        graph_placeholder (st.delta_generator.DeltaGenerator): Streamlit placeholder for the graph.
    """
    # Simulate live streaming
    for i in range(0, len(data), chunk_size):
        # Subset the data for the current chunk
        chunk_data = data.iloc[:i + chunk_size]

        # Display the graph dynamically
        graph_placeholder.line_chart(chunk_data.set_index('Time'))

        # Pause for a short duration to simulate real-time updates
        await asyncio.sleep(1.0)


async def main():
    # Title of the app
    st.title("Simultaneous Live Data Streaming for Multiple CSV Files")

    # Streamlit slider for chunk size
    chunk_size = st.slider("Select the number of rows to process at a time", min_value=1, max_value=50, value=10, step=1)


    # File uploaders for multiple CSV files
    uploaded_files = st.file_uploader("Upload your CSV files", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        # Layout to organize multiple graphs
        max_columns = 3  # Maximum number of graphs per row
        col_index = 0    # To track column position in the current row
        cols = st.columns(max_columns)  # Create initial column placeholders

        # Tasks to handle all graphs asynchronously
        tasks = []

        for idx, file in enumerate(uploaded_files):
            # Load data
            data = pd.read_csv(file)

            # Ensure the selected columns exist in the dataset
            required_columns = ['Time', 'Inj Gas Meter Volume Instantaneous']
            if not all(col in data.columns for col in required_columns):
                st.error(f"The file '{file.name}' must contain the following columns: {', '.join(required_columns)}")
                continue

            # Filter for the required columns
            data = data[required_columns]

            # Convert 'Time' column to datetime for better plotting
            data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

            # Create new row of columns if the current row is full
            if col_index == 0:
                cols = st.columns(max_columns)

            # Assign each graph to a column in the row
            with cols[col_index]:
                st.subheader(f"Live Graph for: {file.name}")
                graph_placeholder = st.empty()  # Create a unique placeholder for each graph

                # Schedule an asynchronous task for the graph
                tasks.append(live_stream_graph(data, chunk_size, graph_placeholder))

            # Update column index and wrap to the next row if needed
            col_index += 1
            if col_index >= max_columns:
                col_index = 0

        # Run all graph tasks simultaneously
        await asyncio.gather(*tasks)


# Run the Streamlit app
if __name__ == "__main__":
    asyncio.run(main())

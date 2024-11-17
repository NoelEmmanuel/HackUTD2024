import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import matplotlib.dates as mdates
import streamlit.components.v1 as components


import streamlit as st

# Define status emojis
status_emojis = {
    'green': '🟢',
    'yellow': '🟡',
    'red': '🔴',
}

# Main menu options with their statuses
menu_options = {
    'Home': 'green',
    'Wells': 'yellow',
}

# Wells and their statuses
wells = ['Well A', 'Well B', 'Well C']
wells_status = {
    'Well A': 'green',
    'Well B': 'green',
    'Well C': 'red',
}

# Create main menu with status emojis
menu_labels = [f"{status_emojis[status]} {name}" for name, status in menu_options.items()]
selected_main = st.sidebar.radio("Main Menu", menu_labels)
selected_main = selected_main.split(' ', 1)[1]  # Remove the emoji to get the actual name

# Handle navigation
if selected_main == 'Home':
    st.write("Welcome to the Home page.")
elif selected_main == 'Wells':
    # Create wells dropdown with status emojis
    well_labels = [f"{status_emojis[wells_status[well]]} {well}" for well in wells]
    selected_well = st.sidebar.selectbox("Select a Well", well_labels)
    selected_well = selected_well.split(' ', 1)[1]  # Remove the emoji
    st.write(f"You selected {selected_well}")

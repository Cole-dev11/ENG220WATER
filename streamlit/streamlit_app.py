import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="New Mexico Interactive Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. Main Page Content ---
st.title("Interactive Map of New Mexico 🗺️")
st.write("This map is now constrained to the state's borders. You can't pan away!")

# --- 3. Folium Map Creation ---

# Define the bounding box for New Mexico
# [south_lat, west_lon], [north_lat, east_lon]
nm_bounds_sw = [31.33, -109.05]  # Southwest corner
nm_bounds_ne = [37.0, -103.0]    # Northeast corner

# Create a Folium map object
m = folium.Map(
    # We don't need location/zoom_start, we will use fit_bounds()
    max_bounds=[nm_bounds_sw, nm_bounds_ne],  # *** This is the key change ***
    min_zoom=7,  # Set a minimum zoom to prevent zooming out too far
    max_zoom=18
)

# Fit the map to the bounds we defined
# This ensures the entire state is visible on load
m.fit_bounds([nm_bounds_sw, nm_bounds_ne])


# --- 4. Display Map in Streamlit ---
st_folium(m, use_container_width=True, height=500)


# --- 5. Example Components (For your reference) ---

# --- Sidebar ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

# --- Columns ---
col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above is now restricted to the New Mexico state boundaries.")

with col2:
    st.header("Next Steps")
    st.write("You can add markers, popups, and more using Folium's functions.")
import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 1. Set Page Configuration ---
# This must be the first Streamlit command in your script.
st.set_page_config(
    page_title="New Mexico Interactive Map",  # Title shown in browser tab
    page_icon="🗺️",                         # Icon shown in browser tab
    layout="wide",                           # 'wide' or 'centered'
    initial_sidebar_state="auto"             # 'auto', 'expanded', or 'collapsed'
)

# --- 2. Main Page Content ---
st.title("Interactive Map of New Mexico 🗺️")
st.write("This map is fully interactive. You can zoom, pan, and click.")

# --- 3. Folium Map Creation ---

# Center coordinates for New Mexico
nm_lat = 34.5
nm_lon = -106.0
nm_zoom = 7  # Folium's zoom scale is slightly different from other platforms

# Create a Folium map object
m = folium.Map(location=[nm_lat, nm_lon], zoom_start=nm_zoom)

# --- 4. Display Map in Streamlit ---
# Use st_folium to render the map
# 'use_container_width=True' makes it fill the space (if layout is "wide")
# 'height=500' sets a fixed height
st_folium(m, use_container_width=True, height=500)


# --- 5. Example Components (For your reference) ---

# --- Sidebar ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")
# Example:
# add_marker = st.sidebar.checkbox("Add a marker to Albuquerque")

# if add_marker:
#     folium.Marker(
#         location=[35.0844, -106.6504],
#         popup="Albuquerque",
#         tooltip="Click for more info"
#     ).add_to(m)
#
#     # Need to re-render the map if you change it
#     st_folium(m, use_container_width=True, height=500, key="map_with_marker")


# --- Columns ---
col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above is centered on New Mexico.")

with col2:
    st.header("Next Steps")
    st.write("You can add markers, popups, and more using Folium's functions.")




    
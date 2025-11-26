import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="US States Interactive Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. Main Page Content ---
st.title("Interactive Map of US States 🗺️")
st.write("This map is fully interactive. You can zoom, pan, and click on a state.")

# --- Load Local GeoJSON File ---
file_path = "data/us_states.json"
try:
    with open(file_path, "r") as f:
        us_state_data = json.load(f) 
except FileNotFoundError:
    st.error(f"Error: GeoJSON file not found at '{file_path}'.")
    st.stop()
except json.JSONDecodeError:
    st.error(f"Error: Could not read or decode the GeoJSON file.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading the file: {e}")
    st.stop()


# --- 3. Folium Map Creation ---
us_lat = 39.8283
us_lon = -98.5795
us_zoom = 4

m = folium.Map(location=[us_lat, us_lon], zoom_start=us_zoom)

# --- Add State Outlines (from local data) ---

folium.GeoJson(
    us_state_data, 
    name="US States",
    
    style_function=lambda feature: {
        'fillColor': '#4682B4', 
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3,
    },
    
    highlight_function=lambda x: {
        'weight': 3,
        'color': '#FF4500', 
        'fillOpacity': 0.6,
    },
    
    tooltip=folium.features.GeoJsonTooltip(
        # CONFIRMED FIELD: 'name' is correct
        fields=['name'],     
        aliases=['State:'],   
        sticky=True
    )
).add_to(m)

# --- 4. Display Map and Capture Clicks ---
st.write("Click on a state to see its name below.")
map_data = st_folium(
    m,
    use_container_width=True,
    height=500,
    returned_objects=["last_object_clicked"]
)

# --- 5. Handle Click Data ---
st.header("Click Information")

if map_data.get("last_object_clicked"):
    # Since we confirmed 'name' is the key in the GeoJSON, we use it directly.
    try:
        # Extract the state name using the confirmed 'name' key
        state_name = map_data["last_object_clicked"]["properties"]["name"]
        st.success(f"You clicked on the state: **{state_name}**!")
    except KeyError:
        # A more specific error now that we know the property should be 'name'
        st.warning("Click detected, but the 'name' property was not found in the clicked GeoJSON feature. Try clicking the center of a larger state.")
else:
    st.info("No state clicked yet.")


# --- 6. Other Page Components ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above shows the outline of all US states.")

with col2:
    st.header("Next Steps")
    st.write("You can use the clicked state name to show specific state-level data.")
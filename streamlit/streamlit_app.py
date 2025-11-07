import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="New Mexico Water Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. Main Page Content ---
st.title("New Mexico Water Map")
st.write("This map is fully interactive. You can zoom, pan, and click on a county.")

# --- Load Local GeoJSON File ---
file_path = "streamlit/tl_2010_35_county10.geojson"
try:
    with open(file_path, "r", encoding="latin-1") as f:
        nm_county_data = json.load(f)
        
except FileNotFoundError:
    st.error(f"Error: GeoJSON file not found at '{file_path}'.")
    st.error("Please make sure the file is in the same directory as your script.")
    st.stop()
except json.JSONDecodeError:
    st.error(f"Error: Could not read or decode the GeoJSON file.")
    st.error("Please ensure the file is a valid GeoJSON.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while loading the file: {e}")
    st.stop()


# --- 3. Folium Map Creation ---
nm_lat = 34.5
nm_lon = -106.0
nm_zoom = 7

m = folium.Map(location=[nm_lat, nm_lon], zoom_start=nm_zoom)

# --- Add County Outlines (from local data) ---
folium.GeoJson(
    nm_county_data,
    name="New Mexico Counties",
    
    style_function=lambda feature: {
        'fillColor': '#FFFF00',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3,
    },
    
    highlight_function=lambda x: {
        'weight': 3,
        'color': '#FF0000',
        'fillOpacity': 0.6,
    },
    
    tooltip=folium.features.GeoJsonTooltip(
        fields=['NAMELSAD10'],
        aliases=['County:'],
        sticky=True
    )
).add_to(m)

# --- 4. Display Map ---
st_folium(
    m,
    use_container_width=True,
    height=500
)

# --- 5. Other Page Components (Sidebar) ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

# --- MOVED TO SIDEBAR ---
st.sidebar.header("Map Info")
st.sidebar.write("The map above shows all counties in New Mexico.")

st.sidebar.header("Next Steps")
st.sidebar.write("You can use the clicked county name to show specific data.")

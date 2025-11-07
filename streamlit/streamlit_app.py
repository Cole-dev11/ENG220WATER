import streamlit as st
import folium
from streamlit_folium import st_folium
import json

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="New Mexico Interactive Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

## UPDATED: Initialize session state to store the clicked county
if "clicked_county" not in st.session_state:
    st.session_state.clicked_county = None

# --- 2. Main Page Content ---
st.title("Interactive Map of New Mexico 🗺️")
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

## UPDATED: Define style functions based on session state
def get_style(feature):
    """
    Styles each feature based on whether it is 'clicked' 
    (i.e., its name is in st.session_state.clicked_county).
    """
    if feature['properties']['NAMELSAD10'] == st.session_state.clicked_county:
        # Style for the SELECTED county
        return {
            'fillColor': '#FFFF00',
            'color': 'black',      # Black outline
            'weight': 3,           # Thicker outline
            'fillOpacity': 0.6,
        }
    else:
        # Default style for all OTHER counties
        return {
            'fillColor': '#FFFF00',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.3,
        }

# This is the HOVER style (your original red line)
highlight_function = lambda x: {
    'weight': 3,
    'color': '#FF0000',
    'fillOpacity': 0.6,
}

# --- Add County Outlines (from local data) ---
folium.GeoJson(
    nm_county_data,
    name="New Mexico Counties",
    
    ## UPDATED: Use the new conditional style function
    style_function=get_style,
    
    ## UPDATED: Keep the red hover function
    highlight_function=highlight_function,
    
    tooltip=folium.features.GeoJsonTooltip(
        fields=['NAMELSAD10'],
        aliases=['County:'],
        sticky=True
    )
).add_to(m)

# --- 4. Display Map and Capture Clicks ---
st.write("Click on a county to see its name below.")
map_data = st_folium(
    m,
    use_container_width=True,
    height=500,
    returned_objects=["last_object_clicked"]
)

# --- 5. Handle Click Data ---
st.header("Click Information")

## UPDATED: Update session state based on the click
if map_data.get("last_object_clicked"):
    try:
        county_name = map_data["last_object_clicked"]["properties"]["NAMELSAD10"]
        # Update the state. This will trigger a rerun.
        st.session_state.clicked_county = county_name
    except (KeyError, TypeError):
        # Click was not on a valid county (e.g., on the ocean)
        st.session_state.clicked_county = None
        st.info("Clicked on the map, but not on a county.")

## UPDATED: Display the persistently selected county from state
if st.session_state.clicked_county:
    st.success(f"You have selected: **{st.session_state.clicked_county}**!")
else:
    st.info("No county selected yet.")


# --- 6. Other Page Components ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above shows all counties in New Mexico.")

with col2:
    st.header("Next Steps")
    st.write("You can use the clicked county name to show specific data.")
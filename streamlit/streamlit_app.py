import streamlit as st
import folium
from streamlit_folium import st_folium
import json  ## NEW ## Import the json library

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="New Mexico Interactive Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. Main Page Content ---
st.title("Interactive Map of New Mexico 🗺️")
st.write("This map is fully interactive. You can zoom, pan, and click on a county.")

## NEW ## --- Load Local GeoJSON File ---
file_path = "streamlit/tl_2010_35_county10.geojson"
try:
    with open(file_path, "r") as f:
        nm_county_data = json.load(f)
except FileNotFoundError:
    st.error(f"Error: GeoJSON file not found at '{file_path}'.")
    st.error("Please make sure the file is in the same directory as your script.")
    st.stop() # Stop the app if the file isn't found
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

## NEW ## --- Add County Outlines (from local data) ---

folium.GeoJson(
    nm_county_data, # Pass the loaded data variable here
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
        ## NEW ## Use the correct field from your file
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

if map_data.get("last_object_clicked"):
    ## NEW ## Use the correct property name from your file
    try:
        county_name = map_data["last_object_clicked"]["properties"]["NAMELSAD10"]
        st.success(f"You clicked on **{county_name}**!")
    except KeyError:
        st.warning("Clicked on the map, but couldn't find the county name property.")
else:
    st.info("No county clicked yet.")


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
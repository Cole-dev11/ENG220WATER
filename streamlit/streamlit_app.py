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
st.write("This map is fully interactive. You can zoom, pan, and click on a county.")

# --- 3. Folium Map Creation ---

# Center coordinates for New Mexico
nm_lat = 34.5
nm_lon = -106.0
nm_zoom = 7

# Create a Folium map object
m = folium.Map(location=[nm_lat, nm_lon], zoom_start=nm_zoom)

## NEW ## --- Add County Outlines (GeoJSON) ---

# This is a URL to a GeoJSON file containing NM county boundaries.
# Source: Public domain data
geojson_url = "http://gstore.unm.edu/apps/rgisarchive/datasets/2ea98a14-0341-466d-9ef8-b61bbfc41c4a/tl_2010_35_county10.derived.geojson"

# Add the GeoJSON layer to the map
folium.GeoJson(
    geojson_url,
    name="New Mexico Counties",
    
    # Style function to color the counties
    style_function=lambda feature: {
        'fillColor': '#FFFF00',  # Yellow fill
        'color': 'black',        # Black border
        'weight': 1,             # Border thickness
        'fillOpacity': 0.3,      # How transparent the fill is
    },
    
    # Highlight function to change style on hover
    highlight_function=lambda x: {
        'weight': 3,             # Thicker border on hover
        'color': '#FF0000',      # Red border on hover
        'fillOpacity': 0.6,      # More opaque on hover
    },
    
    # Tooltip to show county name on hover
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name'],         # The property in the GeoJSON to display
        aliases=['County:'],     # The label to show before the name
        sticky=True
    )
).add_to(m)

# --- 4. Display Map and Capture Clicks ---

# We assign the output of st_folium to a variable `map_data`
# This variable will hold information about the map's state,
# including the last object that was clicked.
st.write("Click on a county to see its name below.")
map_data = st_folium(
    m,
    use_container_width=True,
    height=500,
    returned_objects=["last_object_clicked"] # Tell st_folium to return click data
)

# --- 5. Handle Click Data ---

st.header("Click Information")

# Check if an object was clicked
if map_data.get("last_object_clicked"):
    # The GeoJSON data is nested under 'properties'
    county_name = map_data["last_object_clicked"]["properties"]["name"]
    st.success(f"You clicked on **{county_name}** County!")
else:
    st.info("No county clicked yet.")


# --- 6. Other Page Components (from your code) ---

# --- Sidebar ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

# --- Columns ---
col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above shows all counties in New Mexico.")

with col2:
    st.header("Next Steps")
    st.write("You can use the clicked county name to show specific data.")
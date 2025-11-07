import streamlit as st
import folium
from streamlit_folium import st_folium

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="New Mexico Interactive Map",
    page_icon="🗺️",
    layout="wide",
)

# --- 2. Main Page Content ---
st.title("Interactive Map of New Mexico Counties 🗺️")
st.write("This map is fully interactive. You can zoom, pan, and click on any county.")

# --- 3. GeoJSON Data ---
# This is a URL to a public GeoJSON file containing NM county boundaries.
# We will load this file directly into Folium.

# !!! THIS IS THE CORRECTED URL !!!
nm_geojson_url = "https://raw.githubusercontent.com/usdus/maps/master/geojson/new-mexico-counties.geojson"


# --- 4. Folium Map Creation ---
# Center coordinates for New Mexico
nm_lat = 34.5
nm_lon = -106.0
nm_zoom = 7

# Create a Folium map object
m = folium.Map(location=[nm_lat, nm_lon], zoom_start=nm_zoom)

# --- 5. Add GeoJSON Layer ---
# This is the key part!
# We're adding the GeoJSON data to the map 'm'.

# Define a style function for the GeoJSON layer
def style_function(feature):
    return {
        'fillOpacity': 0.1,  # Light fill
        'weight': 2,         # Border thickness
        'color': 'blue',     # Border color
        'fillColor': '#2596be' # Fill color
    }

# Define a highlight function for when hovering
def highlight_function(feature):
    return {
        'fillOpacity': 0.5,
        'weight': 3,
        'color': 'black',
    }

# Add the GeoJSON layer
folium.GeoJson(
    data=nm_geojson_url,
    style_function=style_function,
    highlight_function=highlight_function,
    
    # This directly enables the "zoom in" feature on click
    zoom_on_click=True,
    
    # This creates the popup. It pulls the 'NAME' property from the GeoJSON file.
    popup=folium.GeoJsonPopup(fields=['NAME'], aliases=['County:']),
    
    # This adds a tooltip that shows on hover
    tooltip=folium.GeoJsonTooltip(fields=['NAME']),
    
    name="New Mexico Counties"
).add_to(m)

# Add layer control to toggle the county layer on/off
folium.LayerControl().add_to(m)


# --- 6. Display Map in Streamlit & Capture Output ---
# We assign the output of st_folium to a variable 'map_data'
# This allows us to see what the user is interacting with
map_data = st_folium(
    m, 
    use_container_width=True, 
    height=500,
    returned_objects=[] # We don't need to return objects for this
)

# --- 7. Display Click Info (Optional) ---
# This demonstrates how you can use the click data in Streamlit
st.header("County Click Information")
st.write("When you click a county, its properties from the GeoJSON file will be shown here.")

if map_data.get("last_geojson_clicked") and map_data["last_geojson_clicked"]["properties"]:
    st.write(map_data["last_geojson_clicked"]["properties"])
else:
    st.write("No county clicked yet.")


# --- 8. Sidebar and Columns (from your original code) ---
st.sidebar.header("Map Options")
st.sidebar.write("Future map controls can go here!")

col1, col2 = st.columns(2)
with col1:
    st.header("Map Info")
    st.write("The map above is centered on New Mexico and loads county boundary data from a public GeoJSON file.")

with col2:
    st.header("How it Works")
    st.write(
        """
        1.  We use `folium.GeoJson` to read the boundary data.
        2.  `zoom_on_click=True` tells Folium to automatically zoom to the feature.
        3.  `folium.GeoJsonPopup(fields=['NAME'])` reads the 'NAME' property from the data file and displays it in the popup.
        """
    )
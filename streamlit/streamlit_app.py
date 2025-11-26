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
# This path matches the 'us_states.json' file you uploaded.
file_path = "data/us_states.json"
try:
    with open(file_path, "r") as f:
        # Load the GeoJSON data into a variable
        us_state_data = json.load(f) 
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


# --- !!! DIAGNOSTIC STEP ADDED HERE !!! ---
# Check the properties of the first feature in the GeoJSON to confirm the state name field.
if us_state_data and 'features' in us_state_data and us_state_data['features']:
    first_feature_properties = us_state_data['features'][0]['properties']
    st.sidebar.subheader("GeoJSON Property Check (Diagnostic)")
    st.sidebar.write("Inspect the properties below to find the correct state name field (e.g., 'name', 'STATE_NAME', 'NAME'):")
    st.sidebar.json(first_feature_properties)
    st.sidebar.markdown("**Look for the field that holds the state name (e.g., 'California', 'Texas', etc.)**")
# --- !!! END OF DIAGNOSTIC STEP !!! ---


# --- 3. Folium Map Creation ---
# Centered on the contiguous United States for a good view
us_lat = 39.8283
us_lon = -98.5795
us_zoom = 4

m = folium.Map(location=[us_lat, us_lon], zoom_start=us_zoom)

# --- Add State Outlines (from local data) ---

folium.GeoJson(
    us_state_data, # Pass the loaded data variable here
    name="US States",
    
    style_function=lambda feature: {
        'fillColor': '#4682B4', # Steel Blue
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.3,
    },
    
    highlight_function=lambda x: {
        'weight': 3,
        'color': '#FF4500', # Orange Red for highlight
        'fillOpacity': 0.6,
    },
    
    # Keep the tooltip fields dynamic until you confirm the name
    tooltip=folium.features.GeoJsonTooltip(
        # Use a placeholder like 'name' initially
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
    # The property name to use for the state name is typically 'name', 'STATE_NAME', or 'NAME'
    # **UPDATE THIS LINE** once you confirm the correct field from the sidebar check!
    state_name_property_key = "name" # Start with 'name'
    
    try:
        # **UPDATED FIELD:** Using the variable property key
        state_name = map_data["last_object_clicked"]["properties"][state_name_property_key]
        st.success(f"You clicked on the state: **{state_name}**!")
    except KeyError:
        st.warning(f"Clicked on the map, but couldn't find the state name property **'{state_name_property_key}'** in the clicked object's properties.")
        st.warning("Please check the GeoJSON properties printed in the sidebar and update the `state_name_property_key` variable.")
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
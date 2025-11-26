import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import numpy as np
import os # To handle file paths robustly

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="US Pipe Lead Content Heatmap",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Define File Paths ---
# Use the file path you provided
DATA_FILE_PATH = "data/projected_pipes.csv"
GEOJSON_FILE_PATH = "data/us_states.json"

## Helper function to load data and handle errors
@st.cache_data
def load_data(path, is_geojson=False):
    """Loads CSV or GeoJSON data and handles file errors."""
    if not os.path.exists(path):
        st.error(f"Error: File not found at '{path}'.")
        st.error("Please ensure the file is correctly placed in your project directory.")
        st.stop()
        return None
        
    try:
        if is_geojson:
            with open(path, "r") as f:
                data = json.load(f)
        else:
            data = pd.read_csv(path)
        return data
    except pd.errors.EmptyDataError:
        st.error(f"Error: The file '{path}' is empty.")
        st.stop()
    except pd.errors.ParserError:
        st.error(f"Error: Could not parse '{path}'. Please check its format.")
        st.stop()
    except json.JSONDecodeError:
        st.error(f"Error: Could not read or decode the GeoJSON file at '{path}'.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the file: {e}")
        st.stop()
        
    return None

# --- 2. Data Loading and Processing ---
st.title("Lead Pipe Content Heatmap by US State 🗺️")

# Load and process pipe data
pipe_df = load_data(DATA_FILE_PATH)

if pipe_df is not None:
    # --- Data Cleaning and Preparation ---
    # Convert the percentage column to a float (stripping the '%' and dividing by 100)
    pipe_df['%_Total_with_lead_float'] = (
        pipe_df['%_Total_with_lead']
        .str.rstrip('%')
        .astype(float)
        / 100
    )
    
    # Fill NaN values in the key columns with 0 for cleaner display/ranking
    pipe_df = pipe_df.fillna(0)

    # --- Data Ranking (out of 50 states) ---
    # Sort by percentage in descending order and calculate rank (1 is highest percentage)
    pipe_df = pipe_df.sort_values(by='%_Total_with_lead_float', ascending=False).reset_index(drop=True)
    pipe_df['Lead_Rank_out_of_50'] = pipe_df.index + 1
    # Only consider the 50 US states (excluding Puerto Rico for ranking, if applicable)
    pipe_df['Lead_Rank_out_of_50'] = pipe_df['%_Total_with_lead_float'].rank(method='min', ascending=False)
    
    # Store the processed DataFrame in session state for easy access on click
    st.session_state['pipe_data'] = pipe_df.set_index('State')

# Load GeoJSON data
us_state_data = load_data(GEOJSON_FILE_PATH, is_geojson=True)

if pipe_df is None or us_state_data is None:
    # Stop execution if data loading failed
    st.stop()

# --- 3. Folium Map Creation ---
us_lat = 39.8283
us_lon = -98.5795
us_zoom = 4

m = folium.Map(location=[us_lat, us_lon], zoom_start=us_zoom, tiles='cartodbdarkmatter')

# --- Add Choropleth Heatmap (based on %_Total_with_lead) ---
folium.Choropleth(
    # GeoJSON Data and Key
    geo_data=us_state_data,
    name='Lead Content Heatmap',
    data=pipe_df,
    columns=['State', '%_Total_with_lead_float'],
    key_on='feature.properties.name', # The GeoJSON property for state name
    
    # Visualization Settings
    fill_color='YlOrRd', # Yellow-Orange-Red color scheme
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Percentage of Total Pipes with Lead (%)',
    
    # Style and Tooltip
    highlight=True
).add_to(m)

# Add a GeoJson layer *again* for custom tooltips and click handling
# This layer will be transparent but handle the click events cleanly
state_layer = folium.GeoJson(
    us_state_data, 
    name="US States Click Layer",
    style_function=lambda x: {'fillColor': 'clear', 'color': 'black', 'weight': 0.5, 'fillOpacity': 0},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name'],
        aliases=['State:'],
        sticky=True
    )
).add_to(m)

# --- 4. Display Map and Capture Clicks ---
st.markdown("---")
st.markdown("Click on any state in the map below to view its specific lead pipe data and national ranking.")
map_data = st_folium(
    m,
    use_container_width=True,
    height=500,
    returned_objects=["last_object_clicked"]
)

# --- 5. Handle Click Data and Display Details ---
st.markdown("---")
st.header("State-Specific Pipe Data")
st.caption("Data is pulled from the loaded 'projected_pipes.csv' file.")

if map_data.get("last_object_clicked"):
    # Get the state name from the clicked object's properties
    clicked_props = map_data["last_object_clicked"].get("properties", {})
    state_name = clicked_props.get("name")
    
    if state_name:
        # Check if the clicked state exists in the pipe data
        if state_name in st.session_state['pipe_data'].index:
            state_data = st.session_state['pipe_data'].loc[state_name]
            
            # --- Displaying the Requested Information ---
            st.success(f"Details for **{state_name}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("National Ranking")
                # Format rank as an integer, as requested (out of 50 states/territories)
                rank = int(state_data['Lead_Rank_out_of_50'])
                st.metric(
                    label="Lead Pipe Percentage Rank",
                    value=f"#{rank}",
                    delta=f"Out of {len(pipe_df)} states/territories"
                )
                
                st.subheader("Total Pipes with Lead")
                st.metric(
                    label="% of Total Pipes with Lead",
                    value=state_data['%_Total_with_lead'],
                    delta=f"Total Pipes: {state_data['Total']:,}" # Add comma formatting for large numbers
                )
                
            with col2:
                st.subheader("Pipe Material Breakdown (Count)")
                # Show the breakdown of the pipe types
                st.table(pd.DataFrame({
                    'Pipe Type': ['Lead Content', 'Standalone Galvanized', 'Not Lead', 'Not Lead or Galvanized'],
                    'Count': [
                        f"{state_data['Lead_Content']:,}", 
                        f"{state_data['Standalone_Galvanized']:,}", 
                        f"{state_data['Not_Lead_or_Galvanized']:,}",
                        # Assuming 'Not Lead' means the sum of the non-lead categories
                        f"{state_data['Standalone_Galvanized'] + state_data['Not_Lead_or_Galvanized']:,}"
                    ]
                }).set_index('Pipe Type'))
                
        else:
            # Handle cases where the state name exists in GeoJSON but not in your CSV data (e.g., if you only had 50 states and clicked on Puerto Rico)
            st.warning(f"Click detected on **{state_name}**. No detailed data found for this location in the CSV file.")
    else:
        st.warning(
            "Click detected on a map feature, but the state name property was not found. "
            "Please try clicking closer to the center of a state."
        )
else:
    st.info("👈 Please click on a state in the map above to view its data.")

# --- 6. Sidebar Info ---
st.sidebar.header("Data Source")
st.sidebar.markdown(f"Data imported from: **{DATA_FILE_PATH}**")
st.sidebar.markdown(f"Map outlines from: **{GEOJSON_FILE_PATH}**")
st.sidebar.caption("The heatmap visualization is based on the `%_Total_with_lead` column, where a darker red indicates a higher percentage.")
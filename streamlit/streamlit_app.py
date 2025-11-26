import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import numpy as np
import os

# --- Define File Paths ---
DATA_FILE_PATH = "data/projected_pipes.csv"
GEOJSON_FILE_PATH = "data/us_state_boundaries.geojson"

# --- Helper function to load data and handle errors ---
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

# --- NEW FUNCTION: Display State Details in Sidebar ---
def display_state_details(state_name, pipe_data):
    """
    Displays the detailed pipe data for a specific state in the Streamlit sidebar.
    """
    if state_name and state_name in pipe_data.index:
        state_data = pipe_data.loc[state_name]
        
        # --- Displaying the Requested Information ---
        st.sidebar.header(f"Details for {state_name} 📊")
        
        # National Ranking
        rank = int(state_data['Lead_Rank_out_of_50'])
        st.sidebar.metric(
            label="Lead Pipe Percentage Rank",
            value=f"#{rank}",
            delta=f"Out of {len(pipe_data)} states/territories"
        )
        
        # Total Pipes with Lead
        st.sidebar.subheader("Lead Content Summary")
        st.sidebar.metric(
            label="% of Total Pipes with Lead",
            value=state_data['%_Total_with_lead'],
            delta=f"Total Pipes: {state_data['Total']:,}" # Add comma formatting
        )
            
        st.sidebar.subheader("Pipe Material Breakdown (Count)")
        # Show the breakdown of the pipe types
        st.sidebar.table(pd.DataFrame({
            'Pipe Type': ['Lead Content', 'Standalone Galvanized', 'Not Lead or Galvanized'],
            'Count': [
                f"{state_data['Lead_Content']:,}", 
                f"{state_data['Standalone_Galvanized']:,}", 
                f"{state_data['Not_Lead_or_Galvanized']:,}",
            ]
        }).set_index('Pipe Type'))
        
        st.sidebar.caption("Data is pulled from the loaded 'projected_pipes.csv' file.")
        
    elif state_name:
        # Handle cases where the state name exists in GeoJSON but not in your CSV data
        st.sidebar.warning(f"Click detected on **{state_name}**. No detailed data found for this location in the CSV file.")
    else:
        st.sidebar.info("👈 Please click on a state in the map to view its data.")

# --- 1. Main Application Function ---
def main():
    st.set_page_config(
        page_title="US Pipe Lead Content Heatmap",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="auto"
    )

    st.title("Lead Pipe Content Heatmap by US State 🗺️")

    # --- 2. Data Loading and Processing ---
    pipe_df = load_data(DATA_FILE_PATH)
    us_state_data = load_data(GEOJSON_FILE_PATH, is_geojson=True)

    if pipe_df is None or us_state_data is None:
        st.stop()
    
    # --- Data Cleaning and Preparation (as before) ---
    pipe_df['%_Total_with_lead_float'] = (
        pipe_df['%_Total_with_lead']
        .str.rstrip('%')
        .astype(float)
        / 100
    )
    pipe_df = pipe_df.fillna(0)

    # --- Data Ranking (as before) ---
    pipe_df['Lead_Rank_out_of_50'] = pipe_df['%_Total_with_lead_float'].rank(method='min', ascending=False)
    pipe_data_indexed = pipe_df.set_index('State')
    
    # --- 3. Folium Map Creation ---
    us_lat = 39.8283
    us_lon = -98.5795
    m = folium.Map(location=[us_lat, us_lon], zoom_start=4, tiles='cartodbdarkmatter')

    # Add Choropleth Heatmap
    folium.Choropleth(
        geo_data=us_state_data,
        name='Lead Content Heatmap',
        data=pipe_df,
        columns=['State', '%_Total_with_lead_float'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Percentage of Total Pipes with Lead (%)',
        highlight=True
    ).add_to(m)

    # Add a GeoJson layer *again* for custom tooltips and click handling
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
    st.info("Click on any state in the map below to view its specific lead pipe data and national ranking in the **sidebar**.")
    
    map_data = st_folium(
        m,
        use_container_width=True,
        height=500,
        returned_objects=["last_object_clicked"]
    )

    # --- 5. Handle Click Data and Display Details ---
    clicked_state_name = ''
    if map_data and map_data.get("last_object_clicked"):
        # Get the state name from the clicked object's properties
        clicked_props = map_data["last_object_clicked"].get("properties", {})
        clicked_state_name = clicked_props.get("name", '')

    # --- Display State-Specific Data in the Sidebar ---
    # The display logic has been moved to this function, which uses st.sidebar
    display_state_details(clicked_state_name, pipe_data_indexed)

    # --- 6. Main Content Footer (Re-position original sidebar content) ---
    st.markdown("---")
    st.header("Map Interpretation")
    st.caption("The map visualizes the lead pipe data based on the `%_Total_with_lead` column, where a darker red indicates a higher percentage.")
    
    st.subheader("Data Sources")
    st.markdown(f"* Pipe Data: **{DATA_FILE_PATH}**")
    st.markdown(f"* Map Outlines: **{GEOJSON_FILE_PATH}**")


if __name__ == "__main__":
    main()
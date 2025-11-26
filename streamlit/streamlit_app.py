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

# --- REMOVED: display_state_details function is no longer needed for hover functionality ---

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
    
    # --- Data Cleaning and Preparation ---
    pipe_df['%_Total_with_lead_float'] = (
        pipe_df['%_Total_with_lead']
        .str.rstrip('%')
        .astype(float)
        / 100
    )
    pipe_df = pipe_df.fillna(0)

    # --- Data Ranking ---
    pipe_df['Lead_Rank'] = pipe_df['%_Total_with_lead_float'].rank(method='min', ascending=False).astype(int)
    
    # --- Prepare all data fields for Tooltip (Formatted Strings) ---
    # We must format the data here so it appears cleanly on hover
    pipe_df['Reports_Rank'] = '#' + pipe_df['Lead_Rank'].astype(str)
    pipe_df['Total_Pipes_Fmt'] = pipe_df['Total'].apply(lambda x: f"{int(x):,}")
    pipe_df['Lead_Pipes_Fmt'] = pipe_df['Lead_Content'].apply(lambda x: f"{int(x):,}")
    pipe_df['Galvanized_Pipes_Fmt'] = pipe_df['Standalone_Galvanized'].apply(lambda x: f"{int(x):,}")
    pipe_df['Not_Lead_Pipes_Fmt'] = pipe_df['Not_Lead_or_Galvanized'].apply(lambda x: f"{int(x):,}")
    
    # Select only the columns needed for the map/tooltip and index by State
    pipe_data_for_map = pipe_df[['State', '%_Total_with_lead_float', 'Reports_Rank', 
                                 '%_Total_with_lead', 'Total_Pipes_Fmt', 'Lead_Pipes_Fmt', 
                                 'Galvanized_Pipes_Fmt', 'Not_Lead_Pipes_Fmt']].set_index('State')
    
    # --- 3. Folium Map Creation ---
    us_lat = 39.8283
    us_lon = -98.5795
    m = folium.Map(location=[us_lat, us_lon], zoom_start=4, tiles='cartodbdarkmatter')

    # Add Choropleth Heatmap
    choropleth = folium.Choropleth(
        geo_data=us_state_data,
        name='Lead Content Heatmap',
        data=pipe_data_for_map,
        columns=['State', '%_Total_with_lead_float'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Percentage of Total Pipes with Lead (%)',
        highlight=True
    ).add_to(m)

    # --- Add Data to GeoJSON features for Tooltips ---
    # This step joins your formatted data to the map features
    for feature in choropleth.geojson.data['features']:
        state_name = feature['properties']['name']
        if state_name in pipe_data_for_map.index:
            state_data = pipe_data_for_map.loc[state_name]
            feature['properties']['Lead_Rank'] = state_data['Reports_Rank']
            feature['properties']['Pct_Lead'] = state_data['%_Total_with_lead']
            feature['properties']['Total_Pipes'] = state_data['Total_Pipes_Fmt']
            feature['properties']['Lead_Content_Count'] = state_data['Lead_Pipes_Fmt']
            feature['properties']['Standalone_Galvanized_Count'] = state_data['Galvanized_Pipes_Fmt']
            feature['properties']['Not_Lead_Count'] = state_data['Not_Lead_Pipes_Fmt']
        else:
            # Handle states not in data (e.g., US territories)
            feature['properties']['Lead_Rank'] = 'N/A'
            feature['properties']['Pct_Lead'] = 'N/A'
            feature['properties']['Total_Pipes'] = 'N/A'
            feature['properties']['Lead_Content_Count'] = 'N/A'
            feature['properties']['Standalone_Galvanized_Count'] = 'N/A'
            feature['properties']['Not_Lead_Count'] = 'N/A'
            
    # --- Create the new HOVER Tooltip ---
    tooltip_fields = [
        'name',
        'Lead_Rank',
        'Pct_Lead',
        'Total_Pipes',
        'Lead_Content_Count',
        'Standalone_Galvanized_Count',
        'Not_Lead_Count'
    ]
    
    tooltip_aliases = [
        'State',
        'National Rank',
        '% Total with Lead',
        'Total Pipes',
        'Count: Lead Content',
        'Count: Standalone Galvanized',
        'Count: Not Lead or Galvanized'
    ]
    
    # Add the tooltip to the Choropleth's GeoJson layer
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True, # Recommended for better display
            sticky=False, # Allows the tooltip to move freely
            style="background-color: white; color: black; font-family: monospace; font-size: 10px; padding: 5px;"
        )
    )

    # --- 4. Display Map (Click capture removed) ---
    st.markdown("---")
    st.info("Hover over any state in the map below to view all its specific lead pipe data and national ranking.")
    
    # Display the map without needing to capture clicks
    st_folium(
        m,
        use_container_width=True,
        height=500
    )

    # --- 5. Sidebar and Click logic removed (since we are using hover tooltips) ---
    st.sidebar.header("Map Functionality")
    st.sidebar.info("Data details now appear on **hover** directly on the map via a tooltip.")
    
    # --- 6. Main Content Footer ---
    st.markdown("---")
    st.header("Map Interpretation")
    st.caption("The map visualizes the lead pipe data based on the `%_Total_with_lead` column, where a darker red indicates a higher percentage.")
    
    st.subheader("Data Sources")
    st.markdown(f"* Pipe Data: **{DATA_FILE_PATH}**")
    st.markdown(f"* Map Outlines: **{GEOJSON_FILE_PATH}**")


if __name__ == "__main__":
    main()
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import numpy as np
import os

DATA_FILE_PATH = "data/projected_pipes.csv"
GEOJSON_FILE_PATH = "data/us_state_boundaries.geojson"

@st.cache_data
def load_data(path, is_geojson=False):
    """
    Loads CSV or GeoJSON data and handles common file and parsing errors.

    Args:
        path (str): The file path to the data.
        is_geojson (bool): If True, loads the file as GeoJSON; otherwise, loads as CSV.

    Returns:
        The loaded data (pandas DataFrame or dict), or None if an error occurs.
    """
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

def main():
    """
    Sets up the Streamlit application, loads and processes data, creates a Folium 
    choropleth map based on user selection, and displays the map and sidebar.
    """
    st.set_page_config(
        page_title="US Pipe Lead Content Heatmap",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="auto"
    )

    st.title("Lead Pipe Content Heatmap by US State 🗺️")

    pipe_df = load_data(DATA_FILE_PATH)
    us_state_data = load_data(GEOJSON_FILE_PATH, is_geojson=True)

    if pipe_df is None or us_state_data is None:
        st.stop()
    
    pipe_df['%_Total_with_lead_float'] = (
        pipe_df['%_Total_with_lead']
        .str.rstrip('%')
        .astype(float)
        / 100
    )
    pipe_df = pipe_df.fillna(0)

    pipe_df['Lead_Rank'] = pipe_df['%_Total_with_lead_float'].rank(method='min', ascending=False).astype(int)
    
    pipe_df['Reports_Rank'] = '#' + pipe_df['Lead_Rank'].astype(str)
    pipe_df['Total_Pipes_Fmt'] = pipe_df['Total'].apply(lambda x: f"{int(x):,}")
    pipe_df['Lead_Pipes_Fmt'] = pipe_df['Lead_Content'].apply(lambda x: f"{int(x):,}")
    pipe_df['Galvanized_Pipes_Fmt'] = pipe_df['Standalone_Galvanized'].apply(lambda x: f"{int(x):,}")
    pipe_df['Not_Lead_Pipes_Fmt'] = pipe_df['Not_Lead_or_Galvanized'].apply(lambda x: f"{int(x):,}")
    
    pipe_data_for_map = pipe_df.set_index('State')
    
    MAP_OPTIONS = {
        '%_Total_with_lead_float': 'Percentage of Total Pipes with Lead (%)',
        'Lead_Content': 'Count of Pipes with Lead Content',
        'Total': 'Total Pipes Count',
        'Standalone_Galvanized': 'Count of Standalone Galvanized Pipes',
        'Not_Lead_or_Galvanized': 'Count of Not Lead or Galvanized Pipes'
    }
    
    selected_key = st.selectbox(
        '**Select the data to display on the heatmap:**',
        options=list(MAP_OPTIONS.keys()),
        format_func=lambda x: MAP_OPTIONS[x],
        index=0
    )
    
    legend_title = MAP_OPTIONS[selected_key]
    
    st.markdown("---")

    us_lat = 39.8283
    us_lon = -98.5795
    m = folium.Map(location=[us_lat, us_lon], zoom_start=4, tiles='cartodbdarkmatter')

    choropleth = folium.Choropleth(
        geo_data=us_state_data,
        name='Data Heatmap',
        data=pipe_df, 
        columns=['State', selected_key],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=legend_title,
        highlight=True
    ).add_to(m)

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
            feature['properties']['Lead_Rank'] = 'N/A'
            feature['properties']['Pct_Lead'] = 'N/A'
            feature['properties']['Total_Pipes'] = 'N/A'
            feature['properties']['Lead_Content_Count'] = 'N/A'
            feature['properties']['Standalone_Galvanized_Count'] = 'N/A'
            feature['properties']['Not_Lead_Count'] = 'N/A'
            
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
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            style="background-color: white; color: black; font-family: monospace; font-size: 10px; padding: 5px;"
        )
    )
    
    st_folium(
        m,
        use_container_width=True,
        height=500
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Map Interpretation")
    st.sidebar.caption("The map visualizes the pipe data based on your selection. A darker red indicates a higher value for the chosen metric.")
    
    st.sidebar.subheader("Data Sources")
    st.sidebar.markdown(f"* Pipe Data: **{DATA_FILE_PATH}**")
    st.sidebar.markdown(f"* Map Outlines: **{GEOJSON_FILE_PATH}**")


if __name__ == "__main__":
    main()
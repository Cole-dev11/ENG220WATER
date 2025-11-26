import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import numpy as np
import os
import altair as alt # <-- Import Altair

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
    # Format counts by converting to integer first to remove decimals, then apply comma formatting
    pipe_df['Reports_Rank'] = '#' + pipe_df['Lead_Rank'].astype(str)
    pipe_df['Total_Pipes_Fmt'] = pipe_df['Total'].apply(lambda x: f"{int(x):,}")
    pipe_df['Lead_Pipes_Fmt'] = pipe_df['Lead_Content'].apply(lambda x: f"{int(x):,}")
    pipe_df['Galvanized_Pipes_Fmt'] = pipe_df['Standalone_Galvanized'].apply(lambda x: f"{int(x):,}")
    pipe_df['Not_Lead_Pipes_Fmt'] = pipe_df['Not_Lead_or_Galvanized'].apply(lambda x: f"{int(x):,}")
    
    # Create the indexed version for quick data look-up when generating tooltips
    pipe_data_for_map = pipe_df.set_index('State')
    
    # --- 3. Folium Map Creation ---
    us_lat = 39.8283
    us_lon = -98.5795
    m = folium.Map(location=[us_lat, us_lon], zoom_start=4, tiles='cartodbdarkmatter')

    # Add Choropleth Heatmap
    choropleth = folium.Choropleth(
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

    # --- Add Data to GeoJSON features for Tooltips ---
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
            localize=True,
            sticky=False,
            style="background-color: white; color: black; font-family: monospace; font-size: 10px; padding: 5px;"
        )
    )

    # --- 4. Display Map ---
    st.markdown("---")
    st.info("Hover over any state in the map below to view all its specific lead pipe data and national ranking.")
    
    # Display the map without needing to capture clicks
    st_folium(
        m,
        use_container_width=True,
        height=500
    )

    # --- 5. Interactive Bar Chart ---
    
    st.markdown("---")
    st.header("State-by-State Pipe Data Comparison 📊")

    # 5a. Define columns for the user to select
    # We will use the raw numerical columns for the chart, not the formatted strings
    chart_columns = {
        '% Total with Lead': '%_Total_with_lead_float',
        'Total Pipes Count': 'Total',
        'Lead Pipes Count': 'Lead_Content',
        'Standalone Galvanized Count': 'Standalone_Galvanized',
        'Not Lead or Galvanized Count': 'Not_Lead_or_Galvanized',
    }
    
    selected_options = st.multiselect(
        "Select data point(s) to display on the Y-axis:",
        options=list(chart_columns.keys()),
        default=['% Total with Lead', 'Total Pipes Count']
    )
    
    if not selected_options:
        st.warning("Please select at least one data point to display on the chart.")
    else:
        # Convert user-friendly names back to DataFrame column names
        selected_cols_df_names = [chart_columns[option] for option in selected_options]
        
        # 5b. Prepare data for Altair
        # We need to melt the DataFrame to long format for easy multi-variable plotting with Altair
        df_chart = pipe_df[['State'] + selected_cols_df_names].melt(
            id_vars=['State'],
            var_name='Metric',
            value_name='Value'
        )

        # Map the DataFrame column names back to user-friendly names for the chart legend/tooltip
        # This is a reverse lookup for display purposes
        df_chart['Metric'] = df_chart['Metric'].map({v: k for k, v in chart_columns.items()})

        # 5c. Create the Altair Chart
        
        # Base chart setup
        base = alt.Chart(df_chart).encode(
            # X-axis is the state name, sorting by the State column
            x=alt.X('State:N', sort=None, axis=alt.Axis(labelAngle=-45)), 
            # Y-axis is the dynamic Value, which will be faceted by Metric
            y=alt.Y('Value:Q', title="Value"),
            # Color is the Metric (the data series selected by the user)
            color='Metric:N',
            # Tooltip for interactivity
            tooltip=['State', 'Metric', alt.Tooltip('Value:Q', format=',.2f')]
        ).properties(
            title='Comparison of Pipe Metrics by State'
        )

        # Bar marks
        bars = base.mark_bar().encode(
            # We use column as a way to group and display the bars for different metrics side-by-side
            column=alt.Column('Metric:N', header=alt.Header(titleOrient="bottom", labelOrient="bottom")),
        )
        
        # Combine the bars and text for better labels (optional but helpful)
        chart = (bars).interactive() # Make the chart zoomable/pannable
        
        st.altair_chart(chart, use_container_width=True)

    # --- 6. Sidebar and Footer (MODIFIED) ---
    st.sidebar.header("Map Functionality")
    st.sidebar.info("Data details now appear on **hover** directly on the map via a tooltip.")
    
    # --- MOVED to Sidebar ---
    st.sidebar.markdown("---")
    st.sidebar.header("Map Interpretation")
    st.sidebar.caption("The map visualizes the lead pipe data based on the `%_Total_with_lead` column, where a darker red indicates a higher percentage.")
    
    st.sidebar.subheader("Data Sources")
    st.sidebar.markdown(f"* Pipe Data: **{DATA_FILE_PATH}**")
    st.sidebar.markdown(f"* Map Outlines: **{GEOJSON_FILE_PATH}**")
    
    # The original st.markdown("---") after the map is removed as the content is moved to the sidebar


if __name__ == "__main__":
    main()
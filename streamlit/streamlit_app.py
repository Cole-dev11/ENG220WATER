import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd

# --- 1. Set Page Configuration ---
st.set_page_config(
    page_title="US Lead Pipe Heatmap",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 2. Load and Process Data ---

STATE_COL = 'State'
COUNT_COL = 'Lead_Content'

try:
    st.sidebar.header("Data Loading")
    st.sidebar.info("Using 'State' and 'Lead_Content' columns from both CSVs.")
    
    # Load and rename columns for merging (using confirmed column names)
    df_proj = pd.read_csv("data/projected_pipes.csv").rename(
        columns={STATE_COL: 'State_Code', COUNT_COL: 'Projected_Pipes'}
    )
    df_meas = pd.read_csv("data/measured_pipes.csv").rename(
        columns={STATE_COL: 'State_Code', COUNT_COL: 'Measured_Pipes'}
    )
    
    # Clean up and ensure State_Code is correct type (2-letter abbreviation for merging)
    df_proj['State_Code'] = df_proj['State_Code'].astype(str).str.upper().str.strip()
    df_meas['State_Code'] = df_meas['State_Code'].astype(str).str.upper().str.strip()
    
    # Merge the two dataframes on the State_Code, fill missing data with 0, and calculate total
    pipes_data = pd.merge(df_proj[['State_Code', 'Projected_Pipes']],
                         df_meas[['State_Code', 'Measured_Pipes']],
                         on='State_Code',
                         how='outer').fillna(0)
                         
    pipes_data['Total_Lead_Pipes'] = pipes_data['Projected_Pipes'] + pipes_data['Measured_Pipes']
    
    st.sidebar.dataframe(pipes_data[['State_Code', 'Total_Lead_Pipes']].sort_values(
        by='Total_Lead_Pipes', ascending=False
    ).head(), caption="Top 5 States by Lead Pipe Count")
    
except Exception as e:
    st.error(f"Error loading or processing pipe data. Please ensure 'data/projected_pipes.csv' and 'data/measured_pipes.csv' are in the correct location and columns are correct. Error: {e}")
    st.stop()
    
# --- Load GeoJSON Data ---
file_path = "us_states.json"
try:
    with open(file_path, "r") as f:
        us_state_data = json.load(f) 
except Exception as e:
    st.error(f"Error loading GeoJSON file at '{file_path}'. Error: {e}")
    st.stop()


# --- 3. Folium Map Creation (Choropleth) ---
st.title("US Lead Pipe Exposure Heatmap 🌡️")
st.write("States are colored darker for a higher estimated total of lead pipes ('Lead_Content' in Projected + Measured). Click a state for detailed data.")

# Centered on the contiguous United States
us_lat = 39.8283
us_lon = -98.5795
us_zoom = 4

m = folium.Map(location=[us_lat, us_lon], zoom_start=us_zoom)

# Create the Choropleth map
cp = folium.Choropleth(
    geo_data=us_state_data,
    data=pipes_data,
    columns=['State_Code', 'Total_Lead_Pipes'],
    key_on='feature.id', # Matches the 'id' field (2-letter code) in the GeoJSON
    fill_color='YlOrRd', # Yellow-Orange-Red color scheme, darker = more pipes
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Total Estimated Lead Pipes (Units: Pipe Count)',
    highlight=True
).add_to(m)

# Add Tooltip and Click Pop-up to Choropleth
style_function = lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1}

# Create a custom GeoJson layer for tooltips and hover/click effects
NIL = folium.GeoJson(
    cp.geojson.data,
    style_function=style_function, 
    control=False,
    highlight_function=highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        # The fields below are added to the GeoJSON data by the choropleth logic
        fields=['name', 'Total_Lead_Pipes', 'Projected_Pipes', 'Measured_Pipes'],
        aliases=['State:', 'Total Pipes:', 'Projected Pipes:', 'Measured Pipes:'],
        localize=True,
        sticky=False,
        labels=True,
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
)
m.add_child(NIL)


# --- 4. Display Map and Capture Clicks ---
st.header("Click Information")
st.write("Click on a state in the map to see its total estimated lead pipe count.")

map_data = st_folium(
    m,
    use_container_width=True,
    height=550,
    returned_objects=["last_object_clicked"]
)

# --- 5. Handle Click Data ---

if map_data.get("last_object_clicked"):
    # The ID matches the 2-letter state code from the GeoJSON
    state_id = map_data["last_object_clicked"]["id"]
    
    # Get the full state name from the GeoJSON properties
    state_name = next(
        (feature['properties']['name'] for feature in us_state_data['features'] if feature['id'] == state_id),
        "Unknown State"
    )
    
    # Filter the pipe data for the clicked state
    clicked_data = pipes_data[pipes_data['State_Code'] == state_id]
    
    st.success(f"### Clicked State: **{state_name} ({state_id})**")
    
    if not clicked_data.empty:
        total = clicked_data['Total_Lead_Pipes'].iloc[0]
        proj = clicked_data['Projected_Pipes'].iloc[0]
        meas = clicked_data['Measured_Pipes'].iloc[0]
        
        st.info(f"""
        - **Total Estimated Lead Pipes (Lead\_Content):** {total:,.0f}
        - **Projected Pipes (Lead\_Content):** {proj:,.0f}
        - **Measured Pipes (Lead\_Content):** {meas:,.0f}
        """)
    else:
        st.warning(f"No lead pipe data found for {state_name} in the provided CSVs.")

else:
    st.info("No state clicked yet. Click a state to see its data.")

# --- 6. Other Page Components ---
st.sidebar.header("Map Data Details")
st.sidebar.write("The map color intensity represents the sum of the **'Lead_Content'** columns from the projected and measured pipe datasets.")
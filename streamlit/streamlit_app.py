import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd

# --- 1. State Name to Code Mapping ---
# Necessary to merge the full state names in your CSV with the 2-letter codes in the GeoJSON.
STATE_TO_CODE = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL',
    'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN',
    'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Puerto Rico': 'PR',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
    'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# --- 2. Set Page Configuration ---
st.set_page_config(
    page_title="US Lead Pipe Heatmap",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- 3. Load and Process Data (Uses confirmed 'State' and 'Lead_Content' columns) ---
try:
    # --- Load Pipe Data ---
    df_proj = pd.read_csv("data/projected_pipes.csv").rename(
        columns={'State': 'State_Name', 'Lead_Content': 'Projected_Pipes'}
    )
    df_meas = pd.read_csv("data/measured_pipes.csv").rename(
        columns={'State': 'State_Name', 'Lead_Content': 'Measured_Pipes'}
    )
    
    # --- Data Cleaning and Mapping ---
    df_proj['State_Code'] = df_proj['State_Name'].astype(str).str.strip().map(STATE_TO_CODE)
    df_meas['State_Code'] = df_meas['State_Name'].astype(str).str.strip().map(STATE_TO_CODE)
    
    # --- Merge and Calculate Total ---
    pipes_data = pd.merge(df_proj[['State_Code', 'Projected_Pipes']],
                         df_meas[['State_Code', 'Measured_Pipes']],
                         on='State_Code',
                         how='outer').fillna(0)
                         
    pipes_data['Total_Lead_Pipes'] = pipes_data['Projected_Pipes'] + pipes_data['Measured_Pipes']
    
    # --- Sidebar Check (Fix: Removed 'caption' argument) ---
    st.sidebar.header("Data Check: Top 5 States")
    st.sidebar.dataframe(pipes_data[['State_Code', 'Total_Lead_Pipes']].sort_values(
        by='Total_Lead_Pipes', ascending=False
    ).head())
    
except Exception as e:
    st.error(f"Error loading or processing pipe data. Please verify file locations and headers. Error: {e}")
    st.stop()
    
# --- Load GeoJSON Data ---
file_path = "us_states.json"
try:
    with open(file_path, "r") as f:
        us_state_data = json.load(f) 
except Exception as e:
    st.error(f"Error loading GeoJSON file at '{file_path}'. Error: {e}")
    st.stop()


# --- 4. Folium Map Creation (Choropleth) ---
st.title("US Lead Pipe Exposure Heatmap 🌡️")
st.write("States are colored darker for a higher estimated total of lead pipes. Click a state for detailed data.")

us_lat = 39.8283
us_lon = -98.5795
us_zoom = 4

m = folium.Map(location=[us_lat, us_lon], zoom_start=us_zoom)

# Create the Choropleth map
cp = folium.Choropleth(
    geo_data=us_state_data,
    data=pipes_data,
    columns=['State_Code', 'Total_Lead_Pipes'],
    key_on='feature.id', # Joins 'State_Code' from pipes_data to the GeoJSON 'id' (2-letter code)
    fill_color='YlOrRd', 
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Total Estimated Lead Pipes (Units: Pipe Count)',
    highlight=True
).add_to(m)

# Add Tooltip and Click Pop-up via a custom GeoJson layer
NIL = folium.GeoJson(
    cp.geojson.data,
    style_function=lambda x: {'fillColor': '#ffffff', 'color':'#000000', 'fillOpacity': 0.1, 'weight': 0.1}, 
    control=False,
    highlight_function=lambda x: {'fillColor': '#000000', 'color':'#000000', 'fillOpacity': 0.50, 'weight': 0.1},
    tooltip=folium.features.GeoJsonTooltip(
        fields=['name', 'Total_Lead_Pipes', 'Projected_Pipes', 'Measured_Pipes'],
        aliases=['State:', 'Total Pipes:', 'Projected Pipes:', 'Measured Pipes:'],
        localize=True,
        sticky=False,
        labels=True,
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
    )
)
m.add_child(NIL)


# --- 5. Display Map and Handle Click Data ---
st.header("Click Information")

map_data = st_folium(
    m,
    use_container_width=True,
    height=550,
    returned_objects=["last_object_clicked"]
)

if map_data.get("last_object_clicked"):
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
        - **Total Estimated Lead Pipes:** {total:,.0f}
        - **Projected Pipes:** {proj:,.0f}
        - **Measured Pipes:** {meas:,.0f}
        """)
    else:
        st.warning(f"No lead pipe data found for {state_name} in the provided CSVs.")

else:
    st.info("No state clicked yet. Click a state to see its data.")
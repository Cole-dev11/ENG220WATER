import streamlit as st
import pandas as pd
import plotly.express as px
import os # Import the os module to help with paths

# Set the page to a wide layout for better visualization
st.set_page_config(layout="wide")

st.title("New Mexico Groundwater Explorer")
st.write("An interactive app to visualize well locations and groundwater level trends.")

# --- EDIT THIS LINE ---
# Change this to the correct path to your file.
#
# Examples:
# If it's in a subfolder named 'data':
# DATA_FILEPATH = 'data/combined_data.csv'
#
# If it's in the same folder:
# DATA_FILEPATH = 'combined_data.csv'
#
# If it's in a folder one level *above* your script:
# DATA_FILEPATH = '../combined_data.csv'
#
DATA_FILEPATH = 'combined_data.csv' # <-- EDIT THIS PATH

# ---

@st.cache_data
def load_data(filepath):
    """
    Loads and processes the combined water data.
    This function is cached for performance.
    """
    
    # Check if the file exists at the given path
    if not os.path.exists(filepath):
        st.error(f"Error: The file was not found at '{filepath}'.")
        st.info(f"Please check the `DATA_FILEPATH` variable in the Python script and make sure it points to your file. The script is currently looking for it at: {os.path.abspath(filepath)}")
        return None
        
    try:
        # Load the dataset
        df = pd.read_csv(filepath)

        # Convert date column to datetime objects
        df['MSRMNT_Date'] = pd.to_datetime(df['MSRMNT_Date'], errors='coerce')

        # Drop any rows where critical data is missing
        df.dropna(subset=['MSRMNT_Date', 'Well_Location_Latitude', 
                           'Well_Location_Longitude', 'Depth_To_Water_At_Msrmnt_Point'], inplace=True)

        # Create a unique identifier for each well based on its coordinates
        df['well_id'] = df.apply(
            lambda row: f"Well at ({row['Well_Location_Latitude']:.5f}, {row['Well_Location_Longitude']:.5f})", 
            axis=1
        )
        
        return df
    except Exception as e:
        st.error(f"An error occurred while loading or processing the data: {e}")
        return None

# --- Main Application ---

# Load the data using the filepath variable
data = load_data(DATA_FILEPATH)

if data is not None:
    # --- Part 1: The Map ---
    st.header("Well Locations")
    st.write("This map shows all unique well locations from the dataset.")

    # Create a simpler DataFrame for the map with unique locations
    map_df = data[['Well_Location_Latitude', 'Well_Location_Longitude']].drop_duplicates()
    
    # Rename columns for st.map()
    map_df.rename(columns={
        'Well_Location_Latitude': 'lat',
        'Well_Location_Longitude': 'lon'
    }, inplace=True)

    st.map(map_df, zoom=5)


    # --- Part 2: Time-Series Chart ---
    st.header("Groundwater Level Over Time")
    st.write("Select a well from the dropdown to see its water level history.")

    # Get a sorted list of unique well IDs for the selector
    well_options = sorted(data['well_id'].unique())
    
    # Create the dropdown selector
    selected_well = st.selectbox("Select a Well:", options=well_options)

    if selected_well:
        # Filter the dataframe to only include data for the selected well
        well_data = data[data['well_id'] == selected_well].copy()
        
        # Sort by date to ensure the line chart is correct
        well_data.sort_values('MSRMNT_Date', inplace=True)

        # Create the interactive line chart
        fig = px.line(
            well_data,
            x='MSRMNT_Date',
            y='Depth_To_Water_At_Msrmnt_Point',
            title=f"Water Level for: {selected_well}",
            markers=True,
            labels={
                'MSRMNT_Date': 'Date',
                'Depth_To_Water_At_Msrmnt_Point': 'Depth to Water (ft)'
            }
        )
        
        # Invert the Y-axis (larger depth = lower water level)
        fig.update_yaxes(autorange="reversed")

        # Set the hover template for more info
        fig.update_traces(
            hovertemplate="<b>Date</b>: %{x}<br><b>Depth</b>: %{y:.2f} ft"
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Data could not be loaded. Waiting for the file to be available...")
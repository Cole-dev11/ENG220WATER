import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Map of New Mexico (via Plotly)")

# Center coordinates for New Mexico
nm_lat = 34.5
nm_lon = -106.0
nm_zoom = 6

# Create a map figure. We use an empty scatter_mapbox
# and just set the center and zoom level.
fig = px.scatter_mapbox(
    lat=[], 
    lon=[],
    center={'lat': nm_lat, 'lon': nm_lon},
    zoom=nm_zoom,
    height=600
)

# Set the map style
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})

# Display the map
st.plotly_chart(fig, use_container_width=True)

#Take 2
import streamlit as st
import pandas as pd
import numpy as np

# Title and description
st.title("📊 Simple Streamlit Dashboard")
st.write("This is a demo app built with Streamlit!")

# Sidebar inputs
st.sidebar.header("User Input")
num_points = st.sidebar.slider("Number of data points", 10, 1000, 100)
show_table = st.sidebar.checkbox("Show Data Table", True)

# Generate some data
data = pd.DataFrame({
    "x": np.arange(num_points),
    "y": np.random.randn(num_points).cumsum()
})

# Display data
st.subheader("Line Chart")
st.line_chart(data, x="x", y="y")

# Optionally show table
if show_table:
    st.subheader("Data Table")
    st.dataframe(data)

# Add user input text
user_name = st.text_input("Enter your name", "Guest")
st.write(f"👋 Hello, **{user_name}**!")


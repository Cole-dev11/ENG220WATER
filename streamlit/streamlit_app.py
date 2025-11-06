import streamlit as st

# --- 1. Set Page Configuration ---
# This must be the first Streamlit command in your script.
st.set_page_config(
    page_title="My Blank App",  # Title shown in browser tab
    page_icon="👋",             # Icon shown in browser tab
    layout="wide",               # 'wide' or 'centered'
    initial_sidebar_state="auto" # 'auto', 'expanded', or 'collapsed'
)

# --- 2. Main Page Content ---
st.title("My Blank Streamlit App")
st.header("Welcome!")

st.write("Start building your app here. Add widgets, text, charts, and more.")

# --- 3. Example Components (Commented Out) ---

# --- Sidebar ---
# st.sidebar.header("Options")
# name = st.sidebar.text_input("What is your name?")
# if name:
#     st.sidebar.write(f"Hello, {name}!")

# --- Columns ---
# col1, col2 = st.columns(2)
# with col1:
#     st.header("Column 1")
#     st.write("This is content for the first column.")

# with col2:
#     st.header("Column 2")
#     st.button("Click me")

# --- Interactive Widgets ---
# if st.checkbox("Show details"):
#     st.write("Here are the details you requested.")\

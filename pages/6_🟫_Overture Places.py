import streamlit as st
st.title("Overture Places Viewer")

# Path to your HTML file
html_file_path = "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/html/overture_places.html"

with open(html_file_path, "r") as f:
    html_content = f.read()

# Display HTML content
st.components.v1.html(html_content, width=800, height=600)



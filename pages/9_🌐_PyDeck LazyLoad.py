import streamlit as st
import pydeck as pdk
import json
import folium
from streamlit_folium import st_folium,folium_static
import streamlit as st
from folium.plugins import MarkerCluster, FastMarkerCluster, Fullscreen
import pandas as pd
import streamlit_ext as ste
import geopandas as gpd
import h3

st.set_page_config(layout="wide")
st.sidebar.info(
    """
    - Web: [Geoprocessing Streamlit](https://geoprocessing.streamlit.app)
    - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
    """
)

st.title("PyDeck Lazy Load")
st.write('PyDeck Lazy Load')


col1, col2 = st.columns(2)

# @st.cache_resource
@st.cache_data
def load_data_by_chunk(file_path, chunksize=1000):
    chunks = pd.read_csv(file_path, chunksize=chunksize)
    return chunks


with col1:
    url = st.text_input(
        "Enter a CSV URL with Latitude and Longitude Columns",
        'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/india_points.csv'
        # 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv'
    )
    uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
   


    form = st.form(key="pydeck_lazyload")
    with form:                          
        submitted = st.form_submit_button("PyDeck Lazy Load")        

if submitted:           
    with col2:
        if url:   
            data_chunks = load_data_by_chunk(url)
                    
        if uploaded_file:        
            data_chunks = load_data_by_chunk(uploaded_file)

        # Initialize an empty list to store PyDeck layers

        map_layers = []
        # Iterate over chunks
        for chunk in data_chunks:
            # Process and prepare data for PyDeck visualization
            # Here you can manipulate the chunked data as needed for your visualization
            # For example, convert chunk into a PyDeck-compatible format
            # and create a PyDeck layer

            # Example: Create a PyDeck scatterplot layer
            scatterplot_layer = pdk.Layer(
                "ScatterplotLayer",
                data=chunk,
                get_position=['lon', 'lat'],
                get_color=[255, 0, 0],
                get_radius=100,
                pickable=True,
            )

            # Add the scatterplot layer to the list of layers
            map_layers.append(scatterplot_layer)

        # Display the map in Streamlit
        view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)
        deck = pdk.Deck(map_layers, initial_view_state=view_state)
        st.pydeck_chart(deck)


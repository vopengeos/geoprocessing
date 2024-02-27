import folium, os
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import routingpy as rp
import pandas as pd
from datetime import datetime
import geopy.distance
from becalib.distance_const import *
from routingpy import OSRM
import geopandas as gdp
from shapely.geometry import Point, LineString
from folium.plugins import Fullscreen
import streamlit_ext as ste
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
import altair as alt
from folium.features import DivIcon


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
st.title("GeoParquet Data Visualization")
st.write('GeoParquet Data Visualization')
col1, col2 = st.columns(2)
def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download " + layer_name,
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 

with col1:
    form = st.form(key="timeseries_visualization")
    layer_name = 'timeseries'
    with form: 
        url = st.text_input(
                "Enter a GeoParquet file URL",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/polygon.parquet'
            )
        uploaded_file = st.file_uploader("Or upload a GeoParquet file")
        if url:   
            df = pd.read_parquet(url)    
            layer_name = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            df = pd.read_parquet(uploaded_file)
            layer_name = os.path.splitext(uploaded_file.name)[0]        
      
        submitted = st.form_submit_button("Display GeoParquet on Map")    
    

if submitted:
    m = folium.Map(max_zoom = 21,
                    tiles='cartodbpositron',
                    zoom_start=14,
                    control_scale=True
                    )
    Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)

    m.fit_bounds(m.get_bounds(), padding=(30, 30))
    folium_static(m, width = 600)
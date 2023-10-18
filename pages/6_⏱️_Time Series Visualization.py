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
from math import radians, cos, acos, sin, asin, sqrt

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
st.title("Time Series Data Visualization")
st.write('Time Series Data Visualization')
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
                "Enter a CSV URL with Latitude and Longitude Columns",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/salinity_2020.csv'
            )
        uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
        lat_column_index, lon_column_index = 0,0     

        if url:   
            df = pd.read_csv(url,encoding = "UTF-8")    
            layer_name = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            df = pd.read_csv(uploaded_file,encoding = "UTF-8")
            layer_name = os.path.splitext(uploaded_file.name)[0]
        m = folium.Map(max_zoom = 21,
                    tiles='stamenterrain',
                    zoom_start=14,
                    control_scale=True
                    )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)

        for index, row in df.iterrows():
            popup = row.to_frame().to_html()
            folium.Marker([row['latitude'], row['longitude']], 
                        popup=popup,
                        icon=folium.Icon(icon='cloud')
                        ).add_to(m)        
            
        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        trackpoints_origin = gdp.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')        
        download_geojson(trackpoints_origin,layer_name)
        submitted = st.form_submit_button("Display Time Series Data")    
    

if submitted:
    with col1:
        filtered = df
        filtered = filtered.drop_duplicates(subset=["ID"], keep='last')
        st.write(filtered)
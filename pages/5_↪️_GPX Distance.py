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
from shapely import reverse
from folium.plugins import Fullscreen
import streamlit_ext as ste
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
from math import radians, cos, acos, sin, asin, sqrt
import requests, polyline
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static


st.set_page_config(layout="wide")
# st.sidebar.info(
#     """
#     - Web: [Geoprocessing Streamlit](https://geoprocessing.streamlit.app)
#     - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
#     """
# )

# st.sidebar.title("Contact")
# st.sidebar.info(
#     """
#     Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
#     """
# )
# st.title("GPX Distance")
# st.write('Distance Calculator for GPS Track Logs')

col1, col2 = st.columns(2)

import gpxpy
import gpxpy.gpx

def calculate_distance(gpx_file):
    # Parse the GPX file
    gpx = gpxpy.parse(gpx_file)
    # Initialize distance variable
    distance = 0
    # Iterate through tracks, segments, and points
    for track in gpx.tracks:
        for segment in track.segments:
            prev_point = None
            for point in segment.points:
                if prev_point:
                    # Calculate distance between two points
                    distance += prev_point.distance_2d(point)
                prev_point = point
    return distance


form = st.form(key="gpx_distance")

with form: 
    gpx_file = st.file_uploader("Upload GPX file", type=["gpx"])
    submitted = st.form_submit_button("Calculate GPX Distance")    

if (submitted):   
    if gpx_file is not None:
        # Calculate distance if file is uploaded
        distance = calculate_distance(gpx_file)
        # Display the distance
        st.write("Total distance:", round(distance*10**(-3),2), "km")
# Example usage

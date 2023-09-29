import folium
from streamlit_folium import folium_static
import streamlit as st
import streamlit_ext as ste
import geopandas as gpd
import pandas as pd
import fiona, os
from shapely.geometry import mapping, shape, Point, MultiPoint, LineString, Polygon, LinearRing
import numpy as np
import shapely
# from shapely.ops import transform
from shapely.ops import voronoi_diagram
from scipy.spatial import Voronoi, ConvexHull, distance_matrix
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
st.title("Concave Hull")
st.write('Concave Hull of a Point Set')
col1, col2 = st.columns(2)    

def download_concavehull(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download LEC",
                file_name= 'lec_' + layer_name+ '.geojson',
                mime="application/json",
                data=geojson
            ) 


@st.cache_data
def save_uploaded_file(file_content, file_name):
    """
    Save the uploaded file to a temporary directory
    """
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(file_name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(file_content.getbuffer())

    return file_path

def style_function(feature):
    return {
        'fillColor': '#b1ddf9',
        'fillOpacity': 0.5,
        'color': 'blue',
        'weight': 2,
        # 'dashArray': '5, 5'
    }

def highlight_function(feature):   
    return {
    'fillColor': '#ffff00',
    'fillOpacity': 0.8,
    'color': '#ffff00',
    'weight': 4,
    # 'dashArray': '5, 5'
}

def concave_hull_create(source): 
    source_dissolved = source.dissolve()
    concavehull = source_dissolved.concave_hull(ratio=0.3, allow_holes=True)
    return concavehull

form = st.form(key="largest_empty_circle")
with form:   
    url = st.text_input(
            "Enter a URL to a point dataset",
            "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/points_concave.geojson",
        )

    uploaded_file = st.file_uploader(
            "Upload a point dataset", type=["geojson", "kml", "zip", "tab"]
        )

    if  url or uploaded_file:
        if url:
            file_path = url
            layer_name = url.split("/")[-1].split(".")[0]
        if uploaded_file:
            file_path = save_uploaded_file(uploaded_file, uploaded_file.name)
            layer_name = os.path.splitext(uploaded_file.name)[0]    

        if file_path.lower().endswith(".kml"):
            fiona.drvsupport.supported_drivers["KML"] = "rw"
            source = gpd.read_file(file_path, driver="KML")
        else:
            source = gpd.read_file(file_path)
        
        center = source.dissolve().centroid
        center_lon, center_lat = center.x, center.y
          
        with col1:   
            fields = [ column for column in source.columns if column not in source.select_dtypes('geometry')]
            m = folium.Map(tiles='stamenterrain', location = [center_lat, center_lon], zoom_start=4)           
            folium.GeoJson(source, name = layer_name,  
                           style_function = style_function, 
                           highlight_function=highlight_function,
                           marker = folium.Marker(icon=folium.Icon(
                                     icon='ok-circle',
                                     color = 'purple'
                                     )),     
                            # marker =  folium.CircleMarker(fill=True),
                            # zoom_on_click = True,
                           popup = folium.GeoJsonPopup(
                           fields = fields
                            )).add_to(m)
           
            m.fit_bounds(m.get_bounds(), padding=(30, 30))
            folium_static(m, width = 600)
        
        submitted = st.form_submit_button("Create Concave Hull")        
        if submitted:
            #################
            # Create Concave Hull
            concave_hull = concave_hull_create(source)
            with col2:                             
                map_center = source.dissolve().centroid
                center_lon, center_lat = map_center.x, map_center.y             
                fields = [ column for column in source.columns if column not in source.select_dtypes('geometry')]
                m = folium.Map(tiles='stamentoner', location = [center_lat, center_lon], zoom_start=4)                                        
                
                folium.GeoJson(concave_hull,                                    
                                style_function = style_function, 
                                highlight_function=highlight_function                                   
                                ).add_to(m)
                
                # folium.GeoJson(source,  
                #                 marker = folium.Marker(icon=folium.Icon(
                #                     icon='ok-circle',
                #                     color = 'purple'
                #                     )),  
                #                 style_function = style_function, 
                #                 highlight_function=highlight_function,                                   
                #                 popup = folium.GeoJsonPopup(
                #                 fields = fields
                #                 )).add_to(m)

                m.fit_bounds(m.get_bounds(), padding=(30, 30))
                folium_static(m, width = 600)  
                download_concavehull(concave_hull, layer_name)  

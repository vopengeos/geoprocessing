import folium
from streamlit_folium import folium_static
import streamlit as st
import streamlit_ext as ste
import geopandas as gpd
import pandas as pd
import fiona, os
from shapely.geometry import shape, Point, MultiPoint, LineString, Polygon, LinearRing
import numpy as np
import shapely
from shapely.ops import transform
from shapely.ops import voronoi_diagram

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
st.title("Center Line")
st.write('Create Center Line for Polygons')
col1, col2 = st.columns(2)    

def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download GeoJSON",
                file_name= 'centerline_' + layer_name+ '.geojson',
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

def densify(f): 
    st.write(shapely.__version__)
    st.write(gpd.__version__)
    densify_polygon = f.segmentize(max_segment_length=5)
    return densify_polygon

def listPoints(f):
    '''List the points in a Polygon in a geometry entry - some polygons are more complex than others, so accommodating for that'''    
    st.write(f)
    pointList = []
    try:
        #Note: might miss parts within parts with this
        for part in f:
            x, y = part.exterior.coords.xy
            pointList.append(list(zip(x,y)))
    except:
        try:
            x,y = f.exterior.coords.xy
            pointList.append(list(zip(x,y)))
        except:
            #this will return the geometry as is, enabling you to see if special handling is required - then modify the function as need be
            pointList.append(f)
    st.write(pointList)
    return pointList

def centerline(source): 
    if (source.geometry.type == 'Polygon').all():
        # # points = listPoints(source.geometry)
        # # target = gpd.GeoDataFrame(source, geometry=geometry)        
        # # data = {'col1': ['name1'], 'geometry': geometry}
        # target = source
        # # target['geometry'] = target.geometry.map(listPoints)
        # target.geometry.apply(lambda x: listPoints(x)).values.tolist()
        # st.write(target.geometry)
        col = source.columns.tolist()
        # new GeoDataFrame with same columns
        target = gpd.GeoDataFrame(columns=col)
        # target = source
        # Extraction of the polygon nodes and attributes values from polys and integration into the new GeoDataFrame
        for index, row in source.iterrows():
            for j in list(row['geometry'].exterior.coords): 
                target = target.append({'id': int(row['id']), 'layer':row['layer'],'name':row['name'], 'area':row['area'],'geometry':Point(j)},ignore_index=True)
        target = target.set_crs(source.crs)
        st.write(target)
        return  target

    

form = st.form(key="latlon_calculator")
with form:   
    url = st.text_input(
            "Enter a URL to a point dataset",
            "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/polygon_centerline.geojson",
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
            gdf = gpd.read_file(file_path, driver="KML")
        else:
            gdf = gpd.read_file(file_path)
        
        center = gdf.dissolve().centroid
        center_lon, center_lat = center.x, center.y
          
        with col1:   
            fields = [ column for column in gdf.columns if column not in gdf.select_dtypes('geometry')]
            m = folium.Map(tiles='stamenterrain', location = [center_lat, center_lon], zoom_start=4)           
            folium.GeoJson(gdf, name = layer_name,  
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
        
        submitted = st.form_submit_button("Create Polygon Diagram for a Point Layer")        
        if submitted:
            # target = voronoi_diagram(gdf)
            target = centerline(gdf)
            with col2:
                if not target.empty: 
                    center = target.dissolve().centroid
                    center_lon, center_lat = center.x, center.y             
                    fields = [ column for column in target.columns if column not in target.select_dtypes('geometry')]
                    m = folium.Map(tiles='stamentoner', location = [center_lat, center_lon], zoom_start=4)
                    folium.GeoJson(target,  
                                   style_function = style_function, 
                                   highlight_function=highlight_function,                                   
                                   popup = folium.GeoJsonPopup(
                                   fields = fields
                                    )).add_to(m)
   
                    m.fit_bounds(m.get_bounds(), padding=(30, 30))
                    folium_static(m, width = 600)         
                    download_geojson(target, layer_name)   
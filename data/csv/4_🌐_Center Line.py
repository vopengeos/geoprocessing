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
from osgeo import ogr
from shapely.wkt import loads


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


def segmentize(geom):
    wkt = geom.wkt  # shapely Polygon to wkt
    geom = ogr.CreateGeometryFromWkt(wkt)  # create ogr geometry
    geom.Segmentize(0.00001 )  # ~1.11 m in WGS84 CRS
    # geom.Segmentize(1)  # 1m in EPSG:3857 CRS
    wkt2 = geom.ExportToWkt()  # ogr geometry to wkt
    new = loads(wkt2)  # wkt to shapely Polygon
    return new

def voronoi_polygon(source):  
    minx, miny, maxx, maxy = source.total_bounds
    bound = Polygon([(minx, miny),
                        (maxx, miny),
                        (maxx, maxy),
                        (minx, maxy)])
    points = MultiPoint(source.geometry.to_list())
    voronoi = voronoi_diagram(points , envelope=bound)
    # st.write(voronoi.geoms)
    voronoi_geometry  = {'geometry':voronoi.geoms}
    target = gpd.GeoDataFrame(voronoi_geometry, crs = source.crs)
    return target

def explodeLine(row):
    """A function to return all segments of a line as a list of linestrings"""
    coords = row.geometry.coords #Create a list of all line node coordinates
    parts = []
    for part in zip(coords, coords[1:]): #For each start and end coordinate pair
        parts.append(LineString(part)) #Create a linestring and append to parts list
    return parts
        
def centerline_create(source):
    source['geometry'] = source['geometry'].map(segmentize)
    source = source.explode(index_parts=False)
    col = source.columns.tolist()
    points = gpd.GeoDataFrame(columns=col)
    for index, row in source.iterrows():
        for j in list(row['geometry'].exterior.coords): 
            points = points.append({'geometry':Point(j)},ignore_index=True)

    points = points.set_crs(source.crs)
    # points = points.set_crs('epsg:3857')
    vor_polygon = voronoi_polygon(points)
    vor_polygon['geometry'] = vor_polygon.geometry.boundary
    dfline = gpd.GeoDataFrame(data=vor_polygon, geometry='geometry')
    dfline['tempgeom'] = dfline.apply(lambda x: explodeLine(x), axis=1) #Create a list of all line segments
    dfline = dfline.explode('tempgeom') #Explode it so each segment becomes a row (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html)

    dfline = gpd.GeoDataFrame(data=dfline, geometry='tempgeom')
    dfline = dfline.drop('geometry', axis=1)
    dfline.crs = source.crs #Dont know why this is needed
    
    centerline_candidate = gpd.sjoin(dfline,source, predicate='within') #for each point index in the points, it stores the polygon index containing that point
    # st.write(centerline_candidate)
    center_line = centerline_candidate.dissolve(by='index_right')
    return center_line

def centerline(source): 
    if (source.geometry.type == 'MultiPolygon').all():
        source = source.explode(index_parts=False)
        center_line_singlepart = centerline_create(source)        
        center_line = center_line_singlepart.dissolve(by = center_line_singlepart.index)
        return center_line

    elif (source.geometry.type == 'Polygon').all():
        center_line = centerline_create(source)  
        return  center_line


form = st.form(key="center_line")
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
            m = folium.Map(tiles='stamenterrain', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)           
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
        
        submitted = st.form_submit_button("Create Center Lines")        
        if submitted:
            target = centerline(gdf)
            with col2:
                if not target.empty: 
                    center = target.dissolve().centroid
                    center_lon, center_lat = center.x, center.y             
                    fields = [ column for column in target.columns if column not in target.select_dtypes('geometry')]
                    m = folium.Map(tiles='stamentoner', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)
                    folium.GeoJson(target,  
                                   style_function = style_function, 
                                   highlight_function=highlight_function,                                   
                                   popup = folium.GeoJsonPopup(
                                   fields = fields
                                    )).add_to(m)
   
                    m.fit_bounds(m.get_bounds(), padding=(30, 30))
                    folium_static(m, width = 600)         
                    download_geojson(target, layer_name)   
import folium
from streamlit_folium import folium_static
import streamlit as st
import streamlit_ext as ste
import geopandas as gpd
import pandas as pd
import fiona, os
from shapely.geometry import Point, MultiPoint, LineString, Polygon, LinearRing
from shapely.ops import transform, voronoi_diagram
from shapely.wkt import loads
import numpy as np

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
st.write('Create Center Line for Polygon')
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
    return geom.segmentize(max_segment_length=2) # meters

def simplify(geom):  
    return geom.simplify(0.1) # meters

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

def polygon_vertices(polygon):
    coords_exterior = list(polygon.exterior.coords)
    vertices = [Point(p[0], p[1]) for p in coords_exterior] 
    # st.write(vertices)
    return vertices
        
def centerline_create(source, vertices):
    # Origin CRS
    origin_crs = source.crs
    # Densify Polygon
    source = source.to_crs(3857) # to set max_segment_length in meters
    source['geometry'] = source['geometry'].map(segmentize)       
    
    # Extract Polygon's vertices
    col = source.columns.tolist()
    vertices = gpd.GeoDataFrame(columns=col)
    for index, row in source.iterrows():
        for j in list(row['geometry'].exterior.coords): 
            vertice = gpd.GeoDataFrame(geometry=[Point(j)]) 
            vertices = pd.concat([vertices, vertice])

    # Create Voronoi Polygon and convert to Polyline    
    voronoi_diagram = voronoi_polygon(vertices)
    voronoi_diagram['geometry'] = voronoi_diagram.geometry.boundary

    # Explode Voronoi Diagram into line segments
    voronoi_exploded = voronoi_diagram.copy()
    # voronoi_exploded = gpd.GeoDataFrame(data=voronoi_diagram, geometry='geometry', crs = source.crs)
    voronoi_exploded['geometry'] = voronoi_exploded.apply(lambda x: explodeLine(x), axis=1) #Create a list of all line segments
    voronoi_exploded = voronoi_exploded.explode('geometry') #Explode it so each segment becomes a row (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html)
    voronoi_exploded = gpd.GeoDataFrame(data=voronoi_exploded, geometry='geometry', crs = source.crs )


    # Find Center_line candidates which are within its corresponding Polygon
    centerline_candidates = gpd.sjoin(voronoi_exploded,source, predicate='within') 
    
    # Merege center_line segments into one 
    centerline_candidates = centerline_candidates.to_crs(3857)
    centerline_candidates['geometry'] = centerline_candidates['geometry'].map(simplify)
    center_line = centerline_candidates.dissolve(by='index_right')
    source = source.to_crs(origin_crs)
    return center_line

def centerline(source): 
    if (source.geometry.type == 'MultiPolygon').all():
        # st.write('MultiPolygon')
        source = source.explode(index_parts=False)
        source_vertices = source.copy()
        source_vertices['geometry'] = source_vertices.geometry.map(polygon_vertices) 
        center_line_singlepart = centerline_create(source, source_vertices)        
        center_line = center_line_singlepart.dissolve(by = center_line_singlepart.index)
        return center_line

    elif (source.geometry.type == 'Polygon').all():
        # st.write('Polygon')
        source_vertices = source.copy()
        source_vertices['geometry'] = source_vertices.geometry.map(polygon_vertices) 
        center_line = centerline_create(source, source_vertices)  
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
        
        origin_crs = gdf.crs
        gdf.to_crs(3857)
        center = gdf.dissolve().centroid
        center_lon, center_lat = center.x, center.y
        gdf.to_crs(origin_crs)

        with col1:   
            fields = [ column for column in gdf.columns if column not in gdf.select_dtypes('geometry')]
            m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)           
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
                    m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)
                    folium.GeoJson(target,  
                                   style_function = style_function, 
                                   highlight_function=highlight_function,                                   
                                   popup = folium.GeoJsonPopup(
                                   fields = fields
                                    )).add_to(m)
   
                    m.fit_bounds(m.get_bounds(), padding=(30, 30))
                    folium_static(m, width = 600)     
                    target =  target.to_crs(origin_crs)
                    download_geojson(target, layer_name)   
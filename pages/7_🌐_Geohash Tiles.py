import folium, os
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import shapely.wkb as wkblib
import pandas as pd
import geopandas as gpd
import streamlit_ext as ste
import geojson
from geojson import MultiLineString
from  becalib import geohash
from shapely import geometry
import fiona

GEOHASH_PRECISION = 8

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
st.title("Geohash")
st.write('Geohash')
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


def is_geohash_in_bounding_box(current_geohash, bbox_coordinates):
    """Checks if the box of a geohash is inside the bounding box

    :param current_geohash: a geohash
    :param bbox_coordinates: bounding box coordinates
    :return: true if the the center of the geohash is in the bounding box
    """

    coordinates = geohash.decode(current_geohash)
    geohash_in_bounding_box = (bbox_coordinates[0] < coordinates[0] < bbox_coordinates[2]) and (
            bbox_coordinates[1] < coordinates[1] < bbox_coordinates[3])
    return geohash_in_bounding_box

def build_geohash_box(current_geohash):
    """Returns a GeoJSON Polygon for a given geohash

    :param current_geohash: a geohash
    :return: a list representation of th polygon
    """

    b = geohash.bbox(current_geohash)
    polygon = [(b['w'], b['s']), (b['w'], b['n']), (b['e'], b['n']), (b['e'], b['s'],), (b['w'], b['s'])]
    return polygon

def compute_geohash_tiles(bbox_coordinates):
    """Computes all geohash tile in the given bounding box

    :param bbox_coordinates: the bounding box coordinates of the geohashes
    :return: a list of geohashes
    """

    checked_geohashes = set()
    geohash_stack = set()
    geohashes = []
    # get center of bounding box, assuming the earth is flat ;)
    center_latitude = (bbox_coordinates[0] + bbox_coordinates[2]) / 2
    center_longitude = (bbox_coordinates[1] + bbox_coordinates[3]) / 2

    center_geohash = geohash.encode(center_latitude, center_longitude, precision=GEOHASH_PRECISION)
    geohashes.append(center_geohash)
    geohash_stack.add(center_geohash)
    checked_geohashes.add(center_geohash)
    while len(geohash_stack) > 0:
        current_geohash = geohash_stack.pop()
        neighbors = geohash.neighbors(current_geohash)
        for neighbor in neighbors:
            if neighbor not in checked_geohashes and is_geohash_in_bounding_box(neighbor, bbox_coordinates):
                geohashes.append(neighbor)
                geohash_stack.add(neighbor)
                checked_geohashes.add(neighbor)
    return geohashes


# def write_geohash_layer(geohashes):
#     """Writes a grid layer based on the geohashes

#     :param geohashes: a list of geohashes
#     """

#     layer = MultiLineString([build_geohash_box(gh) for gh in geohashes])
#     with open('ghash_berlin_bbox.json', 'wb') as f:
#         f.write(geojson.dumps(ghash_polygon, sort_keys=True).encode('utf-8'))

def compute_geohash_tiles_from_polygon(polygon):
    # convert GeoSeries to shapely geometry
    """Computes all hex tile in the given polygon
    :param polygon: the polygon
    :return: a list of geohashes
    """

    checked_geohashes = set()
    geohash_stack = set()
    geohashes = []
    # get center of bounding, assuming the earth is flat ;)
    center_latitude = polygon.centroid.coords[0][1]
    center_longitude = polygon.centroid.coords[0][0]

    center_geohash = geohash.encode(center_latitude, center_longitude, precision=GEOHASH_PRECISION)
    geohashes.append(center_geohash)
    geohash_stack.add(center_geohash)
    checked_geohashes.add(center_geohash)
    while len(geohash_stack) > 0:
        current_geohash = geohash_stack.pop()
        neighbors = geohash.neighbors(current_geohash)
        for neighbor in neighbors:
            point = geometry.Point(geohash.decode(neighbor)[::-1])
            if neighbor not in checked_geohashes and polygon.contains(point):
                geohashes.append(neighbor)
                geohash_stack.add(neighbor)
                checked_geohashes.add(neighbor)
    return geohashes

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

def create_geohash_grid(min_lat, max_lat, min_lon, max_lon, precision):
    grid = {}
    
    # Encode the corners of the bounding box
    sw = geohash.encode(min_lat, min_lon, precision=precision)
    ne = geohash.encode(max_lat, max_lon, precision=precision)
    
    # Decode the geohashes to get the latitudes and longitudes
    sw_lat, sw_lon= geohash.decode(sw)
    ne_lat, ne_lon = geohash.decode(ne)
    
    # Iterate through the rows and columns of the grid
    for lat in range(int(sw_lat), int(ne_lat) + 1):
        for lon in range(int(sw_lon), int(ne_lon) + 1):
            # Encode each cell's center to get the geohash
            cell_center_lat = lat + 0.5
            cell_center_lon = lon + 0.5
            cell_geohash = geohash.encode(cell_center_lat, cell_center_lon, precision=precision)
            
            # Add the geohash to the grid
            if cell_geohash not in grid:
                grid[cell_geohash] = {'latitude': cell_center_lat, 'longitude': cell_center_lon}
    
    return grid



min_latitude = 37.0
max_latitude = 38.0
min_longitude = -122.0
max_longitude = -121.0
precision = 12

grid = create_geohash_grid(min_latitude, max_latitude, min_longitude, max_longitude, precision)

# Print the grid
for geohash, coordinates in grid.items():
    st.write(f"Geohash: {geohash}, Coordinates: {coordinates}")


# form = st.form(key="geohash")
# with form:   
#     url = st.text_input(
#             "Enter a URL to a polygon dataset",
#             "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/vn_vietnam.geojson",
#         )

#     uploaded_file = st.file_uploader(
#             "Upload a polygon dataset", type=["geojson", "kml", "zip", "tab"]
#         )

#     if  url or uploaded_file:
#         if url:
#             file_path = url
#             layer_name = url.split("/")[-1].split(".")[0]
#         if uploaded_file:
#             file_path = save_uploaded_file(uploaded_file, uploaded_file.name)
#             layer_name = os.path.splitext(uploaded_file.name)[0]    

#         if file_path.lower().endswith(".kml"):
#             fiona.drvsupport.supported_drivers["KML"] = "rw"
#             gdf = gpd.read_file(file_path, driver="KML")
#         else:
#             gdf = gpd.read_file(file_path)
        
#         origin_crs = gdf.crs
#         gdf.to_crs(3857)
#         center = gdf.dissolve().centroid
#         center_lon, center_lat = center.x, center.y
#         gdf.to_crs(origin_crs)

#         with col1:   
#             fields = [ column for column in gdf.columns if column not in gdf.select_dtypes('geometry')]
#             m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)           
#             folium.GeoJson(gdf, name = layer_name,  
#                            style_function = style_function, 
#                            highlight_function=highlight_function,
#                            marker = folium.Marker(icon=folium.Icon(
#                                      icon='ok-circle',
#                                      color = 'purple'
#                                      )),     
#                             # marker =  folium.CircleMarker(fill=True),
#                             # zoom_on_click = True,
#                            popup = folium.GeoJsonPopup(
#                            fields = fields
#                             )).add_to(m)
           
#             m.fit_bounds(m.get_bounds(), padding=(30, 30))
#             folium_static(m, width = 600)
        
#         submitted = st.form_submit_button("Create Geohash Tiles")        
#         if submitted:
#             # target = create_centerline(gdf,1)            
#             target = compute_geohash_tiles_from_polygon(gdf)
#             st.write(target)
#             with col2:
#                 if not target.empty: 
#                     center = target.dissolve().centroid
#                     center_lon, center_lat = center.x, center.y             
#                     fields = [ column for column in target.columns if column not in target.select_dtypes('geometry')]
#                     m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4, max_zoom = 20)
#                     folium.GeoJson(target,  
#                                    style_function = style_function, 
#                                    highlight_function=highlight_function,                                   
#                                    popup = folium.GeoJsonPopup(
#                                    fields = fields
#                                     )).add_to(m)
   
#                     m.fit_bounds(m.get_bounds(), padding=(30, 30))
#                     folium_static(m, width = 600)     
#                     target =  target.to_crs(origin_crs)
#                     download_geojson(target, layer_name)   
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
st.title("Largest Empty Circle")
st.write('largest Empty Circle of a Point Set')
col1, col2 = st.columns(2)    

def download_center(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download LEC's center",
                file_name= 'lec_center_' + layer_name+ '.geojson',
                mime="application/json",
                data=geojson
            ) 

def download_lec(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download LEC",
                file_name= 'lec_' + layer_name+ '.geojson',
                mime="application/json",
                data=geojson
            ) 


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



def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371.009 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def great_circle(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 6371.009 * (
        acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2))
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

form = st.form(key="largest_empty_circle")
with form:   
    url = st.text_input(
            "Enter a URL to a point dataset",
            "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/vn_cities.geojson",
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
            m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4)           
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
        
        submitted = st.form_submit_button("Create Largest Empty Circle")        
        if submitted:
            #################
            # Create Voronoi Polygon
            voronoi = voronoi_polygon(source)

            #################
             # Create Convex Hull
            convex_hull_geom = source.unary_union.convex_hull
            convex_hull = gpd.GeoDataFrame(geometry=gpd.GeoSeries(convex_hull_geom),crs = source.crs)
            
            #################
            # Extract Convex Hull Vertices
            convex_hull_coords = convex_hull.get_coordinates()
            convex_hull_points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(convex_hull_coords['x'], convex_hull_coords['y'],crs = source.crs))
            convex_hull_points = convex_hull_points.drop_duplicates() 
           
           #################
            # Clip voronoi with convex_hull and extract intersection vertices which are candidates of LEC's center
            clip = gpd.clip(voronoi, convex_hull)
            clip_points = clip.get_coordinates()
            center_candidates = gpd.GeoDataFrame(geometry=gpd.points_from_xy(clip_points['x'], clip_points['y'], crs = source.crs))
            center_candidates = center_candidates.drop_duplicates() 

            #################
            # Get LEC and LEC centroid
            # center_candidates = center_candidates.to_crs(3857) # to calculate distance in meters
            # source = source.to_crs(3857)  # to calculate distance in meters

            lec_center = gpd.sjoin_nearest(center_candidates, source,distance_col="radius")                              
            lec_center = lec_center[lec_center['radius'] == lec_center['radius'].max()]
            lec_center = lec_center.head(1) # ensure that just only one center is determined as LEC's center
            # st.write(lec_center)
            lec = lec_center.copy()           
            lec['geometry'] = lec['geometry'].buffer(lec['radius'])

            with col2:                             
                map_center = source.dissolve().centroid
                center_lon, center_lat = map_center.x, map_center.y             
                fields = [ column for column in source.columns if column not in source.select_dtypes('geometry')]
                m = folium.Map(tiles='cartodbpositron', location = [center_lat, center_lon], zoom_start=4)
                                          
                folium.GeoJson(clip,  
                                style_function = style_function, 
                                highlight_function=highlight_function,                                   
                                ).add_to(m)
                
                folium.GeoJson(lec_center,  
                                marker = folium.Marker(icon=folium.Icon(
                                    icon='ok-circle',
                                    color = 'green'
                                    )),  
                                style_function = style_function, 
                                highlight_function=highlight_function                                   
                                ).add_to(m)
                
                folium.GeoJson(lec,                                    
                                style_function = style_function, 
                                highlight_function=highlight_function                                   
                                ).add_to(m)
                
                folium.GeoJson(source,  
                                marker = folium.Marker(icon=folium.Icon(
                                    icon='ok-circle',
                                    color = 'purple'
                                    )),  
                                style_function = style_function, 
                                highlight_function=highlight_function,                                   
                                popup = folium.GeoJsonPopup(
                                fields = fields
                                )).add_to(m)

                m.fit_bounds(m.get_bounds(), padding=(30, 30))
                folium_static(m, width = 600)  
                # 
                st.write('Largest Empty Circle Raidus (approximately for distance near the equator): ', round(lec_center['radius'].iloc[0]*111139* 10**(-3),2), ' km') 
                # st.write('Largest Empty Circle Raidus: ', round(lec_center['radius'].iloc[0]*10**(-3),2), ' km') 
                # st.write (haversine(103.609, 14.612, 106.098998559197867, 11.318869769511060))
                # st.write (great_circle(103.609, 14.612, 106.098998559197867, 11.318869769511060))
                download_center(lec_center, layer_name)  
                download_lec(lec, layer_name) 
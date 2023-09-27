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
# from shapely.ops import transform
from shapely.ops import voronoi_diagram
from scipy.spatial import Voronoi, ConvexHull, distance_matrix


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
st.title("Largest Empty Circle")
st.write('largest Empty Circle of a Point Set')
col1, col2 = st.columns(2)    

def download_center(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download LEC's center",
                file_name= 'center_' + layer_name+ '.geojson',
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

import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d


def poly_to_points(poly):
    return poly.exterior.coords

form = st.form(key="largestemptycircle")
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
        
        submitted = st.form_submit_button("Create Largest Empty Circle")        
        if submitted:
            # target = voronoi_diagram(gdf)
            geoms = []
            voronoi = voronoi_polygon(gdf)
            for index,row in gdf.iterrows(): 
                geoms.append(shape(row.geometry)) 

            list_arrays = [ np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geoms ]
            convex_hull_geoms = ConvexHull(list_arrays)
            # convex_hull = gpd.GeoDataFrame({'geometry':convex_hull_geoms}, crs = gdf.crs)
            # convex_hull = gdf
            # st.write(convex_hull_geoms)
            polylist = []
            for idx in convex_hull_geoms.vertices: #Indices of points forming the vertices of the convex hull.
                polylist.append(list_arrays[idx]) #Append this index point to list

            p = Polygon(polylist)
            df = pd.DataFrame({'hull':[1]})
            df['geometry'] = p
            convex_hull = gpd.GeoDataFrame(df, crs=gdf.crs, geometry='geometry')
            convex_hull_points = convex_hull.get_coordinates()
            df = pd.DataFrame(convex_hull_points)
            convex_hull_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['x'], df['y'], crs = gdf.crs))
            convex_hull_points = convex_hull_points.drop_duplicates() 
            clip = gpd.clip(voronoi, convex_hull)
            col = clip.columns.tolist()
            # new GeoDataFrame with same columns
            nodes = gpd.GeoDataFrame(columns=col)
            # Extraction of the polygon nodes and attributes values from polys and integration into the new GeoDataFrame
            for index, row in clip.iterrows():
                for j in list(row['geometry'].exterior.coords): 
                    nodes = nodes.append({'geometry':Point(j) },ignore_index=True)
            nodes = nodes.set_crs(gdf.crs)
            nodes = nodes.drop_duplicates()            
            nearest = gpd.sjoin_nearest(nodes, gdf,distance_col="distance")                              
            nearest = nearest[nearest['distance'] == nearest['distance'].max()]
            # st.write(nearest)
            # circle =nearest['geometry'].buffer(nearest['distance'])
            # st.write(circle)     
            # df = pd.DataFrame(circle)
            # lec = gpd.GeoDataFrame(df, geometry=circle, crs = gdf.crs)

            lec = nearest.copy()
            lec['geometry'] = nearest['geometry'].buffer(nearest['distance'])


            # target = clip  
            ################################
            # convex_hull_points = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry))
            with col2:                
                center = gdf.dissolve().centroid
                center_lon, center_lat = center.x, center.y             
                fields = [ column for column in gdf.columns if column not in gdf.select_dtypes('geometry')]
                m = folium.Map(tiles='stamentoner', location = [center_lat, center_lon], zoom_start=4)
                
                folium.GeoJson(nodes,  
                                style_function = style_function, 
                                highlight_function=highlight_function,   
                                marker = folium.Marker(icon=folium.Icon(
                                    icon='ok-circle',
                                    color = 'red'
                                    ))
                                ).add_to(m)
                
                folium.GeoJson(convex_hull,  
                                style_function = style_function, 
                                highlight_function=highlight_function                                   
                                ).add_to(m)
                
                folium.GeoJson(voronoi,  
                                style_function = style_function, 
                                highlight_function=highlight_function,                                   
                                ).add_to(m)
                
                folium.GeoJson(nearest,  
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
                
                # folium.GeoJson(gdf,  
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
                download_center(nearest, layer_name)  
                download_lec(lec, layer_name) 
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
from sklearn.cluster import KMeans



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
st.title("Split Polygon")
st.write('Split Polygon layer into almost equal parts using Voronoi Diagram')
col1, col2 = st.columns(2)    

def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        with col2:
            ste.download_button(
                label="Download GeoJSON",
                file_name= 'splitted_' + layer_name+ '.geojson',
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

def random_points_in_polygon(polygon, number):
    points = []
    min_x, min_y, max_x, max_y = polygon.bounds
    i= 0
    while i < number:
        point = Point(np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y))
        if polygon.contains(point):
            points.append(point)
            i += 1
    target = gpd.GeoDataFrame({'geometry': points},crs = 'epsg:4326')
    # return points  # returns list of shapely point
    return target 

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


def splitpolygon(source, parts, random_points):	
    #target = source
    # target = random_points_in_polygon(source)
    # target['geometry'] = target['geometry'].map(random_points_in_polygon)
    # target = []
    # for i in source.index:
    # target = source
    target = random_points_in_polygon(source.iloc[0].geometry, random_points)
    a=pd.Series(target['geometry'].apply(lambda p: p.x))
    b=pd.Series(target['geometry'].apply(lambda p: p.y))
    X=np.column_stack((a,b))
    # st.write(X)
    wcss = []
    for i in range(1, 14):
        kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)
    # st.write(wcss)
    kmeans = KMeans(n_clusters = parts, init = 'k-means++', random_state = 100,  max_iter=400)
    y_kmeans = kmeans.fit_predict(X)
    k=pd.DataFrame(y_kmeans, columns=['cluster'])
    target=target.join(k)

    target = target.dissolve(by = target.cluster)
    # centroids = target.centroid
    target['geometry'] = target.geometry.centroid
    target = voronoi_polygon(target)
    target = gpd.overlay(source, target, how='intersection')
    return target              
    # target['geometry'] = target['geometry'].map(random_points_in_polygon)
    #     target.append(random_points_in_polygon(source.iloc[i].geometry, 100))
    # st.write(points)
    # target['geometry'] = target['geometry'].map(sample_random_geo)
    # st.write(target)
    # final = gpd.GeoDataFrame(geometry= MultiPointtarget,crs =source.crs)
    # parameters2 =  {'INPUT': points['OUTPUT'],
    #             'CLUSTERS' :parts,
    #             'FIELD_NAME' : 'CLUSTER_ID',
    #             'SIZE_FIELD_NAME' : 'CLUSTER_SIZE',
    #             'OUTPUT' : 'memory:kmeansclustering'} 
    # kmeansclustering = processing.run('qgis:kmeansclustering', parameters2)

    # parameters3 = {'INPUT': kmeansclustering['OUTPUT'],                  
    #             'GROUP_BY' : 'CLUSTER_ID',
    #             'AGGREGATES' : [],
    #             'OUTPUT' : 'memory:aggregate'} 
    # aggregate = processing.run('qgis:aggregate',parameters3)

    # parameters4 = {'INPUT': aggregate['OUTPUT'],                  
    #             'ALL_PARTS' : False,
    #             'OUTPUT' : 'memory:centroids'} 
    # centroids = processing.run('qgis:centroids',parameters4)

    # parameters5 = {'INPUT': centroids['OUTPUT'],                  
    #             'BUFFER' : 1000,
    #             'OUTPUT' : 'memory:voronoi'} 
    # voronoi = processing.run('qgis:voronoipolygons',parameters5)

    # parameters6 = {'INPUT': layer,  
    #             'OVERLAY':   voronoi['OUTPUT'],           
    #             'OUTPUT' : 'TEMPORARY_OUTPUT'
    #         } 
    # intersection = processing.run('qgis:intersection',parameters6)
    # output = intersection['OUTPUT']
    # return output


form = st.form(key="split_polygon")
with form:   
    url = st.text_input(
            "Enter a URL to a point dataset",
            "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/polygon_split.geojson",
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
        
        submitted = st.form_submit_button("Split Polygons")        
        if submitted:
            # target = voronoi_diagram(gdf)
            target = splitpolygon(gdf,20,200)
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
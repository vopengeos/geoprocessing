import folium
from streamlit_folium import folium_static
import streamlit as st
import streamlit_ext as ste
import geopandas as gpd
import fiona,os, shapely
from centerline.geometry import Centerline
from shapely.geometry import LineString, Polygon, Point, mapping
from timeit import default_timer as timer
from shapely import wkt
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
def coord_lister(geom):
    coords = list(geom.exterior.coords)
    return (coords)



def create_centerline2(gdf):
    coordinate_list = gdf.geometry.get_coordinates() 
    st.write(coordinate_list)
    # polygon = Polygon(((0., 0.), (0., 10.), (10., 10.), (10., 0.), (0., 0.)))
    polygon = Polygon([coordinate_list])
    centerline = Centerline(polygon)
    centerline_geometry  = {'geometry':centerline.geometry.geoms}
    target = gpd.GeoDataFrame(centerline_geometry, crs = gdf.crs)
    return target

def create_centerline(gdf, interpolation_distance=0.001):
   #find the voronoi verticies (equivalent to Centerline._get_voronoi_vertices_and_ridges())
   borders = gdf.segmentize(interpolation_distance) #To have smaler verticies (equivalent to Centerline._get_densified_borders())
#    st.write(borders)
   voronoied = shapely.voronoi_polygons(borders,only_edges=True) #equivalent to the scipy.spatial.Voronoi
#    st.write(voronoied)
   voronoi_geometry  = {'geometry':voronoied}
   centerline_candidates = gpd.GeoDataFrame(voronoi_geometry, crs = 'epsg:4326')
   centerline_candidates = centerline_candidates.explode('geometry') #Explode it so each segment becomes a row (https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.explode.html)
   centerline_candidates = gpd.GeoDataFrame(data=centerline_candidates, geometry='geometry', crs = gdf.crs )
#    st.write(centerline_candidates)
   centerlines = centerline_candidates.sjoin(gdf,predicate="within")
#    centerlines = centerlines.dissolve(by='index_right')
   return centerlines



form = st.form(key="center_line")
with form:   
    url = st.text_input(
            "Enter a URL to a point dataset",
            "https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/polygon_centerline2.geojson",
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
            # target = create_centerline(gdf,1)
            start = timer()
            # target = create_centerline2(gdf)
            end = timer()
            target = create_centerline(gdf,interpolation_distance=0.00001)
            end2 = timer()
            st.write(f" Duration current implementation : {end-start:0.3f}s \n Duration proposed implementation : {end2-end:0.3f}s")

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
                    target =  target.to_crs(origin_crs)
                    download_geojson(target, layer_name)   
import folium
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
from folium.plugins import Fullscreen
import streamlit_ext as ste

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
st.title("Distance Calculator")
st.write('Distance Calculator for GPS Track Logs')
start_time = '2023-01-01 00:00:00'
end_time = '2023-12-31 00:00:00'
MAX_ALLOWED_TIME_GAP = 300  # seconds
MAX_ALLOWED_DISTANCE_GAP = 10000000000000  # meters
col1, col2 = st.columns(2)

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

def preProcessing(data, start_time, end_time, formular):    
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    timestamp_format2 = "%d-%m-%Y %H:%M"
    start = datetime.strptime(start_time, timestamp_format)
    #print(start)
    end = datetime.strptime(end_time, timestamp_format)
    #print(end)
    filtered = data
    
    filtered['datetime'] = pd.to_datetime(filtered['datetime'])

    mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2) | (filtered['motionActivity'] == 32) | (filtered['motionActivity'] == 64) | (filtered['motionActivity'] == 128))
    if formular == 'old': 
        mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2))
    
    filtered = filtered.loc[mask]
    
    filtered = filtered.sort_values('datetime').reset_index().drop('index', axis=1)
    print('First point:', str(data.iloc[0].latitude) + ', ' + str(data.iloc[0].longitude))
    print('Last point:', str(data.iloc[-1].latitude) + ', ' + str(data.iloc[-1].longitude))
    filtered['date_string'] = pd.to_datetime(filtered['datetime']).dt.date    
    return filtered

def preProcessing2(data, start_time, end_time, formular):    
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_time, timestamp_format)
    #print(start)
    end = datetime.strptime(end_time, timestamp_format)
    #print(end)
    filtered = data    
    filtered['datetime'] = pd.to_datetime(filtered['datetime'])

    mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2) | (filtered['motionActivity'] == 32) | (filtered['motionActivity'] == 64) | (filtered['motionActivity'] == 128))
    if formular == 'old': 
        mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2))
    
    filtered = filtered.loc[mask]
    
    filtered = filtered.sort_values('datetime').reset_index().drop('index', axis=1)
    print('First point:', str(data.iloc[0].latitude) + ', ' + str(data.iloc[0].longitude))
    print('Last point:', str(data.iloc[-1].latitude) + ', ' + str(data.iloc[-1].longitude))
    filtered['date_string'] = pd.to_datetime(filtered['datetime']).dt.date    
    # st.write(filtered)
    return filtered

def traveledDistance(data):
    totalDistance = 0
    coordinates = []
    for i in range (1, len(data)):
        timediff = (datetime.strptime(str(data.iloc[i].datetime), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].datetime), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_temp = greatCircle(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        # distance_temp = haversine(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        distance_temp = geopy.distance.geodesic((data.iloc[i].latitude, data.iloc[i].longitude), (data.iloc[i - 1].latitude, data.iloc[i - 1].longitude)).m
        
        if timediff > MAX_ALLOWED_TIME_GAP or distance_temp > MAX_ALLOWED_DISTANCE_GAP:
            #distance_temp = 0
            coor = [[data.iloc[i - 1].longitude, data.iloc[i - 1].latitude], [data.iloc[i].longitude, data.iloc[i].latitude], ]
            api = OSRM(base_url="https://router.project-osrm.org/")
            # print(data.iloc[i - 1].longitude, data.iloc[i - 1].latitude, data.iloc[i].longitude, data.iloc[i].latitude, )
            route = api.directions(
            profile='car',
            locations= coor       
            )
            distance_temp = route.distance
            # distance_temp = 0
        # Access the route properties with .geometry, .duration, .distance                  
        # print("Loop:", i, "timediff:", timediff, "Distance Temp:", distance_temp, "Motion Activity:", data.iloc[i].motionActivity)
        totalDistance += distance_temp
        
    return round(totalDistance/1000, 3)

def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download GeoJSON",
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 

with col1:
    form = st.form(key="distance_calculator")
    with form: 
        url = st.text_input(
                "Enter a CSV URL with Latitude and Longitude Columns",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/gps.csv'
            )
        uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
        lat_column_index, lon_column_index = 0,0     
        if url:   
            df = pd.read_csv(url,skiprows=[1],encoding = "UTF-8")                
        if uploaded_file:        
            df = pd.read_csv(uploaded_file,skiprows=[1],encoding = "UTF-8")
        m = folium.Map(max_zoom = 21,
                    tiles='stamenterrain',
                    zoom_start=14,
                    control_scale=True
                    )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)

        for index, row in df.iterrows():
            popup = row.to_frame().to_html()
            folium.Marker([row['latitude'], row['longitude']], 
                        popup=popup,
                        icon=folium.Icon(icon='cloud')
                        ).add_to(m)        
            
        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        # download_geojson(df, 'nodes')
        submitted = st.form_submit_button("Calculate Distance")    


def CalculateDistance(data, groupBy):        
    grouped = data.groupby(groupBy)
    result = grouped.apply(traveledDistance)
    return result.values[0]


if submitted:
    with col2:
        st.write('Step 1/2: Preprocessing')
        df = preProcessing2(df, start_time, end_time, 'new') 
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['date_string'] = df['date_string'].astype(str)

        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        trackpoints_cleaned = gdp.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')
        trackpoints_cleaned_fields = [ column for column in trackpoints_cleaned.columns if column not in trackpoints_cleaned.select_dtypes('geometry')]

        # aggregate these points with the GrouBy
        # folium.GeoJson(geo_df_cleaned).add_to(m)
        # folium_static(m, width = 800)
        # download_geojson(geo_df_cleaned, 'track_points_cleaned')

        st.write('Step 2/2: Distance Calculation')
        groupBy = ['driver', 'date_string']
        st.write('Distance traveled:', str(CalculateDistance(df, groupBy)), ' km') 

        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        geo_df = gdp.GeoDataFrame(df, geometry=geometry)
        # aggregate these points with the GrouBy
        geo_df = geo_df.groupby(['driver', 'date_string'])['geometry'].apply(lambda x: LineString(x.tolist()))
        track_distance = gdp.GeoDataFrame(geo_df, geometry='geometry', crs = 'EPSG:4326')

        center = track_distance.dissolve().centroid
        center_lon, center_lat = center.x, center.y        
        m = folium.Map(max_zoom = 21,
                        tiles='stamentoner',
                        location = [center_lat, center_lon],
                        zoom_start=14,
                        control_scale=True
                        )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)

        folium.GeoJson(trackpoints_cleaned, name = 'track_points_cleaned',  
                        style_function = style_function, 
                        highlight_function=highlight_function,
                        marker = folium.Marker(icon=folium.Icon(
                                    icon='ok-circle',
                                    color = 'purple',
                                    size = 5
                                    )),     
                        # marker =  folium.CircleMarker(fill=True),
                        # zoom_on_click = True,
                        popup = folium.GeoJsonPopup(
                        fields = trackpoints_cleaned_fields
                        )).add_to(m)

        folium.GeoJson(track_distance, name = 'track_distance',  
                        style_function = style_function, 
                        highlight_function=highlight_function,
                        # popup = folium.GeoJsonPopup(
                        # fields = tracpoints_cleaned_fields
                        # )
                        ).add_to(m)

        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        download_geojson(track_distance, 'track')
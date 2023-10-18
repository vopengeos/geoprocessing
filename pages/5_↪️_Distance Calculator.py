import folium, os
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
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
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
st.title("Distance Calculator")
st.write('Distance Calculator for GPS Track Logs')
start_time = '2023-01-01 00:00:00'
start_time = '2019-01-01 00:00:00'
end_time = '2023-12-31 00:00:00'
MAX_ALLOWED_TIME_GAP = 300  # seconds
MAX_ALLOWED_DISTANCE_GAP = 10000000000000  # meters
col1, col2 = st.columns(2)

shortestpath_geometries = []
dict_ = {"time": [], "distance": [], "duration": [], "speed": []}


def style_function(feature):
    return {
        'fillColor': '#b1ddf9',
        'fillOpacity': 0.5,
        'color': 'blue',
        'weight': 2,
        # 'dashArray': '5, 5'
    }

def style_function2(feature):
    return {
        'fillColor': '#b1dda3',
        'fillOpacity': 0.5,
        'color': 'red',
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

def statistics(trackpoints):
    totalDistance = 0
    trackpoints['datetime'] = pd.to_datetime(trackpoints['datetime']).dt.tz_localize(None)
    for i in range (1, len(trackpoints)):
        distance_temp = geopy.distance.geodesic((trackpoints.iloc[i-1].latitude, trackpoints.iloc[i-1].longitude), (trackpoints.iloc[i].latitude, trackpoints.iloc[i].longitude)).m
        totalDistance += distance_temp      
    
    totalDistance =  round(totalDistance/1000, 3)
    st.write ('Total distance without any filters: ', totalDistance, ' km')
    totalTime =  (datetime.strptime(str(trackpoints.iloc[-1].datetime), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(trackpoints.iloc[0].datetime), '%Y-%m-%d %H:%M:%S')).total_seconds()/60
    st.write ('Total time: ', round(totalTime,2), ' minutes')
    if totalTime > 0 :
        st.write ('Average Speed: ', round(totalDistance/(totalTime/60),2), (' km/h'))
    
    st.write('Number of track points: ', len(trackpoints))  
    st.write ('Number of duplicate datetime: ', trackpoints.duplicated(subset=["datetime"], keep='last').sum())
    st.write ('Number of duplicate lat and long: ', trackpoints.duplicated(subset=["latitude", "longitude"], keep='last').sum())
    st.write ('Number of duplicate datetime, lat and long: ', trackpoints.duplicated(subset=["datetime", "latitude", "longitude"], keep='last').sum())
    st.write ('Start time:', trackpoints.iloc[0].datetime)
    st.write ('End time:', trackpoints.iloc[-1].datetime)

    st.write(trackpoints)
    st.write('Activity types: ', trackpoints['motionActivity'].unique()) 


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

# def smooth(points):
#     kf = KalmanFilter(
#         initial_state_mean = points.iloc[0],
#         observation_covariance = np.diag([0.5, 0.5]) ** 2, # TODO: shouldn't be zero
#         transition_covariance = np.diag([0.3, 0.3]) ** 2, # TODO: shouldn't be zero
#         transition_matrices = [[1, 0], [0, 1]] # TODO
#     )
#     kalman_smoothed, _ = kf.smooth(points)
#     df = pd.DataFrame(data=kalman_smoothed, columns=['latitude', 'longitude'])
#     st.write(df)
#     return df

def removejumping(data): 
    filtered = data
    outliers_index = []
    st.write('Jumping points: ')
    for i in range (1, len(filtered)-1):  #except final jumping point! Ex: WayPoint_20230928142338.csv        
        time_diff = (datetime.strptime(str(data.iloc[i].datetime), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].datetime), '%Y-%m-%d %H:%M:%S')).total_seconds()
        distance_diff = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        # distance_diff = haversine(data.iloc[i-1].latitude, data.iloc[i-1].longitude, data.iloc[i].latitude, data.iloc[i].longitude)
        if time_diff > 0:
            velocity =  (distance_diff/1000)/(time_diff/3600) #km/h   
            # st.write(data.iloc[i-1].datetime, data.iloc[i].datetime,velocity,' km/h') 
            if velocity > 70 : #km/h,
                # filtered = filtered.drop([i])
                st.write('Current Point: ',  data.iloc[i-1].datetime, ' Jumping Point: ', data.iloc[i].datetime,' Time (seconds): ', round(time_diff, 2) , ' Distance (m): ', round(distance_diff,2), 'Velocity: ', round(velocity,2),' km/h')
                outliers_index.append(data.iloc[i].datetime)            
    # st.write(outliers_index)
    filtered = filtered[filtered.datetime.isin(outliers_index) == False]    
    return filtered


def preProcessing2(data, start_time, end_time, formular):
    st.write('Number of original track points: ', len(data))   
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_time, timestamp_format)
    #print(start)
    end = datetime.strptime(end_time, timestamp_format)
    #print(end)
    filtered = data

    ##############MotionActivity filter:  may delete "moving" track points
    mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2) | (filtered['motionActivity'] == 32) | (filtered['motionActivity'] == 64) | (filtered['motionActivity'] == 128))
    if formular == 'old': 
        mask = (filtered['datetime'] > start) & (filtered['datetime'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2))
    filtered = filtered.loc[mask]
    st.write('After filter Motion Activity: ', len(filtered))    


    # filtered['datetime'] = pd.to_datetime(filtered['datetime'])
    filtered['datetime'] = pd.to_datetime(filtered['datetime']).dt.tz_localize(None)
    ############## Drop duplicate track points (the same datetime)
    filtered = filtered.drop_duplicates(subset=["datetime"], keep='last')

    ############## Drop duplicate track points (the same latitude and longitude)
    filtered = filtered.drop_duplicates(subset=["latitude", "longitude"], keep='last') # except last point in case of return to sart point with the same lat long
    # filtered = filtered.drop_duplicates(subset=["latitude", "longitude"], keep='last') # except last point in case of return to sart point with the same lat long
    st.write('After delete duplicates: ', len(filtered))    

    ############## Drop "jumping" track points
    filtered = removejumping(filtered)
    st.write('After remove jumping points: ', len(filtered))    
  

    filtered['date_string'] = pd.to_datetime(filtered['datetime']).dt.date    
    st.write(filtered)
    return filtered    

def traveledDistance(data):
    totalDistance = 0
    count = 0
    shortestpath_index = []
    shortestpath_distance = []
    crowfly_distance = []
    for i in range (1, len(data)):
        velocity_diff = 0
        time_diff = (datetime.strptime(str(data.iloc[i].datetime), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].datetime), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_temp = greatCircle(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        # distance_temp = haversine((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        distance_temp = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        if time_diff>0:
            velocity_diff =  (distance_temp/1000)/(time_diff/3600) #km/h      
        # # if time_diff > MAX_ALLOWED_TIME_GAP or distance_temp > MAX_ALLOWED_DISTANCE_GAP:
        #     # #distance_temp = 0
        #     # st.write(data.iloc[i].datetime)        
        try:  
            if velocity_diff > 70 or time_diff > MAX_ALLOWED_TIME_GAP or distance_temp> 200:  #km/h , MAX_ALLOWED_TIME_GAP = 300s in case of GPS signals lost for more than MAX_ALLOWED_TIME_GAP seconds
                if velocity_diff > 5:
                    st.write(data.iloc[i-1].datetime)
                    st.write(data.iloc[i].datetime)
                    st.write('velocity: ',  velocity_diff)
                    st.write('time_diff: ', time_diff)
                    st.write('distance_temp:', distance_temp)
                    coor = [[data.iloc[i - 1].longitude, data.iloc[i - 1].latitude], [data.iloc[i].longitude, data.iloc[i].latitude]]
                    api = OSRM(base_url="https://routing.openstreetmap.de/routed-car/")
                    # print(data.iloc[i - 1].longitude, data.iloc[i - 1].latitude, data.iloc[i].longitude, data.iloc[i].latitude, )
                    route = api.directions(
                    profile='car',
                    locations= coor       
                    )
                    dict_["time"].append(data.iloc[i - 1].datetime)
                    dict_["distance"].append(route.distance)
                    dict_["duration"].append(route.duration)
                    if (route.duration > 0):
                        dict_["speed"].append((route.distance/1000)/(route.duration/3600)) # km/h
                    else: dict_["speed"].append(0)

                    crowfly_distance.append(round(distance_temp,2))
                    distance_temp = route.distance                
                    shortestpath_distance.append(round(route.distance,2))
                    shortestpath_index.append(data.iloc[i-1].datetime)  
                    shortestpath_index.append(data.iloc[i].datetime)  
                    
                    shortestpath_geometries.append(LineString(route.geometry))
                    count += 1
        except:
            pass
        # Access the route properties with .geometry, .duration, .distance                  
        # print("Loop:", i, "timediff:", time_diff, "Distance Temp:", distance_temp, "Motion Activity:", data.iloc[i].motionActivity)
        totalDistance += distance_temp
    st.write('Number of using shortest path in distance calculation: ', count, shortestpath_index,'Crow fly distance: ' , crowfly_distance, 'Shortest Path Distance: ', shortestpath_distance)
    return round(totalDistance/1000, 3)

def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download " + layer_name,
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 

with col1:
    form = st.form(key="distance_calculator")
    layer_name = 'track'
    with form: 
        url = st.text_input(
                "Enter a CSV URL with Latitude and Longitude Columns",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/gps_noise_2.csv'
            )
        uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
        lat_column_index, lon_column_index = 0,0     

        if url:   
            df = pd.read_csv(url,encoding = "UTF-8")    
            layer_name = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            df = pd.read_csv(uploaded_file,encoding = "UTF-8")
            layer_name = os.path.splitext(uploaded_file.name)[0]
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
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        trackpoints_origin = gdp.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')        
        download_geojson(trackpoints_origin,layer_name)
        submitted = st.form_submit_button("Calculate Distance")    
    


def CalculateDistance(data, groupBy):        
    grouped = data.groupby(groupBy)
    result = grouped.apply(traveledDistance)
    return result.values[0]


if submitted:
    with col1:
        statistics(df)
    with col2:        
        st.write('Step 1/2: Preprocessing')
        # df = smooth(df)
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
        st.write('Distance traveled:', CalculateDistance(df, groupBy), ' km') 

        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        geo_df = gdp.GeoDataFrame(df, geometry=geometry)
        # aggregate these points with the GrouBy
        geo_df = geo_df.groupby(['driver', 'date_string'])['geometry'].apply(lambda x: LineString(x.tolist()))
        track_distance = gdp.GeoDataFrame(geo_df, geometry='geometry', crs = 'EPSG:4326')

        center = track_distance.dissolve().centroid
        center_lon, center_lat = center.x, center.y        
        m = folium.Map(max_zoom = 21,
                        tiles='stamenterrain',
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
                                    color = 'green',
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

        routes_df = gpd.GeoDataFrame(dict_, geometry=shortestpath_geometries, crs="EPSG:4326")
        folium.GeoJson(routes_df, name = 'shortest_path',  
                        style_function = style_function2, 
                        highlight_function=highlight_function,
                        # popup = folium.GeoJsonPopup(
                        # fields = tracpoints_cleaned_fields
                        # )
                        ).add_to(m)
        
        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        download_geojson(trackpoints_cleaned, layer_name + '_cleaned')
        download_geojson(track_distance, layer_name + '_track')
        download_geojson(routes_df, layer_name + '_shortestpath')


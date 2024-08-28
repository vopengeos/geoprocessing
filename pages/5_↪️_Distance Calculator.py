import folium, os
from folium.plugins import Draw, BeautifyIcon  
import streamlit as st
from streamlit_folium import st_folium, folium_static
import pandas as pd
from datetime import datetime
import geopandas as gdp
from shapely.geometry import Point, LineString
from folium.plugins import Fullscreen
from pykalman import KalmanFilter

import streamlit_ext as ste
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
from math import radians, cos, sin, asin, sqrt
import requests, polyline

st.set_page_config(layout="wide")
st.title("Distance Calculator")
st.write('Distance Calculator for GPS Track Logs')
# start_time = '2023-01-01 00:00:00'
start_time = '2023-01-01 00:00:00'
end_time = '2025-12-30 00:00:00'
######## MAX_ALLOWED_TIME_GAP & MAX_ALLOWED_DISTANCE_GAP for 1 minute interval of trackpoints 
MAX_ALLOWED_TIME_GAP = 300  # seconds
MAX_ALLOWED_DISTANCE_GAP = 500  # meters
MAX_ALLOWED_DISTANCE_JUMPING = 1000  # meters

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
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    dist = c * r
    return  dist*1000 # meters


col1, col2 = st.columns(2)

route_geometries = []
shortestpath_dict = {"time": [], "distance": [], "duration": [], "speed": []}
routing_dict = {"time": [], "distance": []}


def style_track(feature):
    return {
        'fillColor': '#b1ddf9',
        'fillOpacity': 0.5,
        'color': 'blue',
        'weight': 2,
        # 'dashArray': '5, 5'
    }

# def style_trackpoints(feature):
#     return {
#         'fillColor': '#b1ddf9',
#         'fillOpacity': 0.5,
#         'color': 'blue',
#         'weight': 2,
#         # 'dashArray': '5, 5'
#     }



def style_route(feature):
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
    trackpoints['time'] = pd.to_datetime(trackpoints['time']).dt.tz_localize(None)
    trackpoints = trackpoints.sort_values('time').reset_index().drop('index', axis=1)
    # mask = (trackpoints['time'] > start_time) & (trackpoints['time'] <= end_time) 
    # trackpoints = trackpoints.loc[mask]
    for i in range (1, len(trackpoints)):
        # distance_temp = geopy.distance.geodesic((trackpoints.iloc[i-1].latitude, trackpoints.iloc[i-1].longitude), (trackpoints.iloc[i].latitude, trackpoints.iloc[i].longitude)).m
        distance_temp = haversine(trackpoints.iloc[i].longitude, trackpoints.iloc[i].latitude, trackpoints.iloc[i - 1].longitude, trackpoints.iloc[i - 1].latitude)
        totalDistance += distance_temp      
    
    totalDistance =  round(totalDistance/1000, 3)
    st.write ('Total distance without any filters: ', totalDistance, ' km')
    totalTime =  (datetime.strptime(str(trackpoints.iloc[-1].time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(trackpoints.iloc[0].time), '%Y-%m-%d %H:%M:%S')).total_seconds()/60
    st.write ('Total time: ', round(totalTime,2), ' minutes')
    if totalTime > 0 :
        st.write ('Average Speed: ', round(totalDistance/(totalTime/60),2), (' km/h'))
    
    st.write('Number of track points: ', len(trackpoints))  
    st.write('Sessions: ', trackpoints['session'].unique()) 
    trackpoints['time_string'] = pd.to_datetime(trackpoints['time']).dt.date.astype(str)
    st.write('Date: ', trackpoints['time_string'].unique() )

    st.write ('Number of duplicate time: ', trackpoints.duplicated(subset=["time"], keep='last').sum())
    st.write ('Number of duplicate lat and long: ', trackpoints.duplicated(subset=["latitude", "longitude"], keep='last').sum())
    st.write ('Number of duplicate time, lat and long: ', trackpoints.duplicated(subset=["time", "latitude", "longitude"], keep='last').sum())
    st.write ('Start time:', trackpoints.iloc[0].time)
    st.write ('End time:', trackpoints.iloc[-1].time)

    # st.write(trackpoints)
    st.write('Activity types: ', trackpoints['motionActivity'].unique()) 

def kalmanfilter(data):
    latitudes = data['latitude'].values
    longitudes = data['longitude'].values
    times = pd.to_datetime(data['time']).astype(np.int64) / 1e9  # Convert to seconds    
    # Calculate time interval (dt) based on time data
    dt = np.mean(np.diff(times))
    dt = 5
    # Initialize the Kalman Filter
    # Define the transition and observation matrices (assuming a simple 2D constant velocity model)
    transition_matrix = np.array([[1, dt, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, dt],
                                [0, 0, 0, 1]])

    observation_matrix = np.array([[1, 0, 0, 0],
                                [0, 0, 1, 0]])

    # Initial state mean
    initial_state_mean = np.array([latitudes[0], 0, longitudes[0], 0])

    # Initial covariance matrix
    initial_state_covariance = np.eye(4) * 1e-4

    # Observation covariance (measurement noise)
    observation_covariance = np.eye(2) * 1e-1

    # Transition covariance (process noise)
    transition_covariance = np.eye(4) * 1e-4
    
    # Initialize the Kalman Filter
    kf = KalmanFilter(
        transition_matrices=transition_matrix,
        observation_matrices=observation_matrix,
        initial_state_mean=initial_state_mean,
        initial_state_covariance=initial_state_covariance,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance
    )   

    # Apply the Kalman Filter
    try:
        # Stack the latitudes and longitudes for the observations
        observations = np.column_stack([latitudes, longitudes])
        # print("Observations stacked successfully.")

        # Use the Kalman Filter to estimate the state means
        state_means, state_covariances = kf.smooth(observations)
        st.write("Kalman Filter applied successfully.")
        filtered_latitudes = state_means[:, 0]
        filtered_longitudes = state_means[:, 2]
        filtered_data = data.copy()  # Copy all original columns
        filtered_data['latitude'] = filtered_latitudes  # Replace with filtered latitude
        filtered_data['longitude'] = filtered_longitudes  # Replace with filtered longitude
        return filtered_data
    except Exception as e:
        st.write(f"Error applying Kalman Filter: {e}")
        return data


def preProcessing(data, start_time, end_time, formular):
    filtered = data
    filtered['time'] = pd.to_datetime(filtered['time'])
     
    
    st.write('Number of original track points: ', len(filtered))   
    timestamp_format = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_time, timestamp_format)
    end = datetime.strptime(end_time, timestamp_format)
    
    
    ##############MotionActivity filter:  may delete "moving" track points
    # mask = (filtered['time'] > start) & (filtered['time'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2) | (filtered['motionActivity'] == 32) | (filtered['motionActivity'] == 64) | (filtered['motionActivity'] == 128))
    mask = (filtered['time'] > start) & (filtered['time'] <= end)

    if formular == 'old': 
        mask = (filtered['time'] > start) & (filtered['time'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2))
    filtered = filtered.loc[mask]
    
    st.write('After filter Motion Activity: ', len(filtered))    

    ############## Drop duplicate track points (the same latitude and longitude, and datetime)  
    filtered = filtered.drop_duplicates(subset=["driver", "session","time"], keep='last') # except last point in case of return to sart point with the same lat long
    filtered = filtered.drop_duplicates(subset=["driver", "session","latitude", "longitude"], keep='last') # except last point in case of return to sart point with the same lat long
    # filtered = filtered.drop_duplicates(subset=["driver", "session","latitude", "longitude", "time"], keep='last') # except last point in case of return to sart point with the same lat long

    st.write('After delete duplicates: ', len(filtered))    
    filtered['time_string'] = pd.to_datetime(filtered['time']).dt.date  
   
    # Initialize new columns
    filtered['time_diff'] = np.nan
    filtered['distance_diff'] = np.nan
    filtered['velocity_diff'] = np.nan
    filtered['accuracy_diff'] = np.nan

    # Calculate time_diff in seconds
    filtered['time_diff'] = filtered['time'].diff().dt.total_seconds()
    filtered['accuracy_diff'] = filtered['accuracy'].diff()

    # Calculate distance_diff in meters using haversine function
    # Shift latitude and longitude to get previous values
    filtered['prev_latitude'] = filtered['latitude'].shift()
    filtered['prev_longitude'] = filtered['longitude'].shift()

    # Calculate distance_diff in meters using haversine function
    filtered['distance_diff'] = filtered.apply(
        lambda row: haversine(
            row['longitude'], row['latitude'],
            row['prev_longitude'], row['prev_latitude']
        ) if pd.notnull(row['prev_latitude']) else 0,
        axis=1
    )
    
    # Calculate velocity in meters per second
    filtered['velocity_diff'] = round((filtered['distance_diff']/1000) / (filtered['time_diff']/3600),2) # in km/h
    # Round distance_diff
    filtered['distance_diff'] =round(filtered['distance_diff'],2)

    # Fill NaN values (first row) with 0 or other appropriate value
    filtered = filtered.fillna(0)
    filtered = filtered.drop(columns=['prev_latitude', 'prev_longitude'])

    # Add an Id representing time asceding
    filtered = filtered.sort_values('time').reset_index().drop('index', axis=1)   
    filtered['id'] = range(0, len(filtered))

    # st.write(filtered)
    return filtered    

def removejumping(data): 
    filtered = data
    st.write('Session: ', filtered['session'].unique()) 
    outliers_index = []
    for i in range (1, len(filtered)-1):  #except final jumping point! Ex: WayPoint_20230928142338.csv        
        time_diff = (datetime.strptime(str(data.iloc[i].time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].time), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_diff = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        distance_diff = haversine(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        if time_diff > 0:
            velocity_diff =  (distance_diff/1000)/(time_diff/3600) #km/h 
            # st.write(data.iloc[i-1].time, data.iloc[i].time,velocity,' km/h') 
            if velocity_diff >70  or distance_diff> MAX_ALLOWED_DISTANCE_JUMPING: #km/h,
                # st.write('Current Point: ', data.iloc[i-1].id, data.iloc[i-1].time, ' Jumping Point: ',data.iloc[i].session, data.iloc[i].id, data.iloc[i].time, ' Time (seconds): ', round(time_diff, 2) , ' Distance (m): ', round(distance_diff,2), 'Velocity: ', round(velocity_diff,2),' km/h')
                outliers_index.append(data.iloc[i].time)            
            
    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    st.write ('After remove jumping points:', len(filtered))    
    return filtered

def removestationary(data): 
    filtered = data
    st.write('Session: ', filtered['session'].unique()) 
    outliers_index = []
    for i in range (1, len(filtered)):     
        if data.iloc[i].accuracy >= 1500 and data.iloc[i].speed == 0 and data.iloc[i].heading == 0:
            outliers_index.append(data.iloc[i].time)             
    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    st.write ('After remove stationary points:', len(filtered))    
    return filtered


def removejumping_formap(data): 
    filtered = data
    outliers_index = []
    for i in range (1, len(filtered)-1):  #except final jumping point! Ex: WayPoint_20230928142338.csv        
        time_diff = (datetime.strptime(str(data.iloc[i].time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].time), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_diff = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        distance_diff = haversine(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        if time_diff > 0:
            velocity =  (distance_diff/1000)/(time_diff/3600) #km/h   
            if velocity >70 or distance_diff> MAX_ALLOWED_DISTANCE_JUMPING: #km/h,
                outliers_index.append(data.iloc[i].time)            
    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    return filtered


def removestationary_formap(data): 
    filtered = data
    outliers_index = []
    for i in range (1, len(filtered)):     
        if data.iloc[i].accuracy >= 1500 and data.iloc[i].speed == 0 and data.iloc[i].heading == 0:
            outliers_index.append(data.iloc[i].time)             
    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    return filtered


def osrm_route(start_lon, start_lat, end_lon, end_lat):       
    # url= f'https://routing.openstreetmap.de/routed-bike/'
    url= f'https://api-gw.sovereignsolutions.com/gateway/routing/india/match/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?radiuses=20%3B20&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
    # url= f'https://api-gw.sovereignsolutions.com/gateway/routing/in/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
    # url = f'https://routing.openstreetmap.de/routed-car/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?continue_straight=true'
    r = requests.get(url,verify=False) 
    if r.status_code == 200:   
        # st.write (url)     
        res = r.json()  
        # routes = polyline.decode(res['matchings'][0]['geometry'])
        routes = polyline.decode(res['matchings'][0]['geometry'])
        
        ##############
        # distance = res['routes'][0]['distance']
        # distance = res['matchings'][0]['distance']
        distance = res['matchings'][0]['distance']
        # print('OSRM distance:', distance)
        osrmroute = {'geometry':routes,      
            'distance':distance           
            }
        return osrmroute
    else:
        url= f'https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
        # st.write (url)
        r = requests.get(url,verify=False) 
        if r.status_code == 200:        
            res = r.json()  
            # routes = polyline.decode(res['matchings'][0]['geometry'])
            routes = polyline.decode(res['routes'][0]['geometry'])            
            ##############
            # distance = res['routes'][0]['distance']
            # distance = res['matchings'][0]['distance']
            distance = res['routes'][0]['distance']
            # print('OSRM distance:', distance)
            osrmroute = {'geometry':routes,      
                'distance':distance           
                }
            return osrmroute
        else:
            return None


def reverse_lat_long_linestring(linestring):
    reversed_coords = [(lng, lat) for lat, lng in linestring.coords]
    return LineString(reversed_coords)

def traveledDistance(data):
    # Remove jumping point groupeb by driver, date, session
    data = removejumping(data) 
    data = removestationary(data)    
    data = kalmanfilter(data)
    
    # applying kalman filter
    
    totalDistance = 0
    count = 0
    routing_index = []
    routing_distance = []
    crowfly_distance = []
    for i in range (1, len(data)):
        velocity_diff = 0
        time_diff = (datetime.strptime(str(data.iloc[i].time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].time), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_temp = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        distance_temp = haversine(data.iloc[i-1].longitude, data.iloc[i-1].latitude, data.iloc[i].longitude, data.iloc[i].latitude)
        accuracy_diff = data.iloc[i].accuracy - data.iloc[i-1].accuracy

        if time_diff>0:
            velocity_diff =  (distance_temp/1000)/(time_diff/3600) #km/h      
       
        # if velocity_diff > 70 or time_diff > MAX_ALLOWED_TIME_GAP or distance_temp> MAX_ALLOWED_DISTANCE_GAP:  # MAX_ALLOWED_TIME_GAP = 300s in case of GPS signals lost for more than MAX_ALLOWED_TIME_GAP seconds
        if velocity_diff > 70 or time_diff > MAX_ALLOWED_TIME_GAP or distance_temp> MAX_ALLOWED_DISTANCE_GAP:  # MAX_ALLOWED_TIME_GAP = 300s in case of GPS signals lost for more than MAX_ALLOWED_TIME_GAP seconds
            if velocity_diff > 5:   
                # st.write(data.iloc[i-1].id, data.iloc[i-1].time)
                # st.write(data.iloc[i].id, data.iloc[i].time)
                # st.write('velocity: ',  velocity_diff)
                # st.write('time_diff: ', time_diff)
                # st.write('distance_temp:', distance_temp)            
                route = osrm_route(data.iloc[i - 1].longitude, data.iloc[i - 1].latitude, data.iloc[i].longitude, data.iloc[i].latitude)
                # print('distance_temp:', distance_temp)
                if route is not None:
                    routing_dict["time"].append(data.iloc[i - 1].time)
                    routing_dict["distance"].append(route['distance'])
                    # # dict_["duration"].append(route['duration'])
                    # if (route['duration'] > 0):
                    #     dict_["speed"].append((route['distance']/1000)/(route['duration']/3600)) # km/h
                    # else: dict_["speed"].append(0)
                    crowfly_distance.append(round(distance_temp,2))

                    if route['distance'] <= 2.5*distance_temp:
                        # print('route distance:',route['distance'])
                        routing_distance.append(round(route['distance'],2))
                        # routing_index.append(data.iloc[i-1].time)  
                        # routing_index.append(data.iloc[i].time)    
                        routing_index.append(data.iloc[i-1].id)  
                        routing_index.append(data.iloc[i].id)                     
                 
                        route_geometries.append(LineString(route['geometry'])) 
                        # st.write('routing_geometries: ', route_geometries)
                        count += 1                    
                        distance_temp = route['distance']
            ############# Not calculate walk points             
            else:     distance_temp = 0
        # if accuracy_diff >= 1000 or data.iloc[i].accuracy >= 1500 :
        if accuracy_diff >= 200 or data.iloc[i].accuracy >= 1500 :
            distance_temp  = 0
                # print('distance_temp after if:', distance_temp)    
        # print("Loop:", i, "timediff:", timediff, "Distance Temp:", distance_temp, "Motion Activity:", data.iloc[i].motionActivity)
        # if distance_temp> 100000:        
        if distance_temp> 400000 and velocity_diff> 200: # if the interval of GPS signal is 1 minutes
        # # if distance_temp> 100000 or distance_temp < 420 : # if the interval of GPS signal is 5 minutes
            distance_temp = 0
        totalDistance += distance_temp   
    # st.write('Number of using routing in distance calculation: ', count, routing_index,'Crow fly distance: ' , crowfly_distance, 'Routing Distance: ', routing_distance)
    totalDistance_km = round(totalDistance/1000, 3)
    return totalDistance_km    

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
        uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns",type=["csv"])
        lat_column_index, lon_column_index = 0,0     

        if url:   
            df = pd.read_csv(url,encoding = "UTF-8")    
            layer_name = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            df = pd.read_csv(uploaded_file,encoding = "UTF-8")
            layer_name = os.path.splitext(uploaded_file.name)[0]
        
        # # display timeseries data
        # my_map = KeplerGl(data={"Track": df}, height=600)
        # keplergl_static(my_map, center_map=True)

        m = folium.Map(
                    max_zoom = 25,
                    tiles='cartodbpositron',
                    zoom_start=14,
                    control_scale=True
                    )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)
        draw = Draw(position='topright',
                    draw_options={'polyline':True,'polygon':False,'rectangle':False,
                                    'circle':False,'marker':False,'circlemarker':False})

        m.add_child(draw)
        
        colors = [ 'green','blue', 'orange', 'red',
                  'lightblue', 'cadetblue', 'darkblue', 
                  'lightgreen', 'darkgreen',             
                  'purple','darkpurple', 'pink',
                  'beige', 'lightred',
                  'white', 'lightgray', 'gray', 'black','darkred']
        if df['session'].nunique() <20:
            df['session_label'] = pd.Categorical(df["session"]).codes
        else: df['session_label'] = 0

        for index, row in df.iterrows():
            popup = row.to_frame().to_html()
            
            folium.Marker([row['latitude'], row['longitude']], 
                        popup=popup,
                        icon=folium.Icon(icon='car', color=colors[row.session_label], prefix='fa')
                        # icon=folium.Icon(icon='car', prefix='fa')
                        ).add_to(m)        
            
        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        trackpoints_origin = gdp.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')        
        download_geojson(trackpoints_origin,layer_name)
        submitted = st.form_submit_button("Calculate Distance")    
    


def CalculateDistance(data, groupBy):        
    grouped = data.groupby(groupBy)
    # result = grouped.apply(traveledDistance)
    result = grouped.apply(traveledDistance)
    # return result.values[0]
    return result.sum()


if submitted:
    with col1:
        statistics(df)
    with col2:        
        st.write('Step 1/2: Preprocessing')
        # df = smooth(df)
        df = preProcessing(df, start_time, end_time, 'new')   
        df['time'] = df['time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        df['time_string'] = df['time_string'].astype(str)
        st.write('Step 2/2: Distance Calculation')
        groupBy = ['driver', 'time_string', 'session']
        st.write('Distance traveled:', CalculateDistance(df, groupBy), ' km') 
        
        df_removejumping = removejumping_formap(df)
        df_removejumping_stationary = removestationary_formap(df_removejumping)
        # df_removejumping = df
        # df_removejumping = removejumping(df)
        geometry = [Point(xy) for xy in zip(df_removejumping_stationary.longitude, df_removejumping_stationary.latitude)]
        trackpoints_cleaned = gdp.GeoDataFrame(df_removejumping_stationary, geometry=geometry, crs = 'epsg:4326')
        # trackpoints_cleaned = trackpoints_cleaned.sort_values(by='time')
        # Create a new column representing the ordered field
        # trackpoints_cleaned['id'] = range(1, len(trackpoints_cleaned) + 1)
                
            
        trackpoints_cleaned_fields = [ column for column in trackpoints_cleaned.columns if column not in trackpoints_cleaned.select_dtypes('geometry') and column not in ['meta']]

        # aggregate these points with the GrouBy
        # folium.GeoJson(geo_df_cleaned).add_to(m)
        # folium_static(m, width = 800)
        # download_geojson(geo_df_cleaned, 'track_points_cleaned')                
        geo_df = gdp.GeoDataFrame(df_removejumping_stationary, geometry=geometry)
        # aggregate these points with the GrouBy
        geo_df = geo_df.groupby(['driver', 'time_string'])['geometry'].apply(lambda x: LineString(x.tolist()))
        track_distance = gdp.GeoDataFrame(geo_df, geometry='geometry', crs = 'EPSG:4326')

        center = track_distance.dissolve().centroid
        center_lon, center_lat = center.x, center.y        
        m = folium.Map( 
                        max_zoom = 25,
                        tiles='cartodbpositron',
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

        draw = Draw(position='topright',
                    draw_options={'polyline':True,'polygon':False,'rectangle':False,
                                    'circle':False,'marker':False,'circlemarker':False})

        m.add_child(draw)        
        
        folium.GeoJson(track_distance, name = 'track_distance',  
                        style_function = style_track, 
                        # highlight_function=highlight_function,
                        # popup = folium.GeoJsonPopup(
                        # fields = tracpoints_cleaned_fields
                        # )
                        ).add_to(m)


        routes_df = gpd.GeoDataFrame(shortestpath_dict, geometry=route_geometries, crs="EPSG:4326")
        # routes_df = gpd.GeoDataFrame(routing_dict, geometry=route_geometries, crs="EPSG:4326")
        # routes_df['geometry'] = routes_df['geometry'].reverse()
        # st.write(routes_df)
        routes_df['geometry'] = routes_df['geometry'].apply(reverse_lat_long_linestring)
        # st.write('reverse geometry: ', routes_df)

        folium.GeoJson(routes_df, name = 'shortest_path',  
                        style_function = style_route, 
                        # highlight_function=highlight_function,
                        ).add_to(m)
        
        trackpoins_cleaned_tooltip = folium.GeoJsonTooltip(
            fields=['time'],
            localize=True
        )
    
        # folium.GeoJson(trackpoints_cleaned, name = 'trackpoints_cleaned',  
        #                 # style_function=style_trackpoints,
        #                 # style_function = lambda feature: style_trackpoints(feature, min_id, max_id),
        #                 tooltip=trackpoins_cleaned_tooltip,                          
        #                 popup = folium.GeoJsonPopup(
        #                 fields = trackpoints_cleaned_fields
        #                 )).add_to(m)

        #### Display start and end points
        def get_color(id, min_id, max_id):
            if id == min_id:
                return 'green'  # color for min ID
            elif id == max_id:
                return 'red'  # color for max ID
            else:
                return 'blue'  # default color
        
        def accuracy_color(accuracy_radius, id, min_id, max_id):            
            if id == min_id:
                fill_color =  'cyan'  # color for min ID
                icon_shape = 'marker'
            elif id == max_id:
                fill_color = 'red'  # color for max ID    
                icon_shape = 'marker'       
            else: 
                fill_color = None
                icon_shape = 'circle'

            if accuracy_radius < 500:
                icon_color = 'green' 
                icon_size = [20,20]  
            elif 500 <= accuracy_radius < 1000:
                icon_color = '#ECC30B'  
                icon_size = [30,30]
            elif 1000 <= accuracy_radius < 2000:
                icon_color = '#ffa500'  
                icon_size = [40,40]
            elif 2000 <= accuracy_radius < 5000:
                icon_color = '#BC5313' 
                icon_size = [60,60] 
            else:
                icon_color = '#ff0000'  
                icon_size = [80,80]
            return icon_color, icon_size, fill_color, icon_shape
            
        min_id = trackpoints_cleaned['id'].min()
        max_id = trackpoints_cleaned['id'].max()
        
        for index, row in trackpoints_cleaned.iterrows():
            # Create a copy of the row to avoid modifying the original DataFrame
            row_copy = row.copy()
            
            # Exclude the field you want to hide (e.g., 'field_to_hide')
            field_to_hide = 'meta'
            if field_to_hide in row_copy:
                row_copy.drop(field_to_hide, inplace=True)
            
            # Create an HTML representation of the row for the popup
            popup = row_copy.to_frame().to_html()
            
            # Determine the color of the icon based on the row's id
            # color = get_color(row['id'], min_id, max_id)

            tooltip = f"time: {row['time']}<br>" \
              f"time_diff: {row['time_diff']}<br>" \
              f"distance_diff: {row['distance_diff']}<br>" \
              f"velocity_diff: {row['velocity_diff']}"

            # folium.Marker([row['latitude'], row['longitude']], 
            #             popup=popup,
            #             tooltip=tooltip , 
            #             icon=folium.Icon(icon='car', color=color, prefix='fa')
            #             # icon=folium.Icon(icon='car', prefix='fa')
            #             ).add_to(m)      
            
            #### Display ID
            # tooltip=trackpoins_cleaned_tooltip,
            # popup = folium.GeoJsonPopup(
            #         fields = trackpoints_cleaned_fields
            #         ) 
            # 
            popup_content = f"""
            <b>ID: </b> {row['id']}<br>
            <b>Time: </b> {row['time']}<br>
            <b>Accuracy: </b> {row['accuracy']}<br>
            <b>time_diff: </b>{row['time_diff']}<br>
            <b>distance_diff: </b>{row['distance_diff']}<br>
            <b>velocity_diff: </b>{row['velocity_diff']}<br>
            <b>accuracy_diff: </b>{row['accuracy_diff']}
            """
            popup = folium.Popup(popup_content, max_width=300)

            coordinates = [row.latitude, row.longitude] 
            id_value = row['id']
            accuracy_radius = row['accuracy']
            # Determine icon color based on value
            icon_color, icon_size, fill_color, icon_shape = accuracy_color(accuracy_radius, id_value, min_id, max_id)

            marker=folium.Marker(
                location=coordinates,               
                icon=BeautifyIcon(
                                # icon="arrow-down", icon_shape="marker",
                                # popup=popup,
                                # tooltip=tooltip , 
                                number=id_value,
                                icon_shape = icon_shape,
                                background_color = fill_color,
                                border_color= icon_color,
                                border_width =1.5,
                                text_color= "#000000",
                                icon_size = icon_size
                            )                
            ).add_to(m)
            marker.add_child(folium.Popup(popup_content, max_width=300))
        

        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)      

        download_geojson(trackpoints_cleaned, layer_name + '_cleaned')
        download_geojson(track_distance, layer_name + '_track')
        download_geojson(routes_df, layer_name + '_routing')
import folium, os
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import routingpy as rp
import pandas as pd
from datetime import datetime
from routingpy import OSRM
import geopandas as gdp
from shapely.geometry import Point, LineString
from shapely import reverse
from folium.plugins import Fullscreen, MeasureControl

import streamlit_ext as ste
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
from math import radians, cos, acos, sin, asin, sqrt
import requests, polyline
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static

st.set_page_config(layout="wide")
st.title("Distance Calculator")
st.write('Distance Calculator for GPS Track Logs')
# start_time = '2023-01-01 00:00:00'
start_time = '2023-01-01 00:00:00'
end_time = '2025-12-30 00:00:00'
######## MAX_ALLOWED_TIME_GAP & MAX_ALLOWED_DISTANCE_GAP for 1 minute interval of trackpoints 
MAX_ALLOWED_TIME_GAP = 300  # seconds
MAX_ALLOWED_DISTANCE_GAP = 500  # meters

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

    st.write(trackpoints)
    st.write('Activity types: ', trackpoints['motionActivity'].unique()) 


def removejumping(data): 
    filtered = data
    outliers_index = []
    for i in range (1, len(filtered)-1):  #except final jumping point! Ex: WayPoint_20230928142338.csv        
        time_diff = (datetime.strptime(str(data.iloc[i].time), '%Y-%m-%d %H:%M:%S') - datetime.strptime(str(data.iloc[i - 1].time), '%Y-%m-%d %H:%M:%S')).total_seconds()
        # distance_diff = geopy.distance.geodesic((data.iloc[i-1].latitude, data.iloc[i-1].longitude), (data.iloc[i].latitude, data.iloc[i].longitude)).m
        distance_diff = haversine(data.iloc[i].longitude, data.iloc[i].latitude, data.iloc[i - 1].longitude, data.iloc[i - 1].latitude)
        if time_diff > 0:
            velocity =  (distance_diff/1000)/(time_diff/3600) #km/h   
            # st.write(data.iloc[i-1].time, data.iloc[i].time,velocity,' km/h') 
            if velocity >70 : #km/h,
                st.write('Current Point: ',  data.iloc[i-1].time,  data.iloc[i-1].session, ' Jumping Point: ', data.iloc[i].time, data.iloc[i].session, ' Time (seconds): ', round(time_diff, 2) , ' Distance (m): ', round(distance_diff,2), 'Velocity: ', round(velocity,2),' km/h')
                outliers_index.append(data.iloc[i].time)            

    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    st.write ('After remove jumping point:', len(filtered)) 
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
            if velocity >70 : #km/h,
                outliers_index.append(data.iloc[i].time)            
    filtered = filtered[filtered.time.isin(outliers_index) == False]   
    return filtered


def preProcessing(data, start_time, end_time, formular):
    filtered = data
    filtered['time'] = pd.to_datetime(filtered['time'])
    filtered = filtered.sort_values('time').reset_index().drop('index', axis=1)
    st.write('Number of original track points: ', len(filtered))   

    timestamp_format = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime(start_time, timestamp_format)
    end = datetime.strptime(end_time, timestamp_format)
    
    
    ##############MotionActivity filter:  may delete "moving" track points
    # mask = (filtered['time'] > start) & (filtered['time'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2) | (filtered['motionActivity'] == 32) | (filtered['motionActivity'] == 64) | (filtered['motionActivity'] == 128))
    # mask = (filtered['time'] > start) & (filtered['time'] <= end)

    if formular == 'old': 
        mask = (filtered['time'] > start) & (filtered['time'] <= end) & ((filtered['motionActivity'] == 0) | (filtered['motionActivity'] == 1) | (filtered['motionActivity'] == 2))
    filtered = filtered.loc[mask]
    
    st.write('After filter Motion Activity: ', len(filtered))    

    # filtered['time'] = pd.to_datetime(filtered['time'])
    filtered['time'] = pd.to_datetime(filtered['time']).dt.tz_localize(None)

    ############## Drop duplicate track points (the same latitude and longitude, and datetime)  
    filtered = filtered.drop_duplicates(subset=["driver", "session","time"], keep='last') # except last point in case of return to sart point with the same lat long
    filtered = filtered.drop_duplicates(subset=["driver", "session","latitude", "longitude"], keep='last') # except last point in case of return to sart point with the same lat long
    filtered = filtered.drop_duplicates(subset=["driver", "session","latitude", "longitude", "time"], keep='last') # except last point in case of return to sart point with the same lat long

    st.write('After delete duplicates: ', len(filtered))    

    filtered['time_string'] = pd.to_datetime(filtered['time']).dt.date    
    st.write(filtered)
    return filtered    

def osrm_route(start_lon, start_lat, end_lon, end_lat):       
    # url= f'https://routing.openstreetmap.de/routed-bike/'
    url= f'https://api-gw.sovereignsolutions.com/gateway/routing/india/match/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?radiuses=20%3B20&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
    # url= f'https://api-gw.sovereignsolutions.com/gateway/routing/in/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
    # url = f'https://routing.openstreetmap.de/routed-car/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?continue_straight=true'
    st.write (url)
    r = requests.get(url,verify=False) 
    if r.status_code == 200:        
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
        st.write (url)
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
        if time_diff>0:
            velocity_diff =  (distance_temp/1000)/(time_diff/3600) #km/h      
       
        if velocity_diff > 70 or time_diff > MAX_ALLOWED_TIME_GAP or distance_temp> MAX_ALLOWED_DISTANCE_GAP:  # MAX_ALLOWED_TIME_GAP = 300s in case of GPS signals lost for more than MAX_ALLOWED_TIME_GAP seconds
            if velocity_diff > 5:   
                st.write(data.iloc[i-1].time)
                st.write(data.iloc[i].time)
                st.write('velocity: ',  velocity_diff)
                st.write('time_diff: ', time_diff)
                st.write('distance_temp:', distance_temp)            
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
                        routing_index.append(data.iloc[i-1].time)  
                        routing_index.append(data.iloc[i].time)                     
                        route_geometries.append(LineString(route['geometry'])) 
                        st.write('routing_geometries: ', route_geometries)
                        count += 1                    
                        distance_temp = route['distance']
            ############# Not calculate walk points             
            else:     distance_temp = 0
                # print('distance_temp after if:', distance_temp)    
        # print("Loop:", i, "timediff:", timediff, "Distance Temp:", distance_temp, "Motion Activity:", data.iloc[i].motionActivity)
        # if distance_temp> 100000:
        if distance_temp> 400000 and velocity_diff> 200: # if the interval of GPS signal is 1 minutes
        # # if distance_temp> 100000 or distance_temp < 420 : # if the interval of GPS signal is 5 minutes
            distance_temp = 0
        totalDistance += distance_temp   
    st.write('Number of using routing in distance calculation: ', count, routing_index,'Crow fly distance: ' , crowfly_distance, 'Routing Distance: ', routing_distance)
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

        m = folium.Map(max_zoom = 21,
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
        geometry = [Point(xy) for xy in zip(df_removejumping.longitude, df_removejumping.latitude)]
        trackpoints_cleaned = gdp.GeoDataFrame(df_removejumping, geometry=geometry, crs = 'epsg:4326')
        trackpoints_cleaned_fields = [ column for column in trackpoints_cleaned.columns if column not in trackpoints_cleaned.select_dtypes('geometry')]

        # aggregate these points with the GrouBy
        # folium.GeoJson(geo_df_cleaned).add_to(m)
        # folium_static(m, width = 800)
        # download_geojson(geo_df_cleaned, 'track_points_cleaned')                
        geo_df = gdp.GeoDataFrame(df_removejumping, geometry=geometry)
        # aggregate these points with the GrouBy
        geo_df = geo_df.groupby(['driver', 'time_string'])['geometry'].apply(lambda x: LineString(x.tolist()))
        track_distance = gdp.GeoDataFrame(geo_df, geometry='geometry', crs = 'EPSG:4326')

        center = track_distance.dissolve().centroid
        center_lon, center_lat = center.x, center.y        
        m = folium.Map(max_zoom = 21,
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

        routes_df = gpd.GeoDataFrame(shortestpath_dict, geometry=route_geometries, crs="EPSG:4326")
        # routes_df = gpd.GeoDataFrame(routing_dict, geometry=route_geometries, crs="EPSG:4326")
        # routes_df['geometry'] = routes_df['geometry'].reverse()
        # st.write(routes_df)
        routes_df['geometry'] = routes_df['geometry'].apply(reverse_lat_long_linestring)
        # st.write('reverse geometry: ', routes_df)

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
        download_geojson(routes_df, layer_name + '_routing')
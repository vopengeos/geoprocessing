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
        print("Loop:", i, "timediff:", timediff, "Distance Temp:", distance_temp, "Motion Activity:", data.iloc[i].motionActivity)
        totalDistance += distance_temp
        
    return round(totalDistance/1000, 3)


form = st.form(key="latlon_calculator")
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
    # for column in df.columns:
    #     if (column.lower() == 'y' or column.lower().startswith("lat") or column.lower().startswith("n")):
    #         lat_column_index=df.columns.get_loc(column)
    #     if (column.lower() == 'x' or column.lower().startswith("ln") or column.lower().startswith("lon") or column.lower().startswith("e") ):
    #         lon_column_index=df.columns.get_loc(column)
    st.write('First point:', str(df.iloc[0].latitude) + ', ' + str(df.iloc[0].longitude))
    st.write('Last point:', str(df.iloc[-1].latitude) + ', ' + str(df.iloc[-1].longitude))
    m = folium.Map(location=[10.775282967747945, 106.70633939229438],
                tiles='stamenterrain',
                zoom_start=14,
                control_scale=True
                )
    for index, row in df.iterrows():
        popup = row.to_frame().to_html()
        folium.Marker([row['latitude'], row['longitude']], 
                    popup=popup,
                    icon=folium.Icon(icon='cloud')
                    ).add_to(m)        
        
    m.fit_bounds(m.get_bounds(), padding=(30, 30))
    folium_static(m, width = 1200)

    submitted = st.form_submit_button("Distance Calculation")    


def CalculateDistance(data, groupBy):
        
    grouped = data.groupby(groupBy)
    result = grouped.apply(traveledDistance)

    return result.values[0]

if submitted:
    data = preProcessing(df, start_time, end_time, 'new')
    groupBy = ['driver', 'date_string']
    st.write('Distance traveled:', str(CalculateDistance(df, groupBy))) 

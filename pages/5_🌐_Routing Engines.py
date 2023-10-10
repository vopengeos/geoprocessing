import folium
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import routingpy as rp
import pandas as pd
from folium.plugins import Fullscreen
from routingpy import OSRM
from routingpy.routers import get_router_by_name
from shapely.geometry import Point, LineString
import geopandas as gpd
import streamlit_ext as ste
import geopandas as gdp

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
st.title("Routing Engines")
st.write('Popular routing engines with routingpy')
routers = {
    'osrm': {
        'display_name': 'OSRM',
        'profile': 'car', #"car", "bike", "foot". 
        # The public FOSSGIS instances ignore any profile parameter set this way and instead chose to encode the ‘profile’ in the base URL, 
        # e.g. https://routing.openstreetmap.de/routed-bike. Default “driving”.
        'color': '#1A2BE2',
        'isochrones': False
    },
    'ors': {
        'api_key': '5b3ce3597851110001cf62483488f43acf744a6b85e2aa7fba0d93f8',
        'display_name': 'OpenRouteService',
        'profile': 'driving-car', # “driving-car”, “driving-hgv”, “foot-walking”, “foot-hiking”, “cycling-regular”, “cycling-road”,”cycling-mountain”, “cycling-electric”
        'color': '#b5152b',
        'isochrones': True
    },
    'mapbox_osrm': {
        'api_key': 'pk.eyJ1IjoidGhhbmdxZCIsImEiOiJucHFlNFVvIn0.j5yb-N8ZR3d4SJAYZz-TZA', 
        'display_name': 'MapBox (OSRM)',
        'profile': 'cycling', # 'driving-traffic', 'driving', 'walking', 'cycling' 
        'color': '#ff9900',
        'isochrones_profile': 'mapbox/driving', 
        'isochrones': True
    },   
    'graphhopper': {
        'api_key': 'cfe0171d-e51b-4988-884e-d4e641bb945a',
        'display_name': 'GraphHopper', 
        'profile': 'mtb', # “car”, “bike”, “foot”, “hike”, “mtb”, “racingbike”, “scooter”, “truck”, “small_truck”        
        'color': '#417900',
        'isochrones': True
    },      
    # 'heremaps': {
    #     'api_key': 'zIA9C4S0jnzUHtDvbG9mk6a78PRSywh97oLU6xBZFRY',  #Right API_KEY but routingpy returns errors
    #     'app_id' : 'z4euQUZZCgMF3ejs8kzF',
    #     'display_name': 'HereMaps',
    #     'profile': 'car', # 'car', 'pedestrian', 'carHOV', 'publicTransport', 'publicTransportTimeTable','truck', 'bicycle'
    #     'color': '#8A2BE2',
    #     'isochrones': True
    # },
    # x = requests.get('https://router.hereapi.com/v8/routes?transportMode=car&origin=10.80256912146467,106.66002143236379&destination=10.8471896823,106.7551364235&return=summary&apikey=zIA9C4S0jnzUHtDvbG9mk6a78PRSywh97oLU6xBZFRY')
    # print ('HERE Maps responses: ', x.content)

    # 'google': {
    #     'api_key': 'AIzaSyAK0hzEteAwyZd9QkfLJI0fj6gg3as075c',
    #     'display_name': 'Google',
    #     'profile': 'driving', # 'driving', 'walking', 'bicycling', 'transit'], bicycling is not available in some countries
    #     'color': '#ff33cc',
    #     'isochrones': False
    # },    
}

def style_function(feature):
    return {
        'fillColor': '#b1ddf9',
        'fillOpacity': 0.5,
        'color': 'blue',
        'weight': 4,
        # 'dashArray': '5, 5'
    }

def highlight_function(feature):   
    return {
    'fillColor': '#ffff00',
    'fillOpacity': 0.8,
    'color': '#ffff00',
    'weight': 6,
    # 'dashArray': '5, 5'
}

def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download GeoJSON",
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 


col1, col2 = st.columns(2)
with col1:
    form = st.form(key="roungting_engines")
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
        coordinates = [[df.iloc[0].longitude, df.iloc[0].latitude], [df.iloc[-1].longitude, df.iloc[-1].latitude]]
        routers_selected = st.multiselect('Choose one or more routing engines: ', routers, default=routers )
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

        submitted = st.form_submit_button("Shortest Path")    

if submitted:
    with col2:
        dict_ = {"router": [], "distance": [], "duration": []}
        geometries = []
        for router in routers_selected: 
            if router == 'osrm':
                api = OSRM(base_url="https://router.project-osrm.org/")
            else:
                api = get_router_by_name(router)(api_key=routers[router]['api_key'])   

            # for coords_pair in input_pairs:
                # just from A to B without intermediate points
            route = api.directions(
                profile=routers[router]['profile'],
                locations=coordinates
            )
            # Access the route properties with .geometry, .duration, .distance
            distance, duration = route.distance / 1000, int(route.duration / 60) #km, minutes
            dict_["router"].append(router)
            dict_["distance"].append(distance)
            dict_["duration"].append(duration)
            geometries.append(LineString(route.geometry))
            st.write("Calulated {}".format(router))

        routes_df = gpd.GeoDataFrame(dict_, geometry=geometries, crs="EPSG:4326")
        
         
        start_end_df = df.iloc[[0, -1]]
        geometry = [Point(xy) for xy in zip(start_end_df.longitude, start_end_df.latitude)]
        start_end_df = gdp.GeoDataFrame(start_end_df, geometry=geometry, crs = 'epsg:4326')
        start_end_df_fields = [ column for column in start_end_df.columns if column not in start_end_df.select_dtypes('geometry')]

        center = start_end_df.dissolve().centroid
        center_lon, center_lat = center.x, center.y          
        m = folium.Map(max_zoom = 21,
                        tiles='stamenterrain',
                        zoom_start=14,
                        location = [center_lat, center_lon],
                        control_scale=True
                        )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)


        folium.GeoJson(start_end_df, name = 'start_end ',  
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
                        fields = start_end_df_fields
                        )).add_to(m)

        folium.GeoJson(routes_df, name = 'shortest_path',  
                        style_function = style_function, 
                        highlight_function=highlight_function,
                        # popup = folium.GeoJsonPopup(
                        # fields = tracpoints_cleaned_fields
                        # )
                        ).add_to(m)

        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        folium_static(m, width = 600)
        st.write(routes_df)
        download_geojson(routes_df, 'shortest_path')
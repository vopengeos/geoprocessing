import routingpy as rp
from shapely.geometry import LineString, Point, Polygon
from matplotlib import pyplot as plt
import geopandas as gpd
import contextily as cx
from pprint import pprint
import random
from shapely.geometry import box, Point, LineString, Polygon, MultiPolygon
from routingpy.routers import get_router_by_name
import requests
from routingpy import OSRM


# One lib to route them all - routingpy is a Python 3 client for several popular routing webservices.


BASEMAP_SOURCE = cx.providers.CartoDB.Positron
coordinates = [[106.66002143236379, 10.80256912146467], [106.65920967368636, 10.793778847708758]]
# coordinates = [[13.413706, 52.490202], [13.421838, 52.514105],
#           [13.453649, 52.507987], [13.401947, 52.543373]]

plt.rcParams['figure.dpi'] = 50

########################
# Open Route Service https://openrouteservice.org/
########################
# key_ors = "5b3ce3597851110001cf62483488f43acf744a6b85e2aa7fba0d93f8"
# api = rp.ORS(api_key=key_ors)
# route = api.directions(locations=coordinates, profile='driving-car')
# print(route)

# start_end = gpd.GeoDataFrame(geometry=[Point(x,y) for x,y in coordinates], crs="EPSG:4326").to_crs("EPSG:3857")
# route_line = gpd.GeoDataFrame(geometry=[LineString(route.geometry)], crs="EPSG:4326").to_crs("EPSG:3857")
# fig, ax = plt.subplots(1,1, figsize=(10,10))
# start_end.plot(ax=ax, color="red")
# route_line.plot(ax=ax, color="red", linewidth=3, alpha=0.5)
# cx.add_basemap(ax=ax, crs="EPSG:3857", source=BASEMAP_SOURCE)
# _ = ax.axis("off")

########################
# Isochrones
# defaults to https://valhalla1.openstreetmap.de
#######################
# api = rp.Valhalla()
# isochrones = api.isochrones(locations=coordinates[0],
#                       profile='auto',
#                       intervals=[100,200])
# isochrone_df = gpd.GeoDataFrame(
#                             {"id": [x for x in range(len(isochrones))]},
#                             geometry=[Polygon(X.geometry) for X in reversed(isochrones)], crs="EPSG:4326",
#                                 ).to_crs("EPSG:3857")
# print(isochrone_df)
# fig, ax = plt.subplots(1,1, figsize=(10,10))
# isochrone_df.plot(ax=ax, column="id", cmap="RdYlGn", linewidth=0, alpha=0.2)
# isochrone_df.plot(ax=ax, column="id", cmap="RdYlGn", linewidth=2, alpha=1, facecolor="none")
# start_end.iloc[:-1].plot(ax=ax, color="black", markersize=45)
# cx.add_basemap(ax=ax, crs="EPSG:3857", source=BASEMAP_SOURCE)
# _ = ax.axis("off")

########################
# Matrix 
########################
# here_key = "Dk5XeAB_8tTxTylzgpQ4JaTvSvrRfB5VdhHCQyT7GAU"
# api = rp.HereMaps(api_key=here_key)
# matrix = api.matrix(locations=coordinates, profile='car')
# pprint(matrix.durations)
# pprint(matrix.raw)

########################
# Expansion 
########################

# valhalla_public_url = "https://valhalla1.openstreetmap.de"
# api = rp.Valhalla(base_url=valhalla_public_url)

# expansions = api.expansion(locations=coordinates[0],
#                       profile='auto',
#                       intervals=[200],
#                       expansion_properties=["durations"])
# expansion_df = gpd.GeoDataFrame(
#                             {"id": [x for x in range(len(expansions))], "duration": [x.duration for x in expansions]},
#                             geometry=[LineString(X.geometry) for X in expansions], crs="EPSG:4326",
#                                 ).to_crs("EPSG:3857")
# # print (expansion_df)
# fig, ax = plt.subplots(1,1, figsize=(10,10))
# expansion_df[expansion_df["duration"] <= 200].plot(ax=ax, column="duration", cmap="RdYlGn_r", linewidth=1, alpha=1)
# start_end.iloc[:-1].plot(ax=ax, color="black", markersize=20)
# cx.add_basemap(ax=ax, crs="EPSG:3857", source=BASEMAP_SOURCE)
# _ = ax.axis("off") 

##############################
bbox = [106.5652081433,10.6948093039,106.7551364235,10.8471896823]  # bbox 

minx, miny, maxx, maxy = bbox
poly_hcmc = box(*bbox)

def random_coordinates(n, min_dist, max_dist):
    assert min_dist < max_dist # make sure parameters are valid
    
    coordinates = []
    for _ in range(n):
        counter = 0
        in_poly = False
        while not in_poly:
            counter += 1
            x = random.uniform(minx, maxx)
            y = random.uniform(miny, maxy)
            p = Point(x, y)
            if poly_hcmc.contains(p):
                # Make sure all route segments are within limits
                if coordinates:
                    if not min_dist < p.distance(Point(coordinates[-1])) < max_dist:
                        continue
                coordinates.append([x, y])
                in_poly = True
            if counter > 1000:
                raise ValueError("Distance settings are too restrictive. Try a wider range and remember it's in degrees.")

    return coordinates

#Define all router clients
#['google', 'graphhopper', 'here', 'heremaps', 'mapbox_osrm', 'mapbox-osrm', 'mapbox', 'mapboxosrm', 'openrouteservice', 'opentripplanner', 'opentripplanner_v2', 'ors', 'osrm', 'otp', 'otp_v2', 'valhalla']
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
    'heremaps': {
        'api_key': 'zIA9C4S0jnzUHtDvbG9mk6a78PRSywh97oLU6xBZFRY',  #Right API_KEY but routingpy returns errors
        'app_id' : 'z4euQUZZCgMF3ejs8kzF',
        'display_name': 'HereMaps',
        'profile': 'car', # 'car', 'pedestrian', 'carHOV', 'publicTransport', 'publicTransportTimeTable','truck', 'bicycle'
        'color': '#8A2BE2',
        'isochrones': True
    },
    # x = requests.get('https://router.hereapi.com/v8/routes?transportMode=car&origin=10.80256912146467,106.66002143236379&destination=10.8471896823,106.7551364235&return=summary&apikey=zIA9C4S0jnzUHtDvbG9mk6a78PRSywh97oLU6xBZFRY')
    # print ('HERE Maps responses: ', x.content)


    # 'google': {
    #     'api_key': '',
    #     'display_name': 'Google',
    #     'profile': 'driving', # 'driving', 'walking', 'bicycling', 'transit'], bicycling is not available in some countries
    #     'color': '#ff33cc',
    #     'isochrones': False
    # },
    
}


#Calculate Directions

route_amount = 1
# distance for 1 degree in Berlin: ~ 110 km latitude, ~68 km longitude, 
# i.e. 3.4-7 km < distance < 6.8-11 km
input_pairs = [random_coordinates(n=2, min_dist=0.05, max_dist=0.1) for i in range(route_amount)]
dict_ = {"router": [], "distance": [], "duration": []}
geometries = []
for router in routers: 
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

    print("Calulated {}".format(router))

routes_df = gpd.GeoDataFrame(dict_, geometry=geometries, crs="EPSG:4326").to_crs("EPSG:3857")
# print(routes_df)
routes_df.to_file('./Data/osmx_data/routingpy.geojson')

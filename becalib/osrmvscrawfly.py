import requests
from geopy.distance import geodesic
import random

# Function to calculate crow-fly distance between two points
def crow_fly_distance(point1, point2):
    return geodesic(point1, point2).kilometers

# Generate random point within a certain radius from a given point
def generate_random_point_within_radius(center, radius):
    lat, lon = center
    # Generate random offset within a circle of radius 'radius'
    r = radius / 111300  # Approximate number of meters per degree latitude
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    w = r * (u ** 0.5)
    t = 2 * 3.141592653589793 * v
    x = w * (2 ** 0.5) * (u ** 0.5)
    lat_new = lat + x * (2 ** 0.5)
    lon_new = lon + x * (2 ** 0.5)
    return (lat_new, lon_new)

# Generate random pairs of points within Bengaluru with distance under 10 km
def generate_random_points_in_bengaluru(num_pairs):
    # Coordinates for Bengaluru
    bengaluru_coordinates = [(12.7500, 77.5800), (13.2000, 77.9000)]  # Rough coordinates to cover the city
    points = []
    for _ in range(num_pairs):
        # Generate random point within Bengaluru
        lat = random.uniform(bengaluru_coordinates[0][0], bengaluru_coordinates[1][0])
        lon = random.uniform(bengaluru_coordinates[0][1], bengaluru_coordinates[1][1])
        center = (lat, lon)
        # Generate another point within 10 km of the center
        radius = 0.02 # 0.1 degree is roughly 10 km at this latitude
        lat_offset = random.uniform(-radius, radius)
        lon_offset = random.uniform(-radius, radius)
        point2 = (lat + lat_offset, lon + lon_offset)
        points.append((center, point2))
    return points

# Calculate routing distance using OSRM API
def calculate_routing_distance(point1, point2):
    # url = f"http://router.project-osrm.org/route/v1/driving/{point1[1]},{point1[0]};{point2[1]},{point2[0]}?overview=false"
    url= f'https://api-gw.sovereignsolutions.com/gateway/routing/india/match/v1/driving/{point1[1]},{point1[0]};{point2[1]},{point2[0]}?radiuses=20%3B20&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'

    print (url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == "Ok":
            return data["matchings"][0]["distance"] / 1000  # Convert to kilometers
    return None

# Generate random pairs of points within Bengaluru with distance under 10 km
num_pairs = 100
random_points = generate_random_points_in_bengaluru(num_pairs)

# Calculate routing distance and crow-fly distance for each pair
j = 0
for i in range(num_pairs):
    center, point2 = random_points[i]
    routing_distance = calculate_routing_distance(center, point2)
    crow_fly_dist = crow_fly_distance(center, point2)
    if routing_distance is not None and routing_distance > 2.5*crow_fly_dist:
        j+=1
        print("No:", j)
        print("Pair:", i+1)
        print("point1:", center)
        print("point2:", point2)
        print("Routing distance:", routing_distance, "km")
        print("Crow-fly distance:", crow_fly_dist, "km")
        print("")

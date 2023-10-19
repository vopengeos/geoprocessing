import geopy.distance
from math import radians, cos, sin, asin, sqrt
from distance_const import *
from geopy import Nominatim

# Next, input the latitude and longitude data for Nairobi and Cairo.  
orig=(36.817223,-1.286389)
dest=( 31.233334,30.033333)
orig = (10.80256912146467, 106.66002143236379)
dest = (10.793778847708758, 106.65920967368636)

# Finally, print the distance between the two locations in kilometers. 

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

def geodistInit():
    for i in range(COS_LUT_SIZE + 1):
        cos_lut[i] = math.cos(2 * PI * i / COS_LUT_SIZE)
    
    for i in range(ASIN_SQRT_LUT_SIZE + 1):
        asin_sqrt_lut[i] = math.asin(math.sqrt(i / ASIN_SQRT_LUT_SIZE))
    
    for i in range(METRIC_LUT_SIZE + 1):
        latitude = float(i * (PI / METRIC_LUT_SIZE) - PI * 0.5)
        wgs84_metric_meters_lut[i * 2] = float((111132.09 - 566.05 * math.cos(2 * latitude) + 1.20 * math.cos(4 * latitude)) ** 2)
        wgs84_metric_meters_lut[i * 2 + 1] = float((111415.13 * math.cos(latitude) - 94.55 * math.cos(3 * latitude) + 0.12 * math.cos(5 * latitude)) ** 2)
        sphere_metric_meters_lut[i] = ((EARTH_DIAMETER * PI / 360) * math.cos(latitude)) ** 2
        sphere_metric_lut[i] = math.cos(latitude) ** 2

def geodistDegDiff(f):
    f = abs(f)
    if f > 180:
        f = 360 - f
    return f

def geodistFastCos(x):
    y = abs(x) * (COS_LUT_SIZE_F / PI_F / 2.0)
    i = int(y)
    y -= i
    i &= (COS_LUT_SIZE - 1)
    return cos_lut[i] + (cos_lut[i + 1] - cos_lut[i]) * y

def geodistFastSin(x):
    y = abs(x) * (COS_LUT_SIZE_F / PI_F / 2.0)
    i = int(y)
    y -= i
    i = (i - COS_LUT_SIZE // 4) & (COS_LUT_SIZE - 1)
    return cos_lut[i] + (cos_lut[i + 1] - cos_lut[i]) * y

def geodistFastAsinSqrt(x):
    if x < 0.122:
        # distance under 4546 km, Taylor error under 0.00072%
        y = math.sqrt(x)
        return y + x * y * 0.166666666666666 + x * x * y * 0.075 + x * x * x * y * 0.044642857142857
    if x < 0.948:
        # distance under 17083 km, 512-entry LUT error under 0.00072%
        x *= ASIN_SQRT_LUT_SIZE
        i = int(x)
        return asin_sqrt_lut[i] + (asin_sqrt_lut[i + 1] - asin_sqrt_lut[i]) * (x - i)
    return math.asin(math.sqrt(x))  # distance over 17083 km, just compute exact


def greatCircle(lon1deg, lat1deg, lon2deg, lat2deg):
    # Get delta
    lat_diff = float(geodistDegDiff(lat1deg - lat2deg))
    lon_diff = float(geodistDegDiff(lon1deg - lon2deg))

    latitude_midpoint = float((lat1deg + lat2deg + 180.0) * METRIC_LUT_SIZE / 360.0)
    latitude_midpoint_index = int(latitude_midpoint) & (METRIC_LUT_SIZE - 1)

    k_lat = (
        float(wgs84_metric_meters_lut[latitude_midpoint_index * 2])
        + float(wgs84_metric_meters_lut[(latitude_midpoint_index + 1) * 2] - wgs84_metric_meters_lut[latitude_midpoint_index * 2])
        * float(latitude_midpoint - latitude_midpoint_index)
    )
    k_lon = (
        float(wgs84_metric_meters_lut[latitude_midpoint_index * 2 + 1])
        + float(wgs84_metric_meters_lut[(latitude_midpoint_index + 1) * 2 + 1] - wgs84_metric_meters_lut[latitude_midpoint_index * 2 + 1])
        * float(latitude_midpoint - latitude_midpoint_index)
    )

    return float(math.sqrt(k_lat * lat_diff * lat_diff + k_lon * lon_diff * lon_diff))

geodistInit()
print("geopy geodesic distance: ",geopy.distance.geodesic(orig,dest).m)
print("geopy geodesic default distance function: ",geopy.distance.distance(orig,dest).m)
print("geopy greatcircle distance: ",geopy.distance.great_circle (orig,dest).m)

print("greatcircle distance using Haversine formular:",haversine(orig[1],orig[0], dest[1], dest[0]))
print("greatcircle distance using Clickhouse formular:", greatCircle(orig[1],orig[0], dest[1], dest[0]))
g = Nominatim(user_agent="my_application")
_, wa = g.geocode('Washington, DC')
_, pa = g.geocode('Palo Alto, CA')
print('Nominatim path distnance:', (geopy.distance.geodesic(orig, dest) + geopy.distance.distance(dest, wa) + geopy.distance.distance(wa, pa)).m)

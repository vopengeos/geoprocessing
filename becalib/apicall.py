import requests
import polyline

def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):
    
    loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    # url = "https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/?api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d"
    url = f'https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/{pickup_lon},{pickup_lat};{dropoff_lon},{dropoff_lat}?alternatives=false&steps=true&overview=simplified&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
    r = requests.get(url, verify=False) 
    if r.status_code!= 200:
        return {}
  
    res = r.json()   
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']
    
    out = {'route':routes,
           'start_point':start_point,
           'end_point':end_point,
           'distance':distance
          }

    return out

pickup_lon = 72.87959175878925
pickup_lat = 20.016468998748095
dropoff_lon = 72.89543879785987
dropoff_lat = 19.974327694670322

route = get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
print(route['route'])

# response = requests.get("https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/72.87959175878925,20.016468998748095;72.89543879785987,19.974327694670322;73.03632658976028,20.000264344928624?alternatives=false&steps=true&overview=simplified&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d", verify=False)
# start_lon = 72.87959175878925
# start_lat = 20.016468998748095
# end_lon = 72.89543879785987
# end_lat = 19.974327694670322
# route_api = f'https://api-gw.sovereignsolutions.com/gateway/routing/india/route/v1/bike/{start_lon},{start_lat};{end_lon},{end_lat}?geometries=geojson&alternatives=false&steps=true&overview=simplified&api-key=6bb21ca2-5a4e-4776-b80a-87e2fbd6408d'
# # response = requests.get(route_api, verify=False)
# response = requests.get(route_api, verify=False) 
# # print(response.json())
# for key in response.json():
#     print(key,":", response.json()[key])

# print(response.json()['geometry'])

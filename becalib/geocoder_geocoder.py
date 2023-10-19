# import requests
# url = 'https://maps.googleapis.com/maps/api/geocode/json'
# params = {'sensor': 'false', 'address': 'VNTTS', 'key': 'AIzaSyAK0hzEteAwyZd9QkfLJI0fj6gg3as075c'}
# r = requests.get(url, params=params)
# results = r.json()['results']
# # location = results[0]['geometry']['location']
# print(results)

import geocoder
##################### Google #######################
# g = geocoder.google('Techcraft, vietnam', method='places',  key = 'AIzaSyAK0hzEteAwyZd9QkfLJI0fj6gg3as075c')
# print ('Google Maps:', g.address, g.latlng) #, g.json
# g = geocoder.google([10.8026049, 106.660012], method='reverse', key = 'AIzaSyAK0hzEteAwyZd9QkfLJI0fj6gg3as075c')
# print ('Google Maps:', g.address,g.latlng)
# g = geocoder.google([10.8026049, 106.660012], method='elevation', key = 'AIzaSyAK0hzEteAwyZd9QkfLJI0fj6gg3as075c')

##################### ArcGIS #######################
# g = geocoder.arcgis('Portland')
# print ('ArcGIS: ', g.address, g.latlng) #, g.json

##################### Bing Maps #######################
# g = geocoder.bing('Portland', key='AouKXy50mwfC7S0ChSOxYG1MLueL0ZVW3zg6kNDnJTfNT4vHqFvlFmCo3RVx8yEt')
# print ('Bing Maps: ', g.address, g.latlng) #, g.json

##################### Geonames #######################
# g = geocoder.geonames('Ho Chi Minh City', key='thangqd') #key='<USERNAME>'
# print ('Geonames: ', g.address, g.latlng, g.description, g.population) #, g.json

##################### HERE Maps #######################
# g = geocoder.here('Portland', app_id ='z4euQUZZCgMF3ejs8kzF', api_key  = 'zIA9C4S0jnzUHtDvbG9mk6a78PRSywh97oLU6xBZFRY') 
# print ('Here Maps: ', g.address, g.latlng) #, g.json
# return error, the same with routingpy

##################### Mapbox #######################
# g = geocoder.mapbox('Techcraft, Vietnam', key= 'pk.eyJ1IjoidGhhbmdxZCIsImEiOiJucHFlNFVvIn0.j5yb-N8ZR3d4SJAYZz-TZA') 
# print ('Mapbox: ', g.address, g.latlng) #, g.json

##################### Mapquest #######################
# g = geocoder.mapquest('Portland', key= 'EGGYYH3j1lOm0DDD4osGMGDhjfZiQ4so') 
# print ('Mapquest: ', g.address, g.latlng) #, g.json

##################### Nominatim #######################
g = geocoder.osm('Techcraft') 
print ('Nominatim: ', g.address, g.latlng) #, g.json


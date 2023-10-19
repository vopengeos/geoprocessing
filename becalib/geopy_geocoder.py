from geopy import Nominatim
import geopy.distance
import pandas as pd
from geopy.extra.rate_limiter import RateLimiter

# orig=(36.817223,-1.286389)
# dest=( 31.233334,30.033333)
# orig = (10.80256912146467, 106.66002143236379)
# dest = (10.793778847708758, 106.65920967368636)

####################
# Nominatim
####################
g = Nominatim(user_agent="techcraft")
orig, dest = None, None
try:
    orig_address, orig = g.geocode('VNTTS', timeout=1000)
except:
    print ('No geocode found in origin address')
    pass
try:
    dest_address, dest = g.geocode('Becamex', timeout=1000)
except:
    print ('No geocode found in dest address')
    pass
if orig and dest is not None:
    print(orig_address, orig)
    print(dest_address, dest)
    print('Geodesy distance:', geopy.distance.geodesic(orig, dest))

####################
# Nominatim GeoDataframe Geocoder
####################

#Creating a dataframe with address of locations we want to reterive
locat = ['Coorg, Karnataka' , 'Khajjiar, Himachal Pradesh',\
         'Chail, Himachal Pradesh' , 'Pithoragarh, Uttarakhand','Munnar, Kerala']
locat = ['811212']
df = pd.DataFrame({'add': locat})
 
#Creating an instance of Nominatim Class
geolocator = Nominatim(user_agent="my_request")
 
#applying the rate limiter wrapper
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
 
#Applying the method to pandas DataFrame
df['location'] = df['add'].apply(geocode)
df['Lat'] = df['location'].apply(lambda x: x.latitude if x else None)
df['Lon'] = df['location'].apply(lambda x: x.longitude if x else None)
print(df)


####################
# Nominatim GeoDataframe Geocoder
####################


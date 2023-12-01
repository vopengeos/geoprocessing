# import folium
# from folium.plugins import Geocoder
# from streamlit_folium import st_folium,folium_static
# import streamlit as st
# from becalib.latlong import parseDMSString, formatDmsString, formatMgrsString 
# import pyproj
# from pyproj import CRS, Transformer
# from pyproj.aoi import AreaOfInterest
# from pyproj.database import query_utm_crs_info
# import what3words
# from  becalib import olc, mgrs, geohash, maidenhead, georef, utm
# from folium.plugins import MarkerCluster, FastMarkerCluster, Fullscreen
# import pandas as pd
# import streamlit_ext as ste
import geopandas as gpd


# st.set_page_config(layout="wide")
# st.sidebar.info(
#     """
#     - Web: [Geoprocessing Streamlit](https://geoprocessing.streamlit.app)
#     - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
#     """
# )

# st.sidebar.title("Contact")
# st.sidebar.info(
#     """
#     Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
#     """
# )

# st.title("PyrOSM")
# st.write('PyrOSM')

import pyrosm
from pyrosm import get_data
from pyrosm.data import sources
# st.write('continents: ', sources.available.keys())
# st.write('countries: ', sources.asia.available)
# st.write('citis:', sources.cities.available)
# st.write("All countries with sub-regions:", sources.subregions.available.keys())
# st.write("Sub-regions in Brazil:", sources.subregions.brazil.available)
# Download data for the city of Helsinki
# fp = get_data("Helsinki",update=True) # Overwirite if existed
# st.write(fp)
# fp = pyrosm.get_data("test_pbf")
# osm = pyrosm.OSM(fp)
# print("Type of 'osm' instance: ", type(osm))
# drive_net = osm.get_network(network_type="driving")
# print(drive_net.head(2))
# drive_net.plot()
fp = ".\data\maldives-latest.osm.pbf"
# Initialize the OSM parser object
osm = pyrosm.OSM(fp)
buildings = osm.get_buildings()
print(buildings.head())
buildings.plot()




        
        
    






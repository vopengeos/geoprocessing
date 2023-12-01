# import folium, os
# from folium.plugins import Draw, LocateControl
# import streamlit as st
# from streamlit_folium import st_folium, folium_static
# from folium.plugins import MousePosition
# import osmium
# import shapely.wkb as wkblib
# import pandas as pd
# import geopandas as gpd
# import streamlit_ext as ste
# from mappymatch import package_root
# from mappymatch.constructs.geofence import Geofence
# from mappymatch.constructs.trace import Trace
# from mappymatch.maps.nx.nx_map import NxMap
# from mappymatch.matchers.lcss.lcss import LCSSMatcher
# from folium.plugins import Fullscreen
# import streamlit_ext as ste
# from shapely.geometry import Point, LineString
# import geopandas as gpd
# from osmnx import graph_from_bbox, graph_from_point
# from math import radians, cos, sin, asin, sqrt

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
# st.title("Map Matching")
# st.write('Map Matching')
# def download_geojson(gdf, layer_name):
#     if not gdf.empty:        
#         geojson = gdf.to_json()  
#         ste.download_button(
#             label="Download " + layer_name,
#             file_name= layer_name+ '.geojson',
#             mime="application/json",
#             data=geojson
#         ) 

# def style_function(feature):
#     return {
#         'fillColor': '#b1ddf9',
#         'fillOpacity': 0.5,
#         'color': 'blue',
#         'weight': 2,
#         # 'dashArray': '5, 5'
#     }

# def style_function2(feature):
#     return {
#         'fillColor': '#b1dda3',
#         'fillOpacity': 0.5,
#         'color': 'red',
#         'weight': 2,
#         # 'dashArray': '5, 5'
#     }


# def highlight_function(feature):   
#     return {
#     'fillColor': '#ffff00',
#     'fillOpacity': 0.8,
#     'color': '#ffff00',
#     'weight': 4,
#     # 'dashArray': '5, 5'
# }

# import osmnx as ox
# import time
# from shapely.geometry import Polygon
# import os
# import numpy as np

# def haversine(lon1, lat1, lon2, lat2):
#     """
#     Calculate the great circle distance in kilometers between two points 
#     on the earth (specified in decimal degrees)
#     """
#     # convert decimal degrees to radians 
#     lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#     # haversine formula 
#     dlon = lon2 - lon1 
#     dlat = lat2 - lat1 
#     a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     c = 2 * asin(sqrt(a)) 
#     r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
#     dist = c * r
#     return  dist*1000 # meters

# def save_graph_geojson_directional(G, filepath=None, encoding="utf-8"):
#     # default filepath if none was provided
#     if filepath is None:
#         filepath = os.path.join(ox.settings.data_folder, "osrm_data")

#     # if save folder does not already exist, create it (shapefiles
#     # get saved as set of files)
#     if not filepath == "" and not os.path.exists(filepath):
#         os.makedirs(filepath)
#     filepath_nodes = os.path.join(filepath, "nodes.geojson")
#     filepath_edges = os.path.join(filepath, "edges.geojson")

#     # convert undirected graph to gdfs and stringify non-numeric columns
#     gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
#     gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
#     gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
#     # We need an unique ID for each edge
#     gdf_edges["fid"] = np.arange(0, gdf_edges.shape[0], dtype='int')
#     # save the nodes and edges as separate ESRI shapefiles
#     gdf_nodes.to_file(filepath_nodes, encoding=encoding)
#     gdf_edges.to_file(filepath_edges, encoding=encoding)

# st.write("osmnx version",ox.__version__)

# # Download by a bounding box
# # bounds = (17.4110711999999985,18.4494298999999984,59.1412578999999994,59.8280297000000019)
# # x1,x2,y1,y2 = bounds
# # boundary_polygon = Polygon([(x1,y1),(x2,y1),(x2,y2),(x1,y2)])
# # G = ox.graph_from_polygon(boundary_polygon, network_type='drive')
# # start_time = time.time()
# # save_graph_shapefile_directional(G, filepath='./network-new')
# # st.write("--- %s seconds ---" % (time.time() - start_time))

# # Download by place name
# orig = (10.80256912146467, 106.66002143236379)
# dest = (10.793778847708758, 106.65920967368636)

# geom_orig = Point(orig[1], orig[0]) #Point(lon, lat)
# gdf_orig = gpd.GeoDataFrame(geometry=[geom_orig], crs=ox.settings.default_crs)
# gdf_orig.to_file('./Data/osmx_data/origin.geojson')

# geom_dest = Point(dest[1], dest[0]) #Point(lon, lat)
# gdf_dest = gpd.GeoDataFrame(geometry=[geom_dest], crs=ox.settings.default_crs)
# gdf_dest.to_file('./Data/osmx_data/dest.geojson')


# print(geom_orig, geom_dest)

# center = ((orig[0]+dest[0])/2, (orig[1]+dest[1])/2)
# dist = haversine(orig[1],orig[0],dest[1],dest[0])*2/3
# G = graph_from_point(center, dist=dist*2, network_type='walk', simplify  = False) #"all_private", "all", "bike", "drive", "drive_service", "walk"

# G = ox.add_edge_speeds(G)
# G = ox.add_edge_travel_times(G)
# save_graph_geojson_directional(G, filepath='./Data/osmx_data')

# from fmm import FastMapMatch,Network,NetworkGraph,UBODTGenAlgorithm,UBODT,FastMapMatchConfig
# network = Network("./Data/osmx_data/edges.shp","fid","u","v")
# st.write("Nodes {} edges {}".format(network.get_node_count(),network.get_edge_count()))
# graph = NetworkGraph(network)


# ### Precompute an UBODT table

# # Can be skipped if you already generated an ubodt file
# ubodt_gen = UBODTGenAlgorithm(network,graph)
# status = ubodt_gen.generate_ubodt("./Data/osmx_data/ubodt.txt", 0.02, binary=False, use_omp=True)
# st.write(status)

# ### Read UBODT

# ubodt = UBODT.read_ubodt_csv("./Data/osmx_data/ubodt.txt")

# ### Create FMM model
# model = FastMapMatch(network,graph,ubodt)

# ### Define map matching configurations

# k = 8
# radius = 0.003
# gps_error = 0.0005
# fmm_config = FastMapMatchConfig(k,radius,gps_error)


# ### Run map matching for wkt
# wkt = "LineString(106.66002143 10.80256912, 106.6592398 10.79371861, 106.65921077 10.79349551, 106.65945237 10.79318357, 106.65939989 10.79298777, 106.65959055 10.79284781, 106.65996389 10.79253907, 106.66017224 10.79237924, 106.66034524 10.7922586, 106.66067268 10.79198399, 106.6610762 10.7917621, 106.66127353 10.79169749, 106.66144935 10.79163991, 106.66166577 10.79157533, 106.66186039 10.79150924, 106.66223895 10.79144512, 106.66246695 10.79146295, 106.66296747 10.79144025, 106.66323095 10.79140316, 106.66340843 10.79135901, 106.66413061 10.791121, 106.66431256 10.79105719, 106.6645565 10.79095202, 106.66503264 10.79078182, 106.66525792 10.79069791, 106.66549159 10.7906224, 106.66573293 10.7905885, 106.66618054 10.79043888, 106.66638399 10.79029565, 106.66623514 10.79009372, 106.66631171 10.789869, 106.66641291 10.78971753, 106.66643927 10.78951491, 106.66676675 10.78921986, 106.6672445 10.78898313, 106.66742204 10.78889448, 106.66760276 10.78880494, 106.66777896 10.78871941, 106.66794477 10.78863687, 106.66811331 10.78856501, 106.66847436 10.78842667, 106.66866281 10.78835575, 106.66883732 10.78829109, 106.66901468 10.78822469, 106.66924958 10.78814639, 106.66949064 10.7880487, 106.6697545 10.78798249, 106.67019776 10.78785618, 106.67042904 10.78777784, 106.67064016 10.78769665, 106.67083132 10.78762784, 106.67104446 10.78756743, 106.67122491 10.78753442, 106.67140133 10.78746759, 106.67166693 10.78738316, 106.67213764 10.78723269, 106.67238078 10.78716388, 106.67263704 10.78708571, 106.6728992 10.78700397, 106.67340585 10.78684504, 106.67365089 10.78676582, 106.67388446 10.78671217, 106.67411851 10.7866138, 106.67450859 10.78636598, 106.67470661 10.78619628, 106.67488409 10.78604419, 106.675059 10.7859017, 106.67567235 10.78541885, 106.67583037 10.78530014, 106.6759873 10.78519067, 106.67613542 10.78508049, 106.676284 10.78496906, 106.6765018 10.78481196, 106.67666116 10.78471822, 106.67684619 10.7846386, 106.67704102 10.7845757, 106.67724234 10.78451029, 106.67743397 10.78444754, 106.67783277 10.78419265, 106.67801106 10.78402572, 106.67813334 10.78393526, 106.67818603 10.78391174, 106.67843478 10.78389425, 106.678644 10.78390123, 106.67887286 10.78391133, 106.67911191 10.78394761, 106.67956663 10.78403364, 106.67978179 10.78402933, 106.68001519 10.78401232, 106.68021906 10.78399141, 106.68028827 10.7837687, 106.68025658 10.78354282, 106.68022962 10.78330691, 106.68017889 10.78308757, 106.68014747 10.78266419, 106.68026223 10.78251425, 106.68046378 10.78240154, 106.68067692 10.78228029, 106.68087061 10.78215087, 106.68106357 10.78204461, 106.68122178 10.78194646, 106.68140237 10.78183231, 106.68160024 10.78170627, 106.68179354 10.78158166, 106.68197589 10.78146246, 106.68216511 10.78135243, 106.68252442 10.78112026, 106.68268318 10.78102687, 106.68286701 10.78090939, 106.68302619 10.78081557, 106.68319716 10.7807184, 106.68359675 10.78047709, 106.68379438 10.7803554, 106.68396008 10.78026578, 106.68413188 10.78017966, 106.68429256 10.78008699, 106.68450036 10.77996698, 106.68488661 10.77972157, 106.6850863 10.77959926, 106.68528 10.77947721, 106.6854796 10.77934347, 106.68563797 10.77924024, 106.68580006 10.77910857, 106.68599014 10.77899951, 106.68614611 10.77888296, 106.68631879 10.7787339, 106.68645752 10.77861441, 106.68664176 10.77845796, 106.68697749 10.77815718, 106.68714242 10.77800469, 106.68733464 10.77783186, 106.6875187 10.77765205, 106.68784915 10.77734129, 106.68800491 10.7771899, 106.68814352 10.77705163, 106.68827509 10.77691426, 106.68845239 10.77678841, 106.68860067 10.77665938, 106.68877556 10.77651145, 106.68895792 10.77635892, 106.68911506 10.77622552, 106.68927561 10.77607988, 106.68940331 10.77593671, 106.68955296 10.77579692, 106.68987638 10.77549873, 106.69006109 10.77532887, 106.69021126 10.77519078, 106.69034934 10.77503901, 106.69047406 10.77487887, 106.69035532 10.77468996, 106.69003668 10.77438701, 106.68989747 10.77421982, 106.68976943 10.77405271, 106.68962943 10.77389493, 106.68949275 10.77376159, 106.68954059 10.77357973, 106.68971126 10.77345582, 106.68988417 10.77333591, 106.69007604 10.77322118, 106.6904714 10.77301344, 106.69090702 10.77280161, 106.69107924 10.77271941, 106.69131274 10.77259546, 106.69153875 10.77247398, 106.69244816 10.77197026, 106.69261955 10.77187206, 106.69278001 10.77177955, 106.69295872 10.77167905, 106.69307979 10.77151515, 106.69314204 10.77130538, 106.69331679 10.77119371, 106.69360836 10.77089228, 106.69374319 10.77066227, 106.69384072 10.77050733, 106.69394229 10.77034973, 106.69430495 10.76979957, 106.69441023 10.76963084, 106.69453115 10.76945913, 106.69462798 10.76933928, 106.69472789 10.76914079, 106.69482816 10.76893025, 106.69493902 10.76877728, 106.69506811 10.76857534, 106.69527228 10.76815698, 106.69536997 10.76799241, 106.69547205 10.76784032, 106.69557351 10.76768537, 106.69568398 10.76749537, 106.6957799 10.76730237, 106.695883 10.76715229, 106.69607716 10.76678499, 106.69617904 10.76659377, 106.69629172 10.76639195, 106.69639035 10.76621802, 106.6964978 10.76602784, 106.69662818 10.76583129, 106.69672372 10.7656724, 106.69683649 10.76548849, 106.69697598 10.76528604, 106.69709253 10.76505782, 106.69723123 10.7649145, 106.69736087 10.76467639, 106.69758156 10.76428468, 106.69786273 10.76387818, 106.69804046 10.76369305, 106.69818039 10.76357552, 106.69850561 10.76325339, 106.69870164 10.76306591, 106.69883311 10.7629386, 106.69915314 10.76261546, 106.69929138 10.76248017, 106.69942349 10.76234023, 106.69955201 10.76218361, 106.69968787 10.76201716, 106.69981161 10.76184771, 106.69994153 10.76163962, 106.7000341 10.76145442, 106.70016538 10.76131412, 106.70011353 10.76151836, 106.69997352 10.76167808, 106.69986111 10.76188015, 106.69971002 10.76207116, 106.69959375 10.76224803, 106.69949003 10.7624202, 106.69923763 10.76272667, 106.69910717 10.76288942, 106.69902377 10.76309097, 106.69895812 10.76327349, 106.69909378 10.76344901, 106.69927686 10.76356259, 106.69947725 10.76359033, 106.69968105 10.76369778, 106.69987553 10.7637672, 106.70005288 10.76363025, 106.70012466 10.76342508, 106.70022995 10.76321828, 106.70031428 10.76282277, 106.70032896 10.76275478, 106.70037522 10.7626365, 106.70044782 10.76246244, 106.70052249 10.76228938, 106.70071549 10.76197437, 106.70085445 10.76178195, 106.70098053 10.76164081, 106.70107809 10.76146844, 106.70121563 10.76125988, 106.70148187 10.76087557, 106.70171794 10.76055605, 106.70183067 10.76040679, 106.70209786 10.76003614, 106.70218718 10.75986619, 106.70205443 10.75973221, 106.7018677 10.75959775, 106.70149878 10.75933045, 106.70134506 10.75921615, 106.70119513 10.75910467, 106.70101865 10.75897132, 106.7008576 10.75886597, 106.70068874 10.75873851, 106.70054041 10.75862244, 106.70039324 10.7585006, 106.7002307 10.75837188, 106.70007585 10.75827094, 106.6999202 10.75815756, 106.6997665 10.75804733, 106.6999403 10.75767611, 106.70007459 10.7575465, 106.70030109 10.75719885, 106.70044973 10.75700153, 106.70060627 10.75680825, 106.70074095 10.75660198, 106.70103551 10.75622806, 106.70134802 10.75585478, 106.7015065 10.75564711, 106.70161884 10.75550274, 106.70178089 10.7552941, 106.7019001 10.75507634, 106.70196715 10.75484965, 106.70198334 10.75459835, 106.70200993 10.75432721, 106.70203636 10.75405835, 106.70206097 10.75386196, 106.70208055 10.75366175, 106.70210154 10.75345531, 106.70213303 10.7530634, 106.7021633 10.75285722, 106.7021663 10.75264376, 106.70218263 10.75244306, 106.7022089 10.75216242, 106.70221561 10.75195709, 106.70225502 10.75154964, 106.70227444 10.75134132, 106.70229239 10.75113615, 106.70231369 10.75091774, 106.70237106 10.75026367, 106.70238753 10.75004569, 106.7024035 10.74982751, 106.70239227 10.74962144, 106.70238176 10.74942341, 106.7023783 10.74923539, 106.70229433 10.74843006, 106.70226029 10.74822299, 106.70222853 10.74802648, 106.70219319 10.74782963, 106.7021589 10.74764515, 106.70212141 10.74744954, 106.70208761 10.74725706, 106.70205287 10.747055, 106.70202209 10.74687596, 106.7019861 10.74668418, 106.70194955 10.74648945, 106.70191724 10.74629996, 106.70188164 10.74606021, 106.70183729 10.7458808, 106.70180646 10.74569397, 106.70175826 10.74550768, 106.70173325 10.7452941, 106.70169037 10.74506398, 106.70162789 10.74465891, 106.70161186 10.7444781, 106.70158786 10.74428853, 106.70155655 10.74410178, 106.70145762 10.74366074, 106.70142828 10.7434364, 106.70139943 10.74323365, 106.7013513 10.74302875, 106.70125119 10.74244544, 106.70121664 10.74224968, 106.70118016 10.74203997, 106.70115132 10.74179698, 106.70109719 10.74154597, 106.70105449 10.74130376, 106.70101195 10.74107034, 106.70097305 10.74085268, 106.70093571 10.74064583, 106.70089731 10.74044825, 106.70085932 10.74024524, 106.70082135 10.7400425, 106.70075252 10.73984511, 106.70070049 10.73961446, 106.70064833 10.73938087, 106.70052441 10.73923547, 106.70045276 10.73904003, 106.70035661 10.73886986, 106.70015193 10.73908269)"
# result = model.match_wkt(wkt,fmm_config)

# ### Print map matching result
# st.write("Opath ",list(result.opath))
# st.write( "Cpath ",list(result.cpath))
# st.write( "WKT ",result.mgeom.export_wkt())


# # Download by a boundary polygon in geojson
# # import osmnx as ox
# # from shapely.geometry import shape
# # json_file = open("stockholm_boundary.geojson")
# # import json
# # data = json.load(json_file)
# # boundary_polygon = shape(data["features"][0]['geometry'])
# # G = ox.graph_from_polygon(boundary_polygon, network_type='drive')
# # save_graph_shapefile_directional(G, filepath='stockholm')



# # col1, col2 = st.columns(2)
# # with col1:
# #     form = st.form(key="distance_calculator")
# #     layer_name = 'track'
# #     with form: 
# #         url = st.text_input(
# #                 "Enter a CSV URL with Latitude and Longitude Columns",
# #                 'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/gps_noise_2.csv'
# #             )
# #         uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
# #         lat_column_index, lon_column_index = 0,0     

# #         if url:   
# #             df = pd.read_csv(url,encoding = "UTF-8")    
# #             layer_name = url.split("/")[-1].split(".")[0]            
# #         if uploaded_file:        
# #             df = pd.read_csv(uploaded_file,encoding = "UTF-8")
# #             layer_name = os.path.splitext(uploaded_file.name)[0]
# #         m = folium.Map(max_zoom = 21,
# #                     tiles='cartodbpositron',
# #                     zoom_start=14,
# #                     control_scale=True
# #                     )
# #         Fullscreen(                                                         
# #                 position                = "topright",                                   
# #                 title                   = "Open full-screen map",                       
# #                 title_cancel            = "Close full-screen map",                      
# #                 force_separate_button   = True,                                         
# #             ).add_to(m)
        
# #         colors = [ 'green','blue', 'orange', 'red',
# #                   'lightblue', 'cadetblue', 'darkblue', 
# #                   'lightgreen', 'darkgreen',             
# #                   'purple','darkpurple', 'pink',
# #                   'beige', 'lightred',
# #                   'white', 'lightgray', 'gray', 'black','darkred']
# #         if df['session'].nunique() <20:
# #             df['session_label'] = pd.Categorical(df["session"]).codes
# #         else: df['session_label'] = 0

# #         for index, row in df.iterrows():
# #             popup = row.to_frame().to_html()
# #             folium.Marker([row['latitude'], row['longitude']], 
# #                         popup=popup,
# #                         icon=folium.Icon(icon='car', color=colors[row.session_label], prefix='fa')
# #                         # icon=folium.Icon(icon='car', prefix='fa')
# #                         ).add_to(m)        
            
# #         m.fit_bounds(m.get_bounds(), padding=(30, 30))
# #         folium_static(m, width = 600)
# #         geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
# #         trackpoints_origin = gpd.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')        
# #         download_geojson(trackpoints_origin,layer_name)
# #         submitted = st.form_submit_button("Map Matching")    
        

# # if submitted:
# #     with col2:
# #         # trace = Trace.from_csv(package_root() / "resources/traces/sample_trace_1.csv")
# #         if url:   
# #             trace = Trace.from_csv(url)        
# #         if uploaded_file:        
# #             trace = Trace.from_csv(uploaded_file)    
        
# #         # generate a geofence polygon that surrounds the trace; units are in meters;
# #         # this is used to query OSM for a small map that we can match to
# #         geofence = Geofence.from_trace(trace, padding=1e3)

# #         # uses osmnx to pull a networkx map from the OSM database
# #         nx_map = NxMap.from_geofence(geofence)

# #         matcher = LCSSMatcher(nx_map)

# #         matches = matcher.match_trace(trace)

# #         # convert the matches to a dataframe
# #         df = matches.matches_to_dataframe()
# #         st.write(df)



import osmnx as ox
from osmnx import graph_from_bbox, graph_from_point
import networkx as nx
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
import taxicab as tc
import geopy.distance

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

def save_graph_geojson_directional(G, filepath=None, encoding="utf-8"):
    # default filepath if none was provided
    if filepath is None:
        filepath = os.path.join(ox.settings.data_folder, "osrm_data")

    # if save folder does not already exist, create it (shapefiles
    # get saved as set of files)
    if not filepath == "" and not os.path.exists(filepath):
        os.makedirs(filepath)
    filepath_nodes = os.path.join(filepath, "nodes.geojson")
    filepath_edges = os.path.join(filepath, "edges.geojson")

    # convert undirected graph to gdfs and stringify non-numeric columns
    gdf_nodes, gdf_edges = ox.utils_graph.graph_to_gdfs(G)
    gdf_nodes = ox.io._stringify_nonnumeric_cols(gdf_nodes)
    gdf_edges = ox.io._stringify_nonnumeric_cols(gdf_edges)
    # We need an unique ID for each edge
    gdf_edges["fid"] = np.arange(0, gdf_edges.shape[0], dtype='int')
    # save the nodes and edges as separate ESRI shapefiles
    gdf_nodes.to_file(filepath_nodes, encoding=encoding)
    gdf_edges.to_file(filepath_edges, encoding=encoding)

# download osm graph
orig = (10.80256912146467, 106.66002143236379)
dest = (10.793778847708758, 106.65920967368636)

geom_orig = Point(orig[1], orig[0]) #Point(lon, lat)
gdf_orig = gpd.GeoDataFrame(geometry=[geom_orig], crs=ox.settings.default_crs)
gdf_orig.to_file('./Data/osmx_data/origin.geojson')

geom_dest = Point(dest[1], dest[0]) #Point(lon, lat)
gdf_dest = gpd.GeoDataFrame(geometry=[geom_dest], crs=ox.settings.default_crs)
gdf_dest.to_file('./Data/osmx_data/dest.geojson')


print(geom_orig, geom_dest)

center = ((orig[0]+dest[0])/2, (orig[1]+dest[1])/2)
dist = haversine(orig[1],orig[0],dest[1],dest[0])*2/3
G = graph_from_point(center, dist=dist, network_type='drive', simplify  = False) #"all_private", "all", "bike", "drive", "drive_service", "walk"

G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)
save_graph_geojson_directional(G, filepath='./Data/osmx_data')

# find nearest nodes
n_orig = ox.nearest_nodes(G, orig[1], orig[0]) #(X, Y)
n_dest = ox.nearest_nodes(G, dest[1], dest[0]) #(X,Y)

osmnx_route = nx.shortest_path(G, n_orig, n_dest, weight = 'length')
length = nx.shortest_path_length(G, n_orig, n_dest, weight='length')
print('osmnx length:', length)

nodes, edges = ox.graph_to_gdfs(G)
# print (nodes)
# print (edges)

route_nodes = nodes.loc[osmnx_route]
gdf_nodes = gpd.GeoDataFrame(route_nodes, geometry=route_nodes['geometry'], crs=ox.settings.default_crs)

route_line = LineString(route_nodes['geometry'].tolist())
gdf_line = gpd.GeoDataFrame(geometry=[route_line], crs=ox.settings.default_crs)

gdf_line.to_file('./Data/osmx_data/osmnx_route_lines.geojson')
gdf_nodes.to_file('./Data/osmx_data/osmnx_route_nodes.geojson')


# plot shortest path graph
fig, ax = ox.plot_graph_route(
    G, osmnx_route, route_color='darkorange', show=False, close=False)

ax.scatter(
    G.nodes[n_orig]['x'], G.nodes[n_orig]['y'], 
    c='lime', s=100, label='orig')

ax.scatter(
    G.nodes[n_dest]['x'], G.nodes[n_dest]['y'],
    c='red', s=100, label='dest')

ax.scatter(
    orig[1], orig[0],
    color='lime', marker='x', s=100, label='orig-point')

ax.scatter(
    dest[1], dest[0],
    color='red', marker='x', s=100, label='dest-point')

plt.legend()
plt.show()

####################### 
# Taxicab route
####################### 
# taxicab_route = tc.distance.shortest_path(G, orig, dest)
# print ('taxicab length: ', taxicab_route[0])
# tc.plot.plot_graph_route(G, taxicab_route)
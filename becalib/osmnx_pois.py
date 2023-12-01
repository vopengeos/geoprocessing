import osmnx as ox
# gdf_poi = ox.pois_from_place('India')
tags = {'building': True}
buildings = ox.geometries_from_place('singapore', tags)
print(buildings)
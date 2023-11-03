import folium, os
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import osmium
import shapely.wkb as wkblib
import pandas as pd
import geopandas as gpd
import streamlit_ext as ste

st.set_page_config(layout="wide")
st.sidebar.info(
    """
    - Web: [Geoprocessing Streamlit](https://geoprocessing.streamlit.app)
    - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
    """
)
st.title("PyOsmium")
st.write('PyOsmium')
col1, col2 = st.columns(2)
def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download " + layer_name,
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 

class StreetsHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.num_nodes = 0
        self.num_relations = 0
        self.num_ways = 0
        self.street_relations = []
        self.street_relation_members = []
        self.street_ways = []
        # A global factory that creates WKB from a osmium geometry
        self.wkbfab = osmium.geom.WKBFactory()

    def way(self, w):
        if w.tags.get("highway") is not None and w.tags.get("name") is not None:
            try:
                wkb = self.wkbfab.create_linestring(w)
                geo = wkblib.loads(wkb, hex=True)
            except:
                return
            row = { "w_id": w.id, "geo": geo }

            for key, value in w.tags:
                row[key] = value

            self.street_ways.append(row)
            self.num_ways += 1

    def relation(self, r):
        if r.tags.get("type") == "associatedStreet" and r.tags.get("name") is not None:
            row = { "r_id": r.id }
            for key, value in r.tags:
                row[key] = value
            self.street_relations.append(row)

            for member in r.members:
                self.street_relation_members.append({ 
                    "r_id": r.id, 
                    "ref": member.ref, 
                    "role": member.role, 
                    "type": member.type, })
                self.num_relations += 1
region = "maldives"
handler = StreetsHandler()
# path to file to local drive
# download from https://download.geofabrik.de/index.html
osm_file = f"D:/osmdata/{region}-latest.osm.pbf"
# start data file processing
handler.apply_file(osm_file, locations=True, idx='flex_mem')
# show stats
st.write(f"num_relations: {handler.num_relations}")
st.write(f"num_ways: {handler.num_ways}")
st.write(f"num_nodes: {handler.num_nodes}")
# create dataframes
street_relations_df = pd.DataFrame(handler.street_relations)
street_relation_members_df = pd.DataFrame(handler.street_relation_members)
street_ways_df = pd.DataFrame(handler.street_ways)
st.write(street_relations_df.dtypes)
# streets_df = pd.merge(street_ways_df, street_relation_members_df, left_on="w_id", right_on="ref", how="left", suffixes=["_way", ""])
# streets_df = pd.merge(streets_df, street_relations_df, left_on="r_id", right_on="r_id", how="left", suffixes=["", "_rel"])
# streets_df["id"] = 'w' + streets_df['w_id'].astype(str)
# # merge name and wikidata property from both ways and relations data
# if "wikidata_rel" in streets_df.columns:
#     streets_df['wikidata_merged'] = streets_df.wikidata.combine_first(streets_df.wikidata_rel)
# else:
#     streets_df['wikidata_merged'] = streets_df.wikidata
# streets_df['name_merged'] = streets_df.name.combine_first(streets_df.name_rel)
# streets_df['name_merged'] = streets_df.name.combine_first(streets_df.name_rel)
# if "uk_rel" in streets_df.columns:
#     streets_df['name:uk_merged'] = streets_df["name:uk"].combine_first(streets_df["name:uk_rel"])
# elif "name:uk" in streets_df.columns:
#     streets_df['name:uk_merged'] = streets_df["name:uk"]
# else:
#     streets_df['name:uk_merged'] = None
# if "ru_rel" in streets_df.columns:
#     streets_df['name:ru_merged'] = streets_df["name:ru"].combine_first(streets_df["name:ru_rel"])
# else:
#     streets_df['name:ru_merged'] = streets_df["name:ru"]
# if "en_rel" in streets_df.columns:
#     streets_df['name:en_merged'] = streets_df["name:en"].combine_first(streets_df["name:en_rel"])
# else:
#     streets_df["name:en"]
# streets_gdf = gpd.GeoDataFrame(streets_df, geometry="geo")
# streets_gdf

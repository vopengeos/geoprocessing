from mappymatch import package_root
from mappymatch.constructs.geofence import Geofence
from mappymatch.constructs.trace import Trace
from mappymatch.maps.nx.nx_map import NxMap
from mappymatch.matchers.lcss.lcss import LCSSMatcher
import streamlit as st

trace = Trace.from_csv(package_root() / "resources/traces/sample_trace_1.csv")

# generate a geofence polygon that surrounds the trace; units are in meters;
# this is used to query OSM for a small map that we can match to
geofence = Geofence.from_trace(trace, padding=1e3)

# uses osmnx to pull a networkx map from the OSM database
nx_map = NxMap.from_geofence(geofence)

matcher = LCSSMatcher(nx_map)

matches = matcher.match_trace(trace)

# convert the matches to a dataframe
df = matches.matches_to_dataframe()
st.write(df)
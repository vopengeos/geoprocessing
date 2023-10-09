import folium
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import MousePosition

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
st.title("Routing Engines")
st.write('Popular routing engines with routingpy')


def get_pos(lat, lng):
    return lat, lng


m = folium.Map(location=[10.775282967747945, 106.70633939229438],
                tiles='stamenterrain',
                zoom_start=14,
                control_scale=True
                )

markers = m.add_child(folium.ClickForMarker())
# LocateControl(auto_start=False).add_to(m)
MousePosition().add_to(m)
map = st_folium(m, width = 800)
latlng = []
if map ['last_clicked'] is not None:
    # st.write(map['last_clicked']['lat'],map['last_clicked']['lng'])
    lat, lng = map['last_clicked']['lat'],map['last_clicked']['lng']
    latlng.append(lat, lng)
    st.write(lat, lng)
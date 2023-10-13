import folium
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium

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
st.title("Rectangle")
st.write('Rectangle')


m = folium.Map(location=[10.775282967747945, 106.70633939229438],
                tiles='stamenterrain',
                zoom_start=14,
                control_scale=True
                )

draw = Draw(position='topleft',
            draw_options={'polyline':False,'polygon':False,'rectangle':True,
                                    'circle':False,'marker':False,'circlemarker':False},
            filename='rectangle.geojson', export=True)


LocateControl(auto_start=True).add_to(m)
draw.add_to(m)
# bounds = [(10.7567509999999995,106.6828079999999943), (10.7888090000000005, 106.7320919999999944)]
# folium.Rectangle(bounds=bounds, color='#ff7800', fill=True, fill_color='#ffff00', fill_opacity=0.2).add_to(m)
st_folium(m, width = 800)
 
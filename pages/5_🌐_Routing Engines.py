import folium
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import routingpy as rp
import pandas as pd

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

form = st.form(key="latlon_calculator")
with form: 
    url = st.text_input(
            "Enter a CSV URL with Latitude and Longitude Columns",
            'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/gps.csv'
        )
    uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
    lat_column_index, lon_column_index = 0,0     
    if url:   
        df = pd.read_csv(url,skiprows=[1],encoding = "UTF-8")                
    if uploaded_file:        
        df = pd.read_csv(uploaded_file,skiprows=[1],encoding = "UTF-8")
    # for column in df.columns:
    #     if (column.lower() == 'y' or column.lower().startswith("lat") or column.lower().startswith("n")):
    #         lat_column_index=df.columns.get_loc(column)
    #     if (column.lower() == 'x' or column.lower().startswith("ln") or column.lower().startswith("lon") or column.lower().startswith("e") ):
    #         lon_column_index=df.columns.get_loc(column)
    st.write('First point:', str(df.iloc[0].latitude) + ', ' + str(df.iloc[0].longitude))
    st.write('Last point:', str(df.iloc[-1].latitude) + ', ' + str(df.iloc[-1].longitude))
    m = folium.Map(location=[10.775282967747945, 106.70633939229438],
                tiles='stamenterrain',
                zoom_start=14,
                control_scale=True
                )
    for index, row in df.iterrows():
        popup = row.to_frame().to_html()
        folium.Marker([row['latitude'], row['longitude']], 
                    popup=popup,
                    icon=folium.Icon(icon='cloud')
                    ).add_to(m)        
        
    m.fit_bounds(m.get_bounds(), padding=(30, 30))
    folium_static(m, width = 1200)

    submitted = st.form_submit_button("Shortest Path")    

if submitted:
     pass
# def get_pos(lat, lng):
#     return lat, lng


# m = folium.Map(location=[10.775282967747945, 106.70633939229438],
#                 tiles='stamenterrain',
#                 zoom_start=14,
#                 control_scale=True
#                 )

# markers = m.add_child(folium.ClickForMarker())
# draw = Draw(
#             position='topleft',
#             draw_options={'polyline':False,'polygon':False,'rectangle':False,
#                                     'circle':False,'marker':True,'circlemarker':False},
#             filename='points.geojson', export=True)
# # LocateControl(auto_start=False).add_to(m)
# m.add_child(draw)
# MousePosition().add_to(m)
# map = st_folium(m, width = 800)
# # latlng = []
# # if map['last_clicked'] is not None:
# #     # st.write(map['last_clicked']['lat'],map['last_clicked']['lng'])
# #     lat, lng = map['last_clicked']['lat'],map['last_clicked']['lng']
# #     latlng.append(map['last_clicked'])
# #     st.write(latlng)
# coordinates = [[106.66002143236379, 10.80256912146467], [106.65920967368636, 10.793778847708758]]
# for point in coordinates:
#     st.write(point)
#     # folium.Marker(point).add_to(map)

# key_ors = "5b3ce3597851110001cf62483488f43acf744a6b85e2aa7fba0d93f8"
# api = rp.ORS(api_key=key_ors)
# route = api.directions(locations=coordinates, profile='driving-car')
# st.write(route)

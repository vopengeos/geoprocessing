import folium, os
from folium.plugins import Draw, LocateControl
import streamlit as st
from streamlit_folium import st_folium, folium_static
from folium.plugins import MousePosition
import routingpy as rp
import pandas as pd
from datetime import datetime
import geopy.distance
from becalib.distance_const import *
from routingpy import OSRM
import geopandas as gdp
from shapely.geometry import Point, LineString
from folium.plugins import Fullscreen
import streamlit_ext as ste
import geopandas as gpd
# from pykalman import KalmanFilter
import numpy as np
import altair as alt
from vega_datasets import data
from folium.features import DivIcon


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
st.title("Time Series Data Visualization")
st.write('Time Series Data Visualization')
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

with col1:
    form = st.form(key="timeseries_visualization")
    layer_name = 'timeseries'
    with form: 
        url = st.text_input(
                "Enter a CSV URL with Latitude and Longitude Columns",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/salinity_2019.csv'
            )
        uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")

        if url:   
            df = pd.read_csv(url,encoding = "UTF-8")    
            layer_name = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            df = pd.read_csv(uploaded_file,encoding = "UTF-8")
            layer_name = os.path.splitext(uploaded_file.name)[0]
        
        timestamp_format = "%Y-%m-%d %H:%M:%S"
        date_format = "%Y-%m-%d"
        
        # df['datetime'] = datetime.strptime(df['datetime'], timestamp_format)
                              
        df_map = df.drop_duplicates(subset=["ID"], keep='last')
        m = folium.Map(max_zoom = 21,
                    tiles='stamenterrain',
                    zoom_start=14,
                    control_scale=True
                    )
        Fullscreen(                                                         
                position                = "topright",                                   
                title                   = "Open full-screen map",                       
                title_cancel            = "Close full-screen map",                      
                force_separate_button   = True,                                         
            ).add_to(m)

        for index, row in df_map.iterrows():
            popup = row.to_frame().to_html()
            circle_lat=row['latitude']
            circle_lon = row['longitude']
            # folium.Circle(location = [circle_lat, circle_lon], radius = 500, fill=False).add_child(folium.Popup(popup)).add_to(m)
            # folium.Circle(
            # # folium.CircleMarker(
            #             location = [circle_lat, circle_lon], 
            #             radius = 5000, 
            #             fill_color  = 'blue',
            #             fill=True,
            #             tooltip = row['ID'],
            #             # color = 'black',
            #             fill_opacity=0.3).add_child(folium.Popup(popup)).add_to(m)
            
            folium.Marker([row['latitude'], row['longitude']], 
                        # popup = popup + f'<input type="text" value="{row["ID"]}" id="myInput"></br><button onclick="myFunction()">Copy ID</button>',
                        popup = popup,
                        icon=folium.Icon(icon='cloud'),
                        tooltip = row['ID'],
                        # icon=DivIcon(
                        # # icon_size=(150,36),
                        # icon_anchor=(0,0),
                        # html='<div style="font-size: 10pt; color: red">%s</div>' %row['ID'],
                        # )
                        ).add_to(m)        
            
        m.fit_bounds(m.get_bounds(), padding=(30, 30))
        # el = folium.MacroElement().add_to(m)
        # el._template = jinja2.Template("""
        #     {% macro script(this, kwargs) %}
        #     function myFunction() {
        #     /* Get the text field */
        #     var copyText = document.getElementById("myInput");

        #     /* Select the text field */
        #     copyText.select();
        #     copyText.setSelectionRange(0, 99999); /* For mobile devices */

        #     /* Copy the text inside the text field */
        #     document.execCommand("copy");
        #     }
        #     {% endmacro %}
        #     """)


        folium_static(m, width = 600)
        # geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        # gdf = gdp.GeoDataFrame(df, geometry=geometry, crs = 'epsg:4326')  
        # download_geojson(gdf,layer_name)     
        IDs_selected = st.multiselect('Choose IDs to display timeseries data: ', options= df['ID'].unique())
        df['datetime'] = pd.to_datetime(df['date']+' ' + df['time_value'])
        df['date'] = pd.to_datetime(df['date']).dt.date        

        Days_selected = st.multiselect('Choose Days to display timeseries data: ', options= df['date'].unique())
        submitted = st.form_submit_button("Display Time Series Data")    
    

if submitted:
    with col2:  
        filtered = df
        if len(IDs_selected) >0:
            filtered =  filtered[filtered['ID'].isin(IDs_selected)]
        if len(Days_selected) >0:
            filtered =  filtered[filtered['date'].isin(Days_selected)]

        c = (
        alt.Chart(filtered)
        # alt.Chart(df[df['ID'] == pyperclip.paste()])
        .mark_circle() #mark_bar()/ mark_point()/ mark_line(), mark_circle()
        .encode(
                x=("datetime:T"), 
                # x=alt.X("datetime:T", axis=alt.Axis(
                #     format="%Y-%M-%D", 
                #     labelOverlap=True, 
                #     labelAngle=-45,
                #     tickCount=len(df.date),
                # )),
                y="salinity:Q", 
                color="ID", tooltip=["ID","datetime:T","time_value", "salinity"]
                )
        ).interactive()
        # temps = data.seattle_temps()
        # st.write (temps)
        # c = (
        # alt.Chart(temps)
        # # alt.Chart(df[df['ID'] == pyperclip.paste()])
        # .mark_circle() #mark_bar()/ mark_point()/ mark_line(), mark_circle()
        # .encode(
        #        x='date:T',
        #        y='temp:Q'
        #         )
        # ).interactive()

        st.altair_chart(c, use_container_width=True)
        st.write(filtered)
import streamlit as st
import pydeck as pdk
import json
import folium
from streamlit_folium import st_folium,folium_static
import streamlit as st
from folium.plugins import MarkerCluster, FastMarkerCluster, Fullscreen
import pandas as pd
import streamlit_ext as ste
import geopandas as gpd

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

st.title("PyDeck Point Rendering")
st.write('PyDeck Point Rendering')


col1, col2 = st.columns(2)

@st.cache_data
def download_csv(df):  
    if not df.empty:
        csv = df.to_csv(encoding ='utf-8')        
        click = ste.download_button(
        label= "Download CSV ",
        data = csv,
        file_name= "points.csv",
        mime = "text/csv")        

@st.cache_data      
def download_geojson(df):
    if not df.empty:
        gdf = gpd.GeoDataFrame(
                    df, geometry=gpd.points_from_xy(df[lon_column], df[lat_column])
                )
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download GeoJSON",
            file_name= "points.geojson",
            mime="application/json",
            data=geojson
        ) 

with col1:
    url = st.text_input(
        "Enter a CSV URL with Latitude and Longitude Columns",
        # 'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/airports.csv'
        'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv'
    )
    uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
    lat_column_index, lon_column_index = 0,0     
    if url:   
        df = pd.read_csv(url,skiprows=[1],encoding = "UTF-8")                
    if uploaded_file:        
        df = pd.read_csv(uploaded_file,skiprows=[1],encoding = "UTF-8")
    
    for column in df.columns:
            if (column.lower() == 'y' or column.lower().startswith("lat") or column.lower().startswith("n")):
                lat_column_index=df.columns.get_loc(column)
            if (column.lower() == 'x' or column.lower().startswith("ln") or column.lower().startswith("lon") or column.lower().startswith("e") ):
                lon_column_index=df.columns.get_loc(column)
    col1_1, col1_2 = col1.columns(2)
    with col1_1:
        lat_column = col1_1.selectbox('Latitude Column', df.columns, index = lat_column_index)
    with col1_2:
        lon_column = col1_2.selectbox('Longitude Column',df.columns, index = lon_column_index)  

    form = st.form(key="pydeck_pointrender")
    with form:
        options = st.multiselect(
            'Types of rendering:',
            ['HeatmapLayer', 'ScatterplotLayer', 'HexagonLayer' ]
            )

        st.write('You selected:', options)
                          
        submitted = st.form_submit_button("PyDeck Point Render")        
    # st.write(df)


if submitted:           
    with col2:    
        maen_lat_column =  df[lat_column].mean()    
        maen_lon_column =  df[lon_column].mean()
        view_state = pdk.ViewState(latitude=maen_lat_column, longitude=maen_lat_column, bearing=0, pitch=20, zoom=9)
        
        scatterplot_layer = pdk.Layer(
            'ScatterplotLayer',     # Change the `type` positional argument here
            df,
            get_position=[lon_column, lat_column],
            auto_highlight=True,
            get_radius=1000,          # Radius is given in meters
            get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
            pickable=True)

        hexagon_layer = pdk.Layer(
            'HexagonLayer',
            df,
            get_position=[lon_column, lat_column],
            auto_highlight=True,
            elevation_scale=100,
            pickable=True,
            elevation_range=[0, 100],
            extruded=True,
            coverage=1,
        )     

        

        deck = pdk.Deck(
        # map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        map_style=None,
        # layers=[scatterplot_layer,hexagon_layer]
        layers=[scatterplot_layer]
        )


        st.pydeck_chart(deck)
        # deck.to_html("pydeck.html")
        # maen_lat_column =  df[lat_column].mean()    
        # maen_lon_column =  df[lon_column].mean()
        # m = folium.Map(tiles="cartodbpositron", location = [maen_lat_column,maen_lon_column], zoom_start =4)
        # Fullscreen(                                                         
        #     position                = "topright",                                   
        #     title                   = "Open full-screen map",                       
        #     title_cancel            = "Close full-screen map",                      
        #     force_separate_button   = True,                                         
        # ).add_to(m)             
        # cluster = MarkerCluster()
        # for i, j in df.iterrows():
        #     icon=folium.Icon(color='purple', icon='ok-circle')
        #     # iframe = folium.IFrame(popContent)
        #     # popup = folium.Popup(popContent,min_width=200,max_width=200) 
        #     popup = j.to_frame().to_html()
        #     folium.Marker(location=[df.loc[i,lat_column], df.loc[i, lon_column]], icon=icon, popup=popup).add_to(cluster)
                                                                                                                    
        # m.add_child(cluster)            
        # folium_static(m, width = 600)
        # download_csv(df)
        # download_geojson(df)


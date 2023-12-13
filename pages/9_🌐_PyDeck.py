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
import h3

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
def load_data(csv_file):
    # Load data from CSV file
    data = pd.read_csv(csv_file,encoding = "UTF-8")
    return data


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
        #  'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/india_points.csv'
         'https://raw.githubusercontent.com/visgl/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv'
    )
    uploaded_file = st.file_uploader("Or upload a CSV file with Latitude and Longitude Columns")
    lat_column_index, lon_column_index = 0,0     
    if url:   
        df = load_data(url)  
                    
    if uploaded_file:        
        df =load_data(uploaded_file)
    st.write ('No. of records:', len(df))

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

        # st.write('You selected:', options)
                          
        submitted = st.form_submit_button("PyDeck Point Render")        
    # st.write(df)

def get_h3_index(row):
    return h3.geo_to_h3(row[lat_column], row[lon_column], resolution=3)  # Adjust resolution as needed

if submitted:           
    with col2:    
        maen_lat_column =  df[lat_column].mean()    
        maen_lon_column =  df[lon_column].mean()

        scatterplot_layer = pdk.Layer(
            'ScatterplotLayer',     # Change the `type` positional argument here
            df,
            get_position=[lon_column, lat_column],
            auto_highlight=True,
            get_radius=1000,          # Radius is given in meters
            get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
            pickable=True)

        icon_layer = pdk.Layer(
                'IconLayer',
                data=df,
                get_position=[lon_column, lat_column],
                # get_icon='your_icon_column_name',  # Replace 'your_icon_column_name' with the column containing icon information
                get_size=50,
                pickable=True,
                auto_highlight=True,
        )
        
        tooltip = {
            'html': '<b>Count:</b> {elevationValue}',
            'style': {
                'backgroundColor': 'steelblue',
                'color': 'white',
                'fontSize': '12px',
            }
        }
        
        hexagon_layer = pdk.Layer(
            'HexagonLayer',
            df,
            get_position=[lon_column, lat_column],
            auto_highlight=True,
            elevation_scale=100,
            pickable=True,
            elevation_range=[0, 1000],
            extruded=True,
            radius = 10000,
            upperPercentile = 100,
            coverage=1                 
        )     
      
        hexagon_layer.tooltip = tooltip

        heatmap_layer = pdk.Layer(
            'HeatmapLayer',
            data=df,
            get_position=[lon_column, lat_column],
            # get_weight='weight',
            opacity=0.8,
            threshold=0.3,
            aggregation='SUM'
        )
        

        grid_layer = pdk.Layer(
            "GridLayer",
            df,
            get_position=[lon_column, lat_column],
            cell_size=1000,  # Adjust cell size as needed
            elevation_scale=50,
            pickable=True,
            extruded=True,
        )
        
        pointcloud_layer = pdk.Layer(
            'PointCloudLayer',
            data=df,
            get_position=[lon_column, lat_column],
            get_color=[255, 255, 255],
            get_normal=[0, 0, 15],
            auto_highlight=True,
            pickable=True,
            point_size=3,
        )
        view = pdk.View(type="OrbitView", controller=True)

        cluster_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=[lon_column, lat_column],
                get_radius=1000,
                get_fill_color=[0, 255, 255, 120],
            )
        
        # df['hex'] = df.apply(get_h3_index, axis=1)
        # # Group points by H3 indexes to cluster them and count points in each hexagon
        # df = df.groupby('hex').size().reset_index(name='count')
        # st.write(df)

        # # df = pd.read_json(H3_HEX_DATA)

        # # Define a layer to display on a map
        # h3hexagon_layer = pdk.Layer(
        #     "H3HexagonLayer",
        #     df,
        #     pickable=True,
        #     stroked=True,
        #     filled=True,
        #     extruded=False,
        #     get_hexagon="hex",
        #     get_fill_color="[255, count/10, 0, 60]",
        #     get_line_color=[255 , 255, 255],
        #     line_width_min_pixels=2,
        # )

        # Render
        
        view_state = pdk.ViewState(latitude=df[lat_column].mean() , longitude=df[lon_column].mean(), bearing=0, pitch=20, zoom=4)
        # view_state = pdk.ViewState(latitude=37.7749295, longitude=-122.4194155, zoom=14, bearing=0, pitch=30)


        
        deck = pdk.Deck(
        # map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        # map_style=None,
        # layers=[scatterplot_layer,hexagon_layer]
        # layers=[scatterplot_layer],
        layers=[scatterplot_layer],
        # tooltip={"text": "Count: {count}"},
        )

        st.pydeck_chart(deck)
        # deck.to_html("pydeck.html")
        

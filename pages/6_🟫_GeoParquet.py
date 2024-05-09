import streamlit as st
from folium.plugins import Fullscreen
import streamlit_ext as ste
import leafmap, os
import leafmap.foliumap as leafmap

st.set_page_config(layout="wide")
# st.sidebar.info(
#     """
#     - Web: [Geoprocessing Streamlit](https://geoprocessing.streamlit.app)
#     - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
#     """
# )

# st.sidebar.title("Contact")
# st.sidebar.info(
#     """
#     Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
#     """
# )
st.title("GeoParquet Data Visualization")
st.write('GeoParquet Data Visualization')
col1, col2 = st.columns(2)
def download_geojson(gdf, layer_name):
    if not gdf.empty:        
        geojson = gdf.to_json()  
        ste.download_button(
            label="Download " + layer_name + ' in GeoJson format',
            file_name= layer_name+ '.geojson',
            mime="application/json",
            data=geojson
        ) 

with col1:
    form = st.form(key="timeseries_visualization")
    layername = 'geoparquet'
    with form: 
        url = st.text_input(
                "Enter a GeoParquet file URL",
                'https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/polygon.parquet'
            )
        uploaded_file = st.file_uploader("Or upload a GeoParquet file")
        if url:   
            gdf = leafmap.read_parquet(url, return_type="gdf", src_crs="EPSG:4326")
            layername = url.split("/")[-1].split(".")[0]            
        if uploaded_file:        
            gdf = leafmap.read_parquet(uploaded_file, return_type="gdf", src_crs="EPSG:4326")

            layername = os.path.splitext(uploaded_file.name)[0]        
      
        submitted = st.form_submit_button("Display GeoParquet on Map")    
    

if submitted:
    m = leafmap.Map(tiles='cartodbpositron')    
    # Add data to the map
    m.add_gdf(gdf, layer_name=layername)
    m.to_streamlit()
    download_geojson(gdf,layername)   




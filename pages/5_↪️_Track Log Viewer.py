import streamlit as st
from streamlit_keplergl import keplergl_static
import pandas as pd
from keplergl import KeplerGl

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
st.title("GPS Tracklog Viewer")
st.write('GPS Tracklog Viewer')

# Load data
@st.cache_data 
def load_data():
    df = pd.read_csv('https://raw.githubusercontent.com/thangqd/geoprocessing/main/data/csv/gps_noise_2.csv')
    return df

df = load_data()

# Display KeplerGL map
st.title('Replay Track Points Based on datetime')
st.write('This app replays track points from a CSV file based on a datetime field.')

config = {
    "version": "v1",
    "config": {
        "mapState": {
            "latitude": 0,
            "longitude": 0,
            "zoom": 1
        }
    }
}

# Function to display KeplerGL map
# def display_map(df):
#     return keplergl_static(height=600, data={"data_1": df}, config=config)

# map = display_map(df)

my_map = KeplerGl(data={"data_1": df}, config = config, height=600)
keplergl_static(my_map, center_map=True)


start_datetime = df['datetime'].min()
end_datetime = df['datetime'].min()
# Function to update map with selected time range
def update_map(start_date, end_date):
    selected_data = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
    my_map.json_dict = {"data_1": selected_data.to_dict(orient='records')}

update_map(start_datetime, end_datetime)

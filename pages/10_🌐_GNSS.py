import streamlit as st
from ftplib import FTP
import io
import pandas as pd
from datetime import datetime
import altair as alt
import folium
from folium.plugins import MarkerCluster, FastMarkerCluster, Fullscreen
from streamlit_folium import st_folium, folium_static
import streamlit_ext as ste

# Streamlit app
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

st.title('GNSS App')
col1, col2 = st.columns(2)
# Function to retrieve CSV file from FTP
def get_csv_from_ftp(host, username, password, folder, filename):
    date_str =filename.split("-")[2]
    ftp = FTP(host)
    ftp.login(username, password)
    ftp.cwd(folder)
    r = io.BytesIO()
    ftp.retrbinary('RETR ' + filename, r.write)
    r.seek(0)
    header_list = ['id', 'time', 'latitude','N', 'longitude', 'E','fix','satellites','HDOP','altitude','M','height', 'm', 'DGPS_id','checksum' ]
    # with open(r, 'r+') as file:
    #     content = file.read()
    #     file.seek(0, 0)
    #     file.write(header + content)
    df_origin = pd.read_csv(r, header= None,dtype={1:"string"} )
    df_origin.to_csv(filename, header=header_list, index=False)
    df = pd.read_csv(filename,dtype={"time":"string"})
    df['latitude'] = df['latitude']/100
    df['longitude'] = df['longitude']/100
    df['time'] = df['time'].str[:6]
    df['datetime'] = pd.to_datetime(date_str+df['time'], format='%Y%m%d%H%M%S')
    # df['time'] = df['datetime'].dt.time

    # time_str = df['time']
    return df

def list_csv_files(ftp, folder):
    try:
        ftp.cwd(folder)
        files = ftp.nlst()
        csv_files = [file for file in files if file.lower().endswith('.txt')]
        return csv_files
    except Exception as e:
        st.error(f"Failed to list files: {e}")
        return []

def ftp_login(host, username, password):
    try:
        ftp = FTP(host)
        ftp.login(username, password)
        return ftp
    except Exception as e:
        st.error(f"Failed to connect to FTP server: {e}")
        return None

with col1:
    form = st.form(key="login")
    with form:
        ftp_server = st.text_input("FTP Host",'ftp.quantraccongtrinh.com')
        ftp_username = st.text_input("Username",'tester1@quantraccongtrinh.com')
        ftp_password = st.text_input("Password",'Khanh09092009*#', type="password")
        ftp_folder = st.text_input("Folder", 'home/tracdiav/testQT1/')
        submitted = st.form_submit_button("Login")    
    # FTP server details
    # ftp_server = 'ftp.quantraccongtrinh.com'
    # username = 'tester1@quantraccongtrinh.com'
    # password = 'Khanh09092009*#'
    # ftp_folder = '/home/tracdiav/testQT1/'

    # Connect to FTP server

    if submitted:
        ftp = ftp_login(ftp_server, ftp_username, ftp_password)
        if ftp:
            st.success("Logged in to FTP server successfully!")
            with col2:
                csv_files = list_csv_files(ftp, ftp_folder)
                if csv_files:
                    # st.write("List of CSV files:")
                    # for file in csv_files:
                    #     st.write(file)
                    # Add double-click event handling
                    selected_file = st.selectbox('Select a CSV file:', csv_files)
                    # selected_file = st.table(csv_files)

                    # form = st.form(key="display")
                    # with form:
                        # display  = st.form_submit_button("Display")    
                    display = st.button('Display')
                    if (display):
                            # st.write(f"Selected file: {selected_file}")
                            # # Get selected CSV file from FTP
                            # df = get_csv_from_ftp(ftp_server,ftp_username, ftp_password, ftp_folder, selected_file)
                            # st.write(df) 
                            # min_altitude = df['altitude'].min()
                            # max_altitude = df['altitude'].max()
                            # line = alt.Chart(df).mark_line().encode(
                            #     x='time',
                            #     y='altitude',
                            #     )
                            
                            # points = alt.Chart(df).mark_point().encode(                        
                            #     x=alt.X("time", axis=alt.Axis(
                            #                 labelOverlap=True, 
                            #                 labelAngle=-45,
                            #                 # tickCount=len(df['datetime']),
                            #             )),
                            #     y=alt.Y('altitude', scale=alt.Scale(domain=[min_altitude,max_altitude])),
                            #     color=alt.value('red'),
                            #     tooltip=["time","altitude"]
                            #     )
                            # c = (alt.layer(points, line)).interactive()                   

                            # st.altair_chart(c, use_container_width=True)

                            # # m = folium.Map(tiles = "https://maps.becagis.vn/tiles/basemap/light/{z}/{x}/{y}.png", attr="BecaGIS Maps", location = [df['latitude'].mean(), df['longitude'].mean() ], zoom_start =12)
                            # m = folium.Map(tiles='cartodbdark_matter', location = [df['latitude'].mean(), df['longitude'].mean() ], zoom_start =12)

                            # Fullscreen(                                                         
                            #     position                = "topright",                                   
                            #     title                   = "Open full-screen map",                       
                            #     title_cancel            = "Close full-screen map",                      
                            #     force_separate_button   = True,                                         
                            # ).add_to(m)             
                            # cluster = MarkerCluster()
                            # for latitude, longigude, Datetime, Altitude in zip(df.latitude, df.longitude, df.datetime, df.altitude):
                            #     # color = 'purple'
                            #     icon=folium.Icon(icon='ok-circle')
                            #     popContent = ("Datetime: " + str(Datetime) + '<br>'+\
                            #                 "Altitude: " + str(Altitude) + '<br>'                               
                            #                 # "WQI_Level: " +  "<font color=" + color + ">" + str(WQI_Level) + "</font> ")
                            #                 )   
                            #     iframe = folium.IFrame(popContent)
                            #     popup = folium.Popup(iframe,
                            #                         min_width=200,
                            #                         max_width=200)   
                            #     folium.Marker(location=[latitude, longigude], icon=icon, popup=popup).add_to(cluster)    
                            # m.add_child(cluster)            
                            # folium_static(m, width = 700)
                            # st.write(df['altitude'].describe())
                            st.warning('selected_file')

                else:
                    st.write("No CSV files found in the chosen folder.")
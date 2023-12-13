import streamlit as st
from ftplib import FTP
import io
import pandas as pd
from datetime import datetime
import altair as alt
import leafmap

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
    form = st.form(key="timeseries_visualization")
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
                    st.write(f"Selected file: {selected_file}")
                    # Get selected CSV file from FTP
                    selected_csv_data = get_csv_from_ftp(ftp_server,ftp_username, ftp_password, ftp_folder, selected_file)
                    st.write(selected_csv_data)  
                    c = (
                    alt.Chart(selected_csv_data)
                    .mark_point() #mark_bar()/ mark_point()/ mark_line(), mark_circle()
                    .encode(
                            x=("datetime:T"), 
                            # x=alt.X("datetime:T", axis=alt.Axis(
                            #     format="%Y-%M-%D", 
                            #     labelOverlap=True, 
                            #     labelAngle=-45,
                            #     tickCount=len(df.date),
                            # )),
                            y="altitude", 
                            color="id", tooltip=["id","datetime","altitude"]
                            )
                    ).interactive()                  

                    st.altair_chart(c, use_container_width=True)
                    st.write(selected_csv_data['altitude'].describe())
                else:
                    st.write("No CSV files found in the chosen folder.")

            # if ftp_server and ftp_username and ftp_password:
            #     # Attempt to login to the FTP server
            #     ftp_connection = ftp_login(ftp_server, ftp_username, ftp_password)
            #     if ftp_connection:
            #         # Perform actions after successful login
            #         # Here you can add FTP operations that you want to perform after login
            #         # List all files in the FTP directory
            #         file_list = ftp_connection.nlst()
            #         # Filter CSV files
            #         csv_files = [file for file in file_list if file.lower().endswith('.txt')]

            #         if len(csv_files) > 0:
            #             selected_file = st.selectbox('Select a CSV file:', csv_files)
            #             st.write(f"Selected file: {selected_file}")

            #             # Get selected CSV file from FTP
            #             selected_csv_data = get_csv_from_ftp(ftp_server,ftp_username, ftp_password, ftp_folder, selected_file)
                        
            #             # Display the content of the CSV file
            #             st.write(selected_csv_data)
            #         else:
            #             st.write("No CSV files found in the FTP directory.")

            #         # Close FTP connection
            #         ftp_connection.quit()
            # else:
            #     st.warning("Please fill in all fields.")

    # ftp = FTP(ftp_server)
    # ftp.login(username, password)
    # ftp.cwd(ftp_folder)






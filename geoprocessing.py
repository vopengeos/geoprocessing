import streamlit as st

st.set_page_config(layout="wide")

st.sidebar.info(
    """
    - GitHub: [Geoprocessing Streamlit](https://github.com/thangqd/geoprocessing) 
    """
)

st.sidebar.title("Contact")
st.sidebar.info(
    """
    Thang Quach: [My Homepage](https://thangqd.github.io) | [GitHub](https://github.com/thangqd) | [LinkedIn](https://www.linkedin.com/in/thangqd)
    """
)
# Customize page title
# col1, mid, col2 = st.columns([1,1,20])
# with col1:
#     st.image("./data/images/becagis.png", width = 90)
# with col2:
#     st.title("BecaGIS on Streamlit")
st.title("Geoprocessing Streamlit")
st.image("./data/images/flight_routes.png")

st.markdown(
    """
    GeoProcessing Streamlit is inspired by [streamlit-geospatial](https://github.com/giswqs/streamlit-geospatial).
    """
)
# from streamlit_extras.buy_me_a_coffee import button
# button(username="thangqd", floating=False, width=221)

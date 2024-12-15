import streamlit as st
from streamlit import Page

# from st_pages import Page, show_pages, add_page_title

# https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/ a good reference to dashboards in Streamlit

pg = st.navigation(
    [
        Page("pages/home.py", title="Home", icon="🏠"),
        Page("pages/demo.py", title="Demo", icon="🎬"),
        Page("pages/detailed_info.py", title="Detailed Information", icon="🌐"),
    ]
)
st.set_page_config(page_title="Streamlit Dashboard", page_icon="📈", layout="wide")
pg.run()

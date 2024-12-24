import streamlit as st
from streamlit import Page

pg = st.navigation(
    [
        Page("dashboards/avg_screentime.py", title="Average Screentime", icon="🖥️"),
        Page("dashboards/demo.py", title="Demo", icon="🎬"),
        Page("dashboards/detailed_info.py", title="Detailed Information", icon="🌐"),
    ]
)
pg.run()

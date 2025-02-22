import streamlit as st
from streamlit import Page

pg = st.navigation(
    [
        Page("dashboards/avg_screentime.py", title="Average Screentime", icon="🖥️"),
        Page("dashboards/demo.py", title="Demo", icon="🎬"),
        Page("dashboards/detailed_info.py", title="Detailed Information", icon="🌐"),
        Page("dashboards/detailed_info_2.py", title="Detailed Information 2", icon="🌐"),
        Page("dashboards/detailed_info_3.py", title="Detailed Information 3", icon="🌐"),
        Page("dashboards/duckdb_shell.py", title="DuckDB Shell", icon=""),
    ]
)
pg.run()

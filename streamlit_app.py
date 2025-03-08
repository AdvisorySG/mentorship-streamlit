import streamlit as st
from streamlit import Page

pg = st.navigation(
    [
        Page("dashboards/avg_screentime.py", title="Average Screentime", icon="🖥️"),
        Page("dashboards/demo.py", title="Demo", icon="🎬"),
        Page("dashboards/detailed_info.py", title="Detailed Information", icon="🌐"),
        Page("dashboards/clicks_and_impressions.py", title="Clicks & Impressions", icon=""),
        Page("dashboards/categorical_analysis.py", title="Categorical Analysis", icon=""),
        Page("dashboards/duckdb_shell.py", title="DuckDB Shell", icon=""),
    ]
)
pg.run()

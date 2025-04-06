import streamlit as st
import duckdb

from utils.duckdb import get_dbcur

cur = get_dbcur()
columns = ["industries", "organisation", "course_of_study", "school"]
db = cur.sql("SELECT * FROM mentors_clicks;").fetchdf()
full_size = len(db)
conn = duckdb.connect()
cur2 = conn.cursor()

# This is for the form (the one w the button)
with st.form("full query"):
    to_filter_columns = []
    filter_dict = {}
    with st.container():
        to_filter = st.multiselect("Filter dataframe on", columns)
    for filter in to_filter:
        left, right = st.columns((1, 20))
        left.write("↳")
        user_text_input = right.text_input(f"Enter sub filter string in {filter}")
        if user_text_input:
            filter_dict[filter] = user_text_input
    query = st.form_submit_button("Query")
    if query and filter_dict:
        db_copy = db.copy()
        for filter, query in filter_dict.items():
            if filter == "" or query == "":
                continue
            db_copy = cur2.execute(
                f"""SELECT * FROM db_copy WHERE CAST({filter} AS VARCHAR) ILIKE {"'%" + query + "%'"};"""
            ).fetch_df()
        st.write(
            "Percentage of data that has this combination: ",
            len(db_copy) / full_size * 100,
            "%",
        )
        st.dataframe(db_copy)

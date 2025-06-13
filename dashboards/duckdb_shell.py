from code_editor import code_editor
import streamlit as st

import time
import traceback

from utils.duckdb import get_dbcur

st.set_page_config(layout="wide")

cur = get_dbcur()

TABLES = [
    "elasticsearch",
    "mentor_visits",
    "umamidb.umami.event_data",
    "umamidb.umami.session",
    "umamidb.umami.session_data",
    "umamidb.umami.website",
    "umamidb.umami.website_event",
]
COMBINED_QUERY = "\n".join(
    ["SHOW ALL TABLES;"]
    + [""]
    + [f"SELECT COUNT(*) FROM {table};" for table in TABLES]
    + [""]
    + [f"SELECT * FROM {table} LIMIT 1000;" for table in TABLES]
)

st.write("Code adapted from [ducklit](https://github.com/MarkyMan4/ducklit).")
st.write("Ctrl+enter to run the SQL commands.")
res = code_editor(COMBINED_QUERY, lang="sql", allow_reset=True, key="editor")

queries = [query for query in res["text"].split(";") if query.strip() != ""]

if len(queries) > 0:
    st.write("## Queries")

    for query in queries:
        st.code(query, "sql")
        try:
            start = time.time()
            cur.execute(query)
            df = cur.pl()
            end = time.time()

            st.write(df)
            st.write(f"Time taken: {round(end - start, 2)} s")
        except Exception:
            st.code(traceback.format_exc())

from code_editor import code_editor
import streamlit as st

import traceback

from utils.duckdb import get_dbcur

st.set_page_config(layout="wide")

cur = get_dbcur()

st.write("Code adapted from [ducklit](https://github.com/MarkyMan4/ducklit).")
st.write("Ctrl+enter to run the SQL commands.")
res = code_editor("SHOW ALL TABLES;", lang="sql", allow_reset=True, key="editor")

for query in res["text"].split(";"):
    if query.strip() == "":
        continue

    try:
        cur.execute(query)
        df = cur.pl()
        st.write(df)
    except Exception:
        st.code(traceback.format_exc())

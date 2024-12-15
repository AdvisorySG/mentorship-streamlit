import datetime
import streamlit as st

from auxiliary_functions import parsing_urls, filter_dataframe


st.title("Detailed Information Dashboard")

# Initialize connection.
conn = st.connection("mysql", type="sql")

# main juicy stuff

df = conn.query("select * from website_event;")

# user search engine
st.subheader("This is a search engine for queries")
st.dataframe(filter_dataframe(parsing_urls(df)))

# shows last 24h stats
st.subheader("This shows queries in the last 24h")

end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(hours=24)
df_filtered = df[(start_time < df["created_at"]) & (df["created_at"] < end_time)]
st.dataframe(parsing_urls(df_filtered))

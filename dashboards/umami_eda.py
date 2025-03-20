import streamlit as st
from utils.duckdb import get_dbcur
import pandas as pd
import plotly.express as px

GET_UMAMI_SESSION_QUERY = (
    "SELECT CAST(created_at AS datetime) AS date, * FROM umamidb.umami.session"
)
GET_UMAMI_WEBSITE_EVENTS_QUERY = (
    "SELECT * FROM umamidb.umami.website_event LIMIT 1000"  # TODO UPDATE
)

cur = get_dbcur()
cur.execute(GET_UMAMI_SESSION_QUERY)
results = cur.fetchall()
columns = [desc[0] for desc in cur.description]  # Get column names
sess_df = pd.DataFrame(results, columns=columns)

cur.execute(GET_UMAMI_WEBSITE_EVENTS_QUERY)
website_df = cur.pl()
# --------------------------------------------------------------------------------------

st.title("Section 1: Umami Session Dashboard!")
sess_df["date"] = pd.to_datetime(sess_df["date"])
st.dataframe(sess_df)

# Daily Counts
daily_counts = sess_df.groupby(sess_df["date"].dt.date).size()
daily_counts = daily_counts.reset_index(name="count")
daily_counts.columns = ["day", "count"]
st.dataframe(daily_counts)

# Weekly Counts
weekly_counts = sess_df.groupby(sess_df["date"].dt.isocalendar().week).size()
weekly_counts = weekly_counts.reset_index(name="count")
weekly_counts.columns = ["week", "count"]
st.dataframe(weekly_counts)

# Monthly Counts
monthly_counts = sess_df.groupby(sess_df["date"].dt.month).size()
monthly_counts = monthly_counts.reset_index(name="count")
monthly_counts.columns = ["month", "count"]
st.dataframe(monthly_counts)

# Quarter Counts
quarter_counts = (
    sess_df.groupby(sess_df["date"].dt.to_period("Q")).size().reset_index(name="count")
)
quarter_counts["date"] = quarter_counts["date"].astype(str)
quarter_counts.columns = ["quarter", "count"]

# Year Counts
year_counts = sess_df.groupby(sess_df["date"].dt.year).size().reset_index(name="count")
year_counts["date"] = year_counts["date"].astype(str)
year_counts.columns = ["year", "count"]

# ---Visualisations---

# Daily Chart
st.subheader("Daily Record Counts")
fig_daily = px.line(daily_counts, x="day", y="count", title="Daily Record Counts")
st.plotly_chart(fig_daily)

# Weekly Chart
st.subheader("Weekly Record Counts")
fig_weekly = px.line(weekly_counts, x="week", y="count", title="Weekly Record Counts")
st.plotly_chart(fig_weekly)

# Monthly Chart
st.subheader("Monthly Record Counts")
fig_monthly = px.line(
    monthly_counts, x="month", y="count", title="Monthly Record Counts"
)
st.plotly_chart(fig_monthly)

# Quarter Chart
st.subheader("Quarterly Record Counts")
fig_quarter = px.line(
    quarter_counts, x="quarter", y="count", title="Quarterly Record Counts"
)
st.plotly_chart(fig_quarter)

# Year Chart
st.subheader("Yearly Record Counts")
fig_year = px.line(year_counts, x="year", y="count", title="Yearly Record Counts")
st.plotly_chart(fig_year)


# --------------------------------------------------------------------------------------
# TODO
# combine n update from existing B PR

st.title("Section 2: Umami Website Event Dashboard! (TODO)")

# st.dataframe(website_df)

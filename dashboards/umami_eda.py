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

st.title("P1: Analytics Across Time Periods")

sess_df["date"] = pd.to_datetime(sess_df["date"])
st.dataframe(sess_df)

# Daily Counts
daily_counts = sess_df.groupby(sess_df["date"].dt.date).size()
daily_counts = daily_counts.reset_index(name="count")
daily_counts.columns = ["day", "count"]

# Weekly Counts
weekly_counts = sess_df.groupby(sess_df["date"].dt.isocalendar().week).size()
weekly_counts = weekly_counts.reset_index(name="count")
weekly_counts.columns = ["week", "count"]

# Monthly Counts
monthly_counts = sess_df.groupby(sess_df["date"].dt.month).size()
monthly_counts = monthly_counts.reset_index(name="count")
monthly_counts.columns = ["month", "count"]

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

# ---P2---
st.title("P2: Session Analytics of Latest Time Period")

# Sliding bar for K months
max_months = (
    (sess_df["date"].max().year - sess_df["date"].min().year) * 12
    + (sess_df["date"].max().month - sess_df["date"].min().month)
    + 1
)
k_months = st.slider("Select Last K Months", min_value=1, max_value=max_months, value=3)

# Filter for the last K months
latest_date = sess_df["date"].max()
cutoff_date = latest_date - pd.DateOffset(months=k_months)
filtered_sess_df = sess_df[sess_df["date"] >= cutoff_date]

st.dataframe(filtered_sess_df)

# Simplify Pie Chart Checkbox
simplify_pie = st.checkbox("Simplify Pie Charts? (Combine Elements < 1%)")

# Pie Charts
columns_to_analyze = ["browser", "os", "device", "language", "country"]

for col in columns_to_analyze:
    st.subheader(f"Pie Chart - {col.capitalize()}")
    counts = filtered_sess_df[col].value_counts(normalize=True)

    if simplify_pie:
        others_percentage = counts[
            counts < 0.01
        ].sum()  # Calculate percentage for "Others"
        counts = counts[counts >= 0.01]  # Filter out values < 1%
        if others_percentage > 0:
            counts["Others"] = others_percentage  # Add "Others" to counts

    fig = px.pie(
        counts,
        values=counts.values,
        names=counts.index,
        title=f"{col.capitalize()} Distribution",
    )
    st.plotly_chart(fig)


# --------------------------------------------------------------------------------------
# TODO - combine n update from existing B PR

st.title("Section 2: Umami Website Event Dashboard! (TODO)")

# st.dataframe(website_df)

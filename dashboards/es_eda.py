import streamlit as st
from utils.duckdb import get_dbcur

import plotly.express as px

GET_ES_DB_QUERY = "SELECT * FROM elasticsearch"
cur = get_dbcur()
cur.execute(GET_ES_DB_QUERY)
es_df = cur.pl()

st.title("ES EDA Dashboard!")

st.subheader("ES Data Snapshot")
st.dataframe(es_df)

# --------------------------------------------------------------------------------------

st.subheader("P1: Course of Study (TODO)")

# 1. Value Counts (Bar Chart)
st.subheader("Course of Study Distribution")
course_counts_desc_df = es_df["course_of_study"].value_counts(sort=True)
course_counts_desc_df.columns = ["Course", "Count"]  # rename the columns

fig_bar = px.bar(
    course_counts_desc_df, x="Course", y="Count", labels={"Count": "Count"}
)  # use the column names from the dataframe
st.plotly_chart(fig_bar)

# 2. Value Counts (Table)
st.subheader("Course of Study Counts (Table)")
st.dataframe(course_counts_desc_df)

# Create visualisations for the top K records
# User input for K using a slider, deafult at K=20, max of 40 set arbitraily
top_k = st.slider("Select the number of top courses to display:", 1, 40, 20)
top_k_courses = course_counts_desc_df.head(top_k)

# 3. Create the pie chart for the top K records
st.subheader(f"Top {top_k} Course Proportions")
fig_pie_top_k = px.pie(
    top_k_courses,
    values="Count",
    names="Course",
    title=f"Top {top_k} Course Distribution",
)
st.plotly_chart(fig_pie_top_k)

# 4. Create the bar chart for the top K records
st.subheader(f"Top {top_k} Course Counts (Bar Chart)")
fig_bar_top_k = px.bar(
    top_k_courses, x="Course", y="Count", title=f"Top {top_k} Course Counts"
)
st.plotly_chart(fig_bar_top_k)

# TODO:
# remove nulls
# For bar charts: insert calculation and showing each course % of total popn (eg econs = 12%, biz = 8.3%)
# jared to look into - clustering or semantic grouping based on similar courses? since some courses with smaller representation are subset of bigger ones


# --------------------------------------------------------------------------------------

st.subheader("P2: Industries")

# Calculate value counts
# Note usage of explode function, since industries column original data type was a list, hence explode the lists to parse individual elements
industry_counts_desc = es_df["industries"].explode().value_counts(sort=True)
industry_counts_desc.columns = ["Industry", "Count"]

# Full data bar chart
st.subheader("Industry Counts (Full Data)")
fig_bar = px.bar(industry_counts_desc, x="Industry", y="Count", title="Industry Counts")
st.plotly_chart(fig_bar)

top_k = st.slider(
    "Select the number of top industries to display:", 1, len(industry_counts_desc), 20
)
top_k_industries = industry_counts_desc.head(top_k)

# Pie chart for top K industries
st.subheader(f"Top {top_k} Industry Proportions (Pie Chart)")
fig_pie_top_k = px.pie(
    top_k_industries,
    values="Count",
    names="Industry",
    title=f"Top {top_k} Industry Distribution",
)
st.plotly_chart(fig_pie_top_k)

# Bar chart for top K industries
st.subheader(f"Top {top_k} Industry Counts (Bar Chart)")
fig_bar_top_k = px.bar(
    top_k_industries, x="Industry", y="Count", title=f"Top {top_k} Industry Counts"
)
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P3: Organisations")

org_counts_desc = es_df["organisation"].value_counts(sort=True)
org_counts_desc.columns = ["Organisation", "Count"]

# Full data bar chart
st.subheader("Organisation Counts (Full Data)")
fig_bar = px.bar(
    org_counts_desc, x="Organisation", y="Count", title="Organisation Counts"
)
st.plotly_chart(fig_bar)

# Slider for top K organisations
max_slider_value = min(40, len(org_counts_desc))
top_k = st.slider(
    "Select the number of top organisations to display:", 1, max_slider_value, 20
)
top_k_orgs = org_counts_desc.head(top_k)

# Pie chart for top K organisations
st.subheader(f"Top {top_k} Organisation Proportions (Pie Chart)")
fig_pie_top_k = px.pie(
    top_k_orgs,
    values="Count",
    names="Organisation",
    title=f"Top {top_k} Organisation Distribution",
)
st.plotly_chart(fig_pie_top_k)

# Bar chart for top K organisations
st.subheader(f"Top {top_k} Organisation Counts (Bar Chart)")
fig_bar_top_k = px.bar(
    top_k_orgs, x="Organisation", y="Count", title=f"Top {top_k} Organisation Counts"
)
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P4: Roles (TODO)")

role_counts_desc = es_df["role"].value_counts(sort=True)
role_counts_desc.columns = ["Role", "Count"]
st.dataframe(role_counts_desc)


# TODO:
# bar n pie chart of all plus Top K with sliding car (refer to above previously done code)
# jared to look into - clustering or semantic grouping based on seniority

# --------------------------------------------------------------------------------------

st.subheader("P5: Schools (TODO)")

school_counts_desc = es_df["school"].value_counts(sort=True)
school_counts_desc.columns = ["School", "Count"]
st.dataframe(school_counts_desc)

# TODO:
# bar n pie chart of all plus Top K with sliding car (refer to above previously done code)

# --------------------------------------------------------------------------------------

st.subheader("P6: Waves (TODO)")

waveid_counts_desc = es_df["wave_id"].value_counts(sort=True)
waveid_counts_desc.columns = ["WaveID", "Count"]
st.dataframe(waveid_counts_desc)

# TODO:
# bar charts showing breakdown organised based on yearly basis (ie. 2021, 2022, ..), values aggregated on year
# another sub bar chart showing within each year separate waves breakdown; eg 2021 show 2x bars for 2021-1, 2021-2; also 2023 show one set for 2023-2 and 2023-vjc

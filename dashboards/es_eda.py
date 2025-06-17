import streamlit as st
from utils.duckdb import get_dbcur
import plotly.express as px

GET_ES_DB_QUERY = "SELECT * FROM elasticsearch"
cur = get_dbcur()
cur.execute(GET_ES_DB_QUERY)
es_df = cur.pl().to_pandas()

# Remove nulls for relevant columns
es_df = es_df.dropna(subset=["course_of_study", "industries", "organisation", "role", "school", "wave_id"])

st.title("ES EDA Dashboard!")

st.subheader("ES Data Snapshot")
st.dataframe(es_df)

# --------------------------------------------------------------------------------------

st.subheader("P1: Course of Study")

course_counts_desc_df = es_df["course_of_study"].value_counts().reset_index()
course_counts_desc_df.columns = ["Course", "Count"]
course_counts_desc_df["Percentage"] = (course_counts_desc_df["Count"] / course_counts_desc_df["Count"].sum()) * 100

fig_bar = px.bar(course_counts_desc_df, x="Course", y="Count", text=course_counts_desc_df["Percentage"].round(1).astype(str) + '%')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

st.subheader("Course of Study Counts (Table)")
st.dataframe(course_counts_desc_df)

top_k = st.slider("Select the number of top courses to display:", 1, 40, 20)
top_k_courses = course_counts_desc_df.head(top_k)

st.subheader(f"Top {top_k} Course Proportions")
fig_pie_top_k = px.pie(top_k_courses, values="Count", names="Course", title=f"Top {top_k} Course Distribution")
st.plotly_chart(fig_pie_top_k)

st.subheader(f"Top {top_k} Course Counts (Bar Chart)")
fig_bar_top_k = px.bar(top_k_courses, x="Course", y="Count", text=top_k_courses["Percentage"].round(1).astype(str) + '%')
fig_bar_top_k.update_traces(textposition='outside')
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P2: Industries")

industry_counts_desc = es_df["industries"].explode().value_counts().reset_index()
industry_counts_desc.columns = ["Industry", "Count"]
industry_counts_desc["Percentage"] = (industry_counts_desc["Count"] / industry_counts_desc["Count"].sum()) * 100

st.subheader("Industry Counts (Full Data)")
fig_bar = px.bar(industry_counts_desc, x="Industry", y="Count", text=industry_counts_desc["Percentage"].round(1).astype(str) + '%')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

top_k = st.slider("Select the number of top industries to display:", 1, len(industry_counts_desc), 20)
top_k_industries = industry_counts_desc.head(top_k)

st.subheader(f"Top {top_k} Industry Proportions (Pie Chart)")
fig_pie_top_k = px.pie(top_k_industries, values="Count", names="Industry", title=f"Top {top_k} Industry Distribution")
st.plotly_chart(fig_pie_top_k)

st.subheader(f"Top {top_k} Industry Counts (Bar Chart)")
fig_bar_top_k = px.bar(top_k_industries, x="Industry", y="Count", text=top_k_industries["Percentage"].round(1).astype(str) + '%')
fig_bar_top_k.update_traces(textposition='outside')
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P3: Organisations")

org_counts_desc = es_df["organisation"].value_counts().reset_index()
org_counts_desc.columns = ["Organisation", "Count"]
org_counts_desc["Percentage"] = (org_counts_desc["Count"] / org_counts_desc["Count"].sum()) * 100

st.subheader("Organisation Counts (Full Data)")
fig_bar = px.bar(org_counts_desc, x="Organisation", y="Count", text=org_counts_desc["Percentage"].round(1).astype(str) + '%')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

max_slider_value = min(40, len(org_counts_desc))
top_k = st.slider("Select the number of top organisations to display:", 1, max_slider_value, 20)
top_k_orgs = org_counts_desc.head(top_k)

st.subheader(f"Top {top_k} Organisation Proportions (Pie Chart)")
fig_pie_top_k = px.pie(top_k_orgs, values="Count", names="Organisation", title=f"Top {top_k} Organisation Distribution")
st.plotly_chart(fig_pie_top_k)

st.subheader(f"Top {top_k} Organisation Counts (Bar Chart)")
fig_bar_top_k = px.bar(top_k_orgs, x="Organisation", y="Count", text=top_k_orgs["Percentage"].round(1).astype(str) + '%')
fig_bar_top_k.update_traces(textposition='outside')
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P4: Roles")

role_counts_desc = es_df["role"].value_counts().reset_index()
role_counts_desc.columns = ["Role", "Count"]
role_counts_desc["Percentage"] = (role_counts_desc["Count"] / role_counts_desc["Count"].sum()) * 100
st.dataframe(role_counts_desc)

fig_bar = px.bar(role_counts_desc, x="Role", y="Count", text=role_counts_desc["Percentage"].round(1).astype(str) + '%')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

top_k = st.slider("Select the number of top roles to display:", 1, min(40, len(role_counts_desc)), 20)
top_k_roles = role_counts_desc.head(top_k)

fig_pie_top_k = px.pie(top_k_roles, values="Count", names="Role", title=f"Top {top_k} Role Distribution")
st.plotly_chart(fig_pie_top_k)

fig_bar_top_k = px.bar(top_k_roles, x="Role", y="Count", text=top_k_roles["Percentage"].round(1).astype(str) + '%')
fig_bar_top_k.update_traces(textposition='outside')
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P5: Schools")

school_counts_desc = es_df["school"].value_counts().reset_index()
school_counts_desc.columns = ["School", "Count"]
school_counts_desc["Percentage"] = (school_counts_desc["Count"] / school_counts_desc["Count"].sum()) * 100
st.dataframe(school_counts_desc)

fig_bar = px.bar(school_counts_desc, x="School", y="Count", text=school_counts_desc["Percentage"].round(1).astype(str) + '%')
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

top_k = st.slider("Select the number of top schools to display:", 1, min(40, len(school_counts_desc)), 20)
top_k_schools = school_counts_desc.head(top_k)

fig_pie_top_k = px.pie(top_k_schools, values="Count", names="School", title=f"Top {top_k} School Distribution")
st.plotly_chart(fig_pie_top_k)

fig_bar_top_k = px.bar(top_k_schools, x="School", y="Count", text=top_k_schools["Percentage"].round(1).astype(str) + '%')
fig_bar_top_k.update_traces(textposition='outside')
st.plotly_chart(fig_bar_top_k)

# --------------------------------------------------------------------------------------

st.subheader("P6: Waves")

# Extract year and wave (e.g., from '2021-1' to 2021)
es_df["year"] = es_df["wave_id"].str.extract(r"(\d{4})")
wave_counts_by_year = es_df["year"].value_counts().sort_index().reset_index()
wave_counts_by_year.columns = ["Year", "Count"]

st.subheader("Wave Counts by Year")
fig_wave_year = px.bar(wave_counts_by_year, x="Year", y="Count", title="Wave Counts by Year")
st.plotly_chart(fig_wave_year)

wave_counts_full = es_df["wave_id"].value_counts().reset_index()
wave_counts_full.columns = ["WaveID", "Count"]

st.subheader("Wave Breakdown (by Wave ID)")
fig_wave_breakdown = px.bar(wave_counts_full, x="WaveID", y="Count", title="Detailed Wave Breakdown")
st.plotly_chart(fig_wave_breakdown)
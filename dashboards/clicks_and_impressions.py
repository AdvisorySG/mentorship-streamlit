import streamlit as st
import matplotlib.pyplot as plt

from utils.duckdb import get_dbcur

st.title("Clicks & Impressions Dashboard")

cur = get_dbcur()

query = """
WITH ranked_events AS (
    SELECT 
        ed.website_event_id,
        es.id AS mentor_id,
        ANY_VALUE(es.name) AS mentor_name,
        SUM(CASE WHEN we.event_name = 'Click' THEN 1 ELSE 0 END) AS click_count,
        SUM(CASE WHEN we.event_name = 'Impression' THEN 1 ELSE 0 END) AS impression_count
    FROM 
        umamidb.event_data ed
    JOIN 
        umamidb.website_event we
        ON ed.website_event_id = we.event_id
    JOIN 
        memory.elasticsearch es
        ON es.id = ed.string_value
    WHERE 
        (we.event_name = 'Click' OR we.event_name = 'Impression')
        AND we.url_path LIKE '/mentors%'
        AND we.referrer_path LIKE '/mentors%'
    GROUP BY 
        ed.website_event_id, 
        es.id
)

SELECT 
    mentor_id,
    ANY_VALUE(mentor_name) AS mentor_name,
    SUM(click_count) AS total_clicks,
    SUM(impression_count) AS total_impressions
FROM 
    ranked_events
GROUP BY 
    mentor_id
ORDER BY 
    total_clicks DESC;
"""

df = cur.execute(query).fetch_df()
top_20_clicks = df.nlargest(20, 'total_clicks')
top_20_impressions = df.nlargest(20, 'total_impressions')

# table to show data
st.subheader("Mentors Data")
st.dataframe(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 20 by Clicks")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_20_clicks['mentor_name'], top_20_clicks['total_clicks'], color='skyblue')
    ax.set_xlabel('Mentor Name')
    ax.set_ylabel('Total Clicks')
    ax.set_title('Top 20 Mentors - Clicks')
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    st.subheader("Total Clicks")
    fig, ax = plt.subplots()
    ax.hist(df['total_clicks'], bins=15, color='skyblue', edgecolor='black')
    ax.set_xlabel('Total Clicks')
    ax.set_ylabel('Number of Mentors')
    ax.set_title('Distribution of Clicks Across Mentors')
    st.pyplot(fig)

with col2:
    st.subheader("Top 20 by Impressions")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_20_impressions['mentor_name'], top_20_impressions['total_impressions'], color='lightgreen')
    ax.set_xlabel('Mentor Name')
    ax.set_ylabel('Total Impressions')
    ax.set_title('Top 20 Mentors - Impressions')
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    st.subheader("Total Impressions")
    fig, ax = plt.subplots()
    ax.hist(df['total_impressions'], bins=15, color='lightgreen', edgecolor='black')
    ax.set_xlabel('Total Impressions')
    ax.set_ylabel('Number of Mentors')
    ax.set_title('Distribution of Impressions Across Mentors')
    st.pyplot(fig)

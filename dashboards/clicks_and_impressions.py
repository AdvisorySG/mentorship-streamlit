import streamlit as st
import pandas as pd
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
        SUM(CASE WHEN we.event_name = 'Click' THEN 1 ELSE 0 END) AS click_count, -- convert to numeric for counting
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
    mentor_name,
    SUM(click_count) AS total_clicks,
    SUM(impression_count) AS total_impressions
FROM 
    ranked_events
GROUP BY 
    mentor_name -- group by mentor name as there are some ids that produce duplicate mentor names
ORDER BY 
    total_clicks DESC;
"""
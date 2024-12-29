import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.duckdb import get_dbcur

st.title("Clicks & Impressions Dashboard")

cur = get_dbcur()

query = """
SELECT 
    ed.website_event_id,
    SUM(CASE WHEN we.event_name = 'Click' THEN 1 ELSE 0 END) AS click_count,
    SUM(CASE WHEN we.event_name = 'Impression' THEN 1 ELSE 0 END) AS impression_count
FROM 
    umamidb.event_data ed
JOIN 
    umamidb.website_event we
    ON ed.website_event_id = we.event_id
WHERE 
    ed.data_key = 'env' AND ed.string_value = 'production'
GROUP BY 
    ed.website_event_id
ORDER BY 
    ed.website_event_id
"""
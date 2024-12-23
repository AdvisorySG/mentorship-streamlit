import pandas as pd
import streamlit as st
from auxiliary_functions import extract_query_params, process_query_params

st.title("Clicks & Impressions Dashboard")

# Initialize connection
conn = st.connection("mysql", type="sql")

df = conn.query("select * from website_event;")

df_processed = df.copy(deep=True)
#
df_processed["url"] = "/?" + df["url_query"].astype(str)
df_processed["query_params"] = df_processed["url"].apply(extract_query_params)
df_processed["parsed_params"] = df_processed["query_params"].apply(process_query_params)

# helper to extract industry
def extract_industry(params):
    industries = params.get("industries", [])
    if isinstance(industries, list) and industries:
        return industries[0]
    return None

df_processed["industries"] = df_processed["parsed_params"].apply(extract_industry)

metrics = []
for industry in df_processed["industries"].dropna().unique(): #remove the null
    industry_data = df_processed[df_processed["industries"] == industry]
    clicks = len(industry_data[industry_data["event_name"] == "Click"]) #calclate the number of clicks for each industry
    impressions = len(industry_data[industry_data["event_name"] == "Impression"]) # do the same for impressions

    metrics.append({
        "industry": industry,
        "Click": clicks,
        "Impression": impressions
    })

metrics_df = pd.DataFrame(metrics)

# get the top and bottom 5 industries
clicks_top = metrics_df.nlargest(5, "Click")[["industry", "Click"]]
clicks_bottom = metrics_df.nsmallest(5, "Click")[["industry", "Click"]]
impressions_top = metrics_df.nlargest(5, "Impression")[["industry", "Impression"]]
impressions_bottom = metrics_df.nsmallest(5, "Impression")[["industry", "Impression"]]

#display in table formmm
col1, col2 = st.columns(2)

with col1:
    st.subheader("Industry Clicks")
    st.markdown("**Top 5 Most Clicked**")
    st.dataframe(clicks_top)

    st.markdown("**Bottom 5 Least Clicked**")
    st.dataframe(clicks_bottom)

with col2:
    st.subheader("Industry Impressions")
    st.markdown("**Top 5 Most Impressions**")
    st.dataframe(impressions_top)

    st.markdown("**Bottom 5 Least Impressions**")
    st.dataframe(impressions_bottom)
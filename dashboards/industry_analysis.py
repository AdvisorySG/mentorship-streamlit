import streamlit as st
import pandas as pd
from utils import duckdb
import json
from collections import Counter
from urllib.parse import unquote
from datetime import timedelta

st.title("Industry Analysis Dashboard")

# Initialize connection.
cur = duckdb.get_dbcur()

# get data from duckdb mentor visits table and umamidb website event table
df = cur.sql("""
    SELECT mv.url_params, mv.visit_id, we.created_at
    FROM mentor_visits mv
    INNER JOIN umamidb.website_event we
    ON mv.visit_id = we.visit_id
    WHERE json_extract(url_params, '$.filters.industries') IS NOT NULL
""").df()


# customized function for getting industries from url params
def process_query_params(params):  # given the url params for 1 entry
    params_json = json.loads(params)
    industry_values = params_json["filters"]["industries"]["values"]
    industries = []
    for industry in industry_values:
        industries.append(industry)
    return industries


df["industries"] = df["url_params"].apply(process_query_params)

# group by visit_id and sort
df = df.sort_values(by=["visit_id", "created_at"])

# combine same timestamp rows into one step (by visit_id and created_at) then aggregate industries in list
grouped_df = df.groupby(["visit_id", "created_at"])["industries"].sum().reset_index()
# remove duplicates
grouped_df["industries"] = grouped_df["industries"].apply(
    lambda x: list(dict.fromkeys(x))
)


# function to count switches
def compute_switches(prev, curr):
    switches = []
    for p in prev:
        if p in curr:
            switches.append((p, p))  # stayed the same
        else:
            for c in curr:
                if c != p:
                    switches.append((p, c))  # switched to something else
    return switches


# function to emulate rolling window since pandas windowing only accepts numbers
def rolling_window_switches(grouped_df, window_minutes):
    all_switches = []
    window_delta = timedelta(minutes=window_minutes)

    for visit_id, group in grouped_df.groupby("visit_id"):
        times = group["created_at"].tolist()
        industries_lists = group["industries"].tolist()

        # sliding window [start_idx, end_idx]
        group_len = len(group)
        start_idx = 0
        end_idx = 0

        while start_idx < group_len:
            # end_idx go as far as possible within window
            while (
                end_idx + 1 < group_len
                and times[end_idx + 1] - times[start_idx] <= window_delta
            ):
                end_idx += 1

            # only compute switches if window size >= 2
            if end_idx > start_idx:
                prev_industries = industries_lists[start_idx]
                curr_industries = industries_lists[end_idx]
                switches = compute_switches(prev_industries, curr_industries)
                all_switches.extend(switches)

            # move start_idx forward
            start_idx += 1

    return all_switches


# store switches globally
all_switches = rolling_window_switches(grouped_df, window_minutes=2)

# count switches
switches_count = Counter(all_switches)

# convert to dataframe
switches_df = pd.DataFrame(
    [{"from": f, "to": t, "count": c} for (f, t), c in switches_count.items()]
).sort_values(by="count", ascending=False)

# remove url encoding
switches_df["from"] = switches_df["from"].apply(unquote)
switches_df["to"] = switches_df["to"].apply(unquote)

st.write(switches_df)

import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import timedelta
import seaborn as sns 

st.title("Average Screentime Dashboard")

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Get data
df = conn.query("SELECT * FROM website_event")

# Creating the df with [session_id, created_at_max, created_at_min, time_difference]
df1 = df[['session_id', 'created_at']]
df2 = df1.groupby(['session_id']).max()
df2 = df2.join(df1.groupby(['session_id']).min(), lsuffix='_max',rsuffix='_min')
df2['time_difference'] = df2['created_at_max'] - df2['created_at_min']
df2.drop(df2[df2['time_difference'] == timedelta(0)].index, inplace=True) # Remove the rows where the time_difference is 0 days


# Formatting & convert from timedelta to float seconds because Seaborn cannot handle timedelta
df2.drop(columns=["created_at_max", "created_at_min"], inplace=True)
df2.reset_index(drop=True, inplace=True)
def convert_to_seconds(timedelta):
    return float(timedelta.total_seconds())
df2['time_difference'] = df2['time_difference'].apply(convert_to_seconds)

# Only plot the 25th to 75th percentile
lower_limit, upper_limit = df2['time_difference'].quantile(.25), df2['time_difference'].quantile(.75)
plot = sns.histplot(data=df2[(df2['time_difference'] > lower_limit) & (df2['time_difference'] < upper_limit)]['time_difference'], bins=30, kde=True)
st.pyplot(plot.get_figure())

# Avg time for the 25th to 75th percentile
avg_time = df2[(df2['time_difference'] > lower_limit) & (df2['time_difference'] < upper_limit)]['time_difference'].mean()
avg_time = str(timedelta(seconds=avg_time))

# Display the result
st.metric(label="Average Screentime", value=avg_time)
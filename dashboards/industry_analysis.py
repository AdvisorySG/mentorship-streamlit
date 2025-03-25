import streamlit as st
from auxiliary_functions import extract_query_params
import pandas as pd
from collections import defaultdict

st.title("Industry Analysis Dashboard")

# Initialize connection.
conn = st.connection("mysql", type="sql")

# Get data
df = conn.query("select session_id, url_query, referrer_query, created_at from website_event;")
df["created_at"] = pd.to_datetime(df["created_at"]) # So we can sort by create_at
df = df.sort_values("created_at")

# Customized functions for getting industries from both url_query and referrer_query
def process_query_params(params):
    industries = []
    for key, value in params.items():
        if "filters" in key and "[field]" in key and value[0] == "industries": # filters[X][field] : ["industries"]
            industry_key = key.replace("[field]", "[values]")  # filters[X][field] -> filters[X][values]
            for key in params:
                if industry_key in key:  # Check if the key contains "filters[X][values]"
                    industries.extend(params[key])  # Add all values to the industries list without getting nested list like append    
    return(industries)  
    
def parsing_urls(df):
    df = df.copy(deep=True)
    df["current"] = "/?" + df["url_query"].astype(str) # Make url_query in a way that can be used with extract_query_params
    df["previous"] = "/?" + df["referrer_query"].astype(str)
    df["current_query_params"] = df["current"].apply(extract_query_params)  
    df["previous_query_params"] = df["previous"].apply(extract_query_params)
    df["current_industries"] = df["current_query_params"].apply(process_query_params)
    df["previous_industries"] = df["previous_query_params"].apply(process_query_params)
    
    # Drop rows where either 'current_industries' and 'previous_industries' are 
    df = df[(df['current_industries'].map(len) > 0) & (df['previous_industries'].map(len) > 0)] # an empty list 
    df = df[df['current_industries'].ne(df['previous_industries'])] # equal
    return df.dropna(subset=['current_industries', 'previous_industries'], how="any", axis=0) # NaN 

# Function to detect and return added and removed industries per row
def detect_switches(row):
    # Convert the lists to set because lists do not have set operations 
    current_set = set(row['current_industries'])
    previous_set = set(row['previous_industries'])
    
    # Find the industries that were removed and added
    removed = previous_set - current_set
    added = current_set - previous_set
    return removed, added

# Create new dataframe using the aggregating timing window per session
def process_group(group, time_window):
    """Analyze industry switches within a session using a rolling time window
    lets say our time window is 10mins

    then he goes

    start ABCD
    2 mins ABE
    9 mins ACF
    11mins ANM
    13mins ABCD

    so ill consider these pairs
    start 9mins
    2mins 11mins
    9mins 13mins
    11mins 13mins
    """
    session_df = pd.DataFrame(columns=['start_created_at', 'start_industries', 'end_created_at', 'end_industries', 'removed', 'added'])
    
    # For every timestamp, we iterate through all timestamps from the timestamp and break on the first hit we get
    for i in range(len(group)):
        start_created_at = group['created_at'].iloc[i] 

        for j in range(len(group)-1, i, -1):
            end_created_at = group['created_at'].iloc[j] 
               
            # Get the industries, the switches, and append them to the new dataframe
            if end_created_at - start_created_at < time_window:
                start_industries = group['current_industries'].iloc[i]
                end_industries = group['current_industries'].iloc[j]
                added = set(end_industries) - set(start_industries)
                removed = set(start_industries) - set(end_industries)
                session_df.loc[len(session_df)] = [start_created_at, start_industries, end_created_at, end_industries, removed, added]
                break
                 
    return session_df    


# Count the relevant switches in the aggregated dataframe
def count_industry_switches(df):
    switch_counts = defaultdict(int)  # Dictionary to store switch counts, defaultdict automatically initializes missing keys with a default value, 0 for int

    for _, row in df.iterrows():
        removed = row["removed"]
        added = row["added"]

        # Create switch pairs and count them
        # It'll look like {("A", "D"): 3, ("A", "E"): 2, ("C", "D"): 1, ("C", "E"): 4}
        for r in removed:
            for a in added:
                switch_counts[(r, a)] += 1  # Count each removed r -> added a

        # Count removed r -> null if added is empty
        if not added:  
            for r in removed:
                switch_counts[(r, None)] += 1  

        # Count null -> added a if removed is empty
        if not removed:  
            for a in added:
                switch_counts[(None, a)] += 1  
            
    # Convert to DataFrame 
    switch_df = pd.DataFrame(
        [(k[0], k[1], v) for k, v in switch_counts.items()],
        columns=["From", "To", "Count"]
    )
    
    return switch_df

# Function to display results in streamlit
def display_industry_switch_analysis(df):
    st.header("Industry Switch Analysis")
    overall_df = pd.DataFrame(columns=['start_created_at', 'start_industries', 'end_created_at', 'end_industries', 'removed', 'added'])
    
    # Iterate over the groups by session_id
    for session_id, group in df.groupby("session_id"):
    
        #axis=1 for row-wise application and expand [removed, added] into individual columns rather than a single series
        #group[['removed_industries', 'added_industries']] = group.apply(detect_switches, axis=1, result_type="expand") 
        
        # New df per session that follows timing_window aggregation rule, appends the session_df to the overall_df to be processed to get the switches
        session_df = process_group(group, pd.Timedelta(minutes=10))
        
        # Before concatenating, remove empty or all-NA columns from session_df to fix the error [The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.]
        session_df = session_df.dropna(axis=1, how='all')  
        overall_df = overall_df.dropna(axis=1, how='all')
        
        overall_df = pd.concat([overall_df, session_df], axis=0, ignore_index=True) # Concatenate the DataFrames
        
        #st.subheader(f"Session ID: {session_id}")  
        #st.write(session_df)
        #st.markdown("=" * 40) # Separator
        
        # st.write(group[['current_industries', 'previous_industries', 'removed_industries', 'added_industries']])
    
    st.subheader(f"Overall df")  
    st.write(overall_df)
    
    st.subheader(f"Switches df")  
    switch_df = count_industry_switches(overall_df)
    st.write(switch_df)
    
# Analyzing by session
df_processed = parsing_urls(df)
display_industry_switch_analysis(df_processed)




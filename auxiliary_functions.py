import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote
import streamlit as st
import plotly.express as px


def extract_query_params(url):
    url = unquote(url)  # make it human readable, not percentages
    query_params = parse_qs(urlparse(url).query)
    return query_params


def process_query_params(params):
    """
    Parameters:
    params -> {'size': ['n_20_n'], 'filters[0][field]': ['industries'], 'filters[0][values][0]': ['Information and Communications Technology'], 'filters[0][type]': ['all']}

    Returns:
    {
        "search_query": "search term",
        "filter_name": ["filter value 1", "filter value 2"]
    }

    Note:
    - The filter_name is the name of the filter, e.g. industries, school etc.
    - size and type are ignored
    """
    result = {}
    current_field = ""

    for key, value in params.items():
        if "filters" in key:
            parts = key.split("[")
            if len(parts) < 3:
                continue
            field_or_value = parts[2].strip("]")

            if field_or_value == "field":
                # if its a field then use it as a key
                current_field = value[0]
                result[current_field] = []
            elif field_or_value == "type":
                # there's a type of all in all queries, not sure what that is and whether its relevant
                continue
            else:
                # if its a value then add it to the list by using the last saved field
                result[current_field].extend(value)
        elif key == "q":
            result["search_query"] = value[0]

    result = dict(result)
    return result


def parsing_urls(df):
    df = df.copy(deep=True)
    df["url"] = "/?" + df["url_query"].astype(str)
    df["query_params"] = df["url"].apply(
        extract_query_params
    )  # gets all the query params and makes it a dictionary
    # optimized version of the code above
    df_processed = df.copy(deep=True)
    df_processed["query_params"] = df_processed["query_params"].apply(
        process_query_params
    )  # use only 1 for loop
    df_processed = pd.DataFrame(df_processed["query_params"].values.tolist())
    #     ['i', 'ind', 'cou', 'indust', 'o', 'sch', 'course_of']
    #     print(df_processed['indust'].value_counts())
    #     print(df_processed['ind'].value_counts())
    #     print(df_processed['i'].value_counts())
    #     print(df_processed['cou'].value_counts())
    #     print(df_processed['sch'].value_counts())
    #     print(df_processed['o'].value_counts())
    #     print(df_processed['course_of'].value_counts())
    #     print(df_processed['wave_id'].value_counts())# drop unused columns ['i', 'ind', 'cou', 'indust', 'o', 'sch', 'course_of']
    df_processed = df_processed.drop(
        [
            "c",
            "organisat",
            "course",
            "industrie",
            "wave_id",
            "i",
            "ind",
            "cou",
            "indust",
            "o",
            "sch",
            "course_of",
        ],
        axis=1,
        errors="ignore",
    )
    #     df_processed.info()
    return df_processed.dropna(how="all", axis=0)


def filter_dataframe(df):
    full_size = len(df)
    df = df.copy()
    c = st.container()
    with c:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            user_text_input = right.text_input(f"Enter sub filter string in {column}")
            if user_text_input:
                df = df[
                    df[column].astype(str).str.contains(user_text_input, case=False)
                ]
    st.write(
        "Percentage of data that has this combination: ", len(df) / full_size * 100, "%"
    )
    return df


def pie_chart(df):
    # df_10 = df.groupby(['name']).size().to_frame().sort_values([0], ascending = False).head(10).reset_index()
    fig_pie = px.pie(
        df.head(10), names="count", title="Top 10 most selected industries", hole=0.4
    )
    st.plotly_chart(fig_pie)


def bar_chart(df):
    return df.head(10)
    # df_10 = df.groupby(['name']).size().to_frame().sort_values([0], ascending = False).head(10).reset_index()
    # fig_bar = px.bar(df_10.value_counts(), x=df['Product Category'].value_counts().index, y=df['Industry'].value_counts().values,
    #                 labels={'x': 'Industry', 'y': 'Count'}, title='Top 10 most selected industries', color=df['name'].value_counts().index)
    # bar_chart_col.plotly_chart(fig_bar)

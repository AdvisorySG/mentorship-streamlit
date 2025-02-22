import streamlit as st
import duckdb
import seaborn as sns

from utils.duckdb import get_dbcur

def parse_url_query(query_list):
    # Adapted from process_query_params from auxiliary_functions.py
    # Functionally does the same but modified slightly due to different structure of arguments passed in
    # Also returns a json obj instead of py dict so that duckdb recognizes this structure
    import json
    result = {}
    current_field = ""

    for query in query_list:
        if "=" not in query:
            continue
        key, value = query.split("=")
        if "filters" in key:
            parts = key.split("[")
            if len(parts) < 3:
                continue
            field_or_value = parts[2].strip("]")

            if field_or_value == "field":
                # if its a field then use it as a key
                current_field = value
                result[current_field] = []
            elif field_or_value == "type":
                # there's a type of all in all queries, not sure what that is and whether its relevant
                continue
            else:
                # if its a value then add it to the list by using the last saved field
                result[current_field].append(value)
        elif key == "q":
            result["search_query"] = [value]
    return json.dumps(result)

def get_db(cur, columns):
    # Function reads the data from umami and cleans it to the required format
    # 1. Extract the necessary information and format the url to its parameters
    tmp_db = cur.sql("""
        USE umamidb;
        SELECT created_at,
            list_sort([param FOR param IN regexp_split_to_array(url_query, '&') IF param LIKE 'q%' OR param LIKE 'filters%']) AS url_params,
            list_sort([param FOR param IN regexp_split_to_array(referrer_query, '&') IF param LIKE 'q%' OR param LIKE 'filters%']) AS referrer_params,
            visit_id
        FROM website_event
        WHERE event_type = 1 -- clicks
            AND url_path LIKE '/mentors%'
            AND referrer_path LIKE '/mentors%'
            AND url_params <> referrer_params
        QUALIFY row_number() OVER (PARTITION BY url_params, referrer_params, visit_id) = 1
        ORDER BY created_at DESC;
        """).fetchdf()
    # 2. Convert the url parameters to json-like object
    tmp_db["url_params"] = tmp_db["url_params"].apply(
            parse_url_query
        )  # gets all the query params and makes it a dictionary
    # 2.1 Convert created_at from datetime to date so that DuckDB can recognize it
    tmp_db['created_at'] = tmp_db['created_at'].dt.date
    # 3. Prepare the SQL query statement to convert the json object into individual columns
    # Basically loop through the columns (above) and extracts out each part in the json obj as a new column
    sql_json_query = ", ".join([f"CAST(json_extract(url_params, '{col_name}') AS VARCHAR[]) AS {col_name}" for col_name in ["search_query"] + columns])
    # 4. Convert the json-like object to columns
    tmp_db = duckdb.query(f"SELECT CAST(created_at AS DATE) AS created_at, visit_id, {sql_json_query} FROM tmp_db").to_df()
    return tmp_db

columns = ["industries", "organisation", "course_of_study", "school"] # Can be obtained dynamically, but usually takes too long so...
cur = get_dbcur()
db = get_db(cur, columns)
st.dataframe(db)

# A series which we will use often to filter results
st.subheader("Getting the top industries")
top_industries = duckdb.query("""
                        SELECT industries, count(*) AS total_count
                        FROM db
                        WHERE industries IS NOT NULL
                            AND len(industries) < 2
                        GROUP BY industries
                        ORDER BY total_count DESC
                        LIMIT 10;""").to_df()
st.dataframe(top_industries)

# Query 1
st.subheader("Query 1: Frequency of single instance of industry selected, where the count > 5")
tmp_db = db.copy()
tmp_db = duckdb.query("""
                  SELECT CAST(industries AS VARCHAR) AS industries, 
                    COUNT(industries) AS count
                  FROM tmp_db 
                  WHERE industries IS NOT NULL
                    AND len(industries) < 2
                  GROUP BY industries
                  HAVING count > 5;""").to_df()
st.dataframe(tmp_db)
plot = sns.histplot(
    data=tmp_db,
    x='industries',
    y='count'
)
st.pyplot(plot.get_figure())

# Query 2
st.subheader("Query 2: Line graph trend of industry over time")
tmp_db = db.copy()
tmp_db = duckdb.query("""
                SELECT make_date(YEAR(created_at), MONTH(created_at), 1) AS created_at,
                    CAST(industries AS VARCHAR) AS industries, 
                    1 AS count
                FROM tmp_db 
                WHERE industries IS NOT NULL
                    AND len(industries) < 2;"""
                      ).to_df()
tmp_db = duckdb.query("""
                SELECT DISTINCT CAST(created_at AS VARCHAR) AS date, industries, SUM(count)
                OVER(PARTITION BY industries ORDER BY date) AS cumulative_count
                FROM tmp_db
                ORDER BY date ASC, industries ASC;"""
                      ).to_df()
st.dataframe(tmp_db)
plot.clear()
plot = sns.lineplot(
    data=tmp_db,
    x='date',
    y='cumulative_count',
    hue='industries',
    legend='brief',
)
plot.figure.set_figheight(20)
plot.figure.set_figwidth(25)
st.pyplot(plot.get_figure())
# Query 2.1
st.text("Query 2.1: Line graph for only top 10 industries")
tmp_db = duckdb.query("""
                    SELECT * 
                    FROM tmp_db 
                    WHERE industries IN (
                        SELECT industries FROM top_industries
                    )
                    ORDER BY date ASC, industries ASC;""").to_df()
st.dataframe(tmp_db)
plot.clear()
plot = sns.lineplot(
    data=tmp_db,
    x='date',
    y='cumulative_count',
    hue='industries',
    legend='brief',
)
st.pyplot(plot.get_figure())

# Query 3
st.subheader("Query 3: Histogram of industry searches per month")
tmp_db = db.copy()
tmp_db = duckdb.query("""
                SELECT make_date(YEAR(created_at), MONTH(created_at), 1) AS date,
                    CAST(industries AS VARCHAR) AS industries, count(*) AS clicks_per_month
                FROM tmp_db
                WHERE industries IN (
                    SELECT industries FROM top_industries
                )
                GROUP BY date, industries
                ORDER BY date ASC, industries ASC;"""
                ).to_df()
st.dataframe(tmp_db)
plot.clear()
plot = sns.barplot(
    data=tmp_db,
    x='date',
    y='clicks_per_month',
    hue='industries',
)
plot.figure.set_figwidth(15)
st.pyplot(plot.get_figure())
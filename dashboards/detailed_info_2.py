import streamlit as st

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
    # 3. Prepare the SQL query statement to convert the json object into individual columns
    # Basically loop through the columns (above) and extracts out each part in the json obj as a new column
    sql_json_query = ", ".join([f"CAST(json_extract(url_params, '{col_name}') AS VARCHAR[]) AS {col_name}" for col_name in ["search_query"] + columns])
    # 4. Convert the json-like object to columns
    import duckdb
    tmp_db = duckdb.query(f"SELECT visit_id, {sql_json_query} FROM tmp_db").to_df()
    return tmp_db

columns = ["industries", "organisation", "course_of_study", "school"] # Can be obtained dynamically, but usually takes too long so...
cur = get_dbcur()

# This is for the form (the one w the button)
with st.form("full query"):
    to_filter_columns = []
    filter_dict = {}
    with st.container():
        to_filter = st.multiselect("Filter dataframe on", columns)
    for filter in to_filter:
            left, right = st.columns((1, 20))
            left.write("↳")
            user_text_input = right.text_input(f"Enter sub filter string in {filter}")
            if user_text_input:
                filter_dict[filter] = user_text_input
    query = st.form_submit_button("Query")
    if query and filter_dict:
        db = get_db(cur, columns)
        full_size = len(db)
        import duckdb
        conn = duckdb.connect()
        cur2 = conn.cursor()
        cur2.execute("PREPARE query_db AS SELECT * FROM db WHERE CAST($filter AS VARCHAR) ILIKE CAST($query AS VARCHAR);")
        # db = cur2.execute("SELECT * FROM db WHERE CAST(search_query AS VARCHAR) ILIKE '%temasek%';").fetch_df()
        # print(db)
        for filter, query in filter_dict.items():
            if filter == "" or query == "": continue
            print(filter)
            print(query)
            query = "'%" + query + "%'"
            # db = cur2.execute(f"EXECUTE query_db(filter := '{filter}', query := '%{query}%');").fetch_df()
            db = cur2.execute(f"SELECT * FROM db WHERE CAST({filter} AS VARCHAR) ILIKE {query};").fetch_df()
        st.write(
            "Percentage of data that has this combination: ", len(db) / full_size * 100, "%"
        )
        st.dataframe(db)

# This is the original ui with the container (no button)
# with st.container():
#     to_filter_columns = []
#     filter_dict = {}
#     to_filter = st.multiselect("Filter dataframe on", columns)
#     for filter in to_filter:
#             left, right = st.columns((1, 20))
#             left.write("↳")
#             user_text_input = right.text_input(f"Enter sub filter string in {filter}")
#             if user_text_input:
#                 filter_dict[filter] = user_text_input
#     db = get_db(cur, columns)
#     full_size = len(db)
#     import duckdb
#     conn = duckdb.connect()
#     cur2 = conn.cursor()
#     cur2.execute("PREPARE query_db AS SELECT * FROM db WHERE CAST($filter AS VARCHAR) ILIKE CAST($query AS VARCHAR);")
#     # db = cur2.execute("SELECT * FROM db WHERE CAST(search_query AS VARCHAR) ILIKE '%temasek%';").fetch_df()
#     # print(db)
#     for filter, query in filter_dict.items():
#         if filter == "" or query == "": continue
#         print(filter)
#         print(query)
#         query = "'%" + query + "%'"
#         # db = cur2.execute(f"EXECUTE query_db(filter := '{filter}', query := '%{query}%');").fetch_df()
#         db = cur2.execute(f"SELECT * FROM db WHERE CAST({filter} AS VARCHAR) ILIKE {query};").fetch_df()
#     st.write(
#         "Percentage of data that has this combination: ", len(db) / full_size * 100, "%"
#     )
#     st.dataframe(db)
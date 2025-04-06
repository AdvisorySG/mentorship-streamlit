import duckdb
from duckdb.typing import VARCHAR
from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan
import streamlit as st

from collections import defaultdict
import html
import json
import re
import tempfile


@st.cache_resource(ttl=900, max_entries=1)
def get_dbcur() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    cur = con.cursor()

    # enable correct handling of timestamptz from MySQL
    cur.sql("SET TimeZone = 'UTC';")

    cur.sql("BEGIN TRANSACTION;")
    setup_elasticsearch(cur)
    setup_umamidb(cur)
    cur.sql("COMMIT;")

    # disable external file access once all required files are read
    # see https://duckdb.org/docs/operations_manual/securing_duckdb/overview
    cur.sql("SET enable_external_access = false;")

    cur.sql("SET lock_configuration = true;")
    return cur


ELASTICSEARCH_HOST = st.secrets.connections.elasticsearch.host
ELASTICSEARCH_PORT = st.secrets.connections.elasticsearch.port
ELASTICSEARCH_APIKEY = st.secrets.connections.elasticsearch.apikey
ELASTICSEARCH_INDEX = st.secrets.connections.elasticsearch.index


def setup_elasticsearch(cur: duckdb.DuckDBPyConnection):
    client = Elasticsearch(
        f"https://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}",
        api_key=ELASTICSEARCH_APIKEY,
    )
    with tempfile.NamedTemporaryFile("w", suffix=".ndjson", delete=False) as f:
        for result in scan(
            client,
            index=ELASTICSEARCH_INDEX,
            query={"query": {"match_all": {}}},
        ):
            f.write(json.dumps(result["_source"]) + "\n")
        f.flush()

        cur.sql(f"""CREATE TABLE elasticsearch AS
                SELECT *
                FROM read_ndjson('{f.name}');""")


UMAMIDB_HOST = st.secrets.connections.mysql.host
UMAMIDB_PORT = st.secrets.connections.mysql.port
UMAMIDB_DATABASE = st.secrets.connections.mysql.database
UMAMIDB_USERNAME = st.secrets.connections.mysql.username
UMAMIDB_PASSWORD = st.secrets.connections.mysql.password


def setup_umamidb(cur: duckdb.DuckDBPyConnection):
    cur.install_extension("mysql")
    cur.load_extension("mysql")
    cur.sql(f"""CREATE SECRET (
        TYPE MYSQL,
        HOST '{UMAMIDB_HOST}',
        PORT {UMAMIDB_PORT},
        DATABASE '{UMAMIDB_DATABASE}',
        USER '{UMAMIDB_USERNAME}',
        PASSWORD '{UMAMIDB_PASSWORD}'
    );
    """)
    cur.sql("ATTACH '' AS umamidb (TYPE MYSQL, READ_ONLY);")

    # UDF for creation of mentor_clicks table
    cur.create_function(
        "parse_url_query",
        lambda query_list: json.dumps(parse_url_query(query_list)),
        # parameters=duckdb.typing.DuckDBPyType(list[str]),
        return_type=VARCHAR,
    )
    columns = [
        "industries",
        "organisation",
        "course_of_study",
        "school",
    ]  # Can be obtained dynamically, but usually takes too long so...
    setup_mentors_clicks(cur, columns)


QUERY_INDEX_RE = r"\[(\d+|[a-zA-Z]+)\]"


def parse_url_query(query_list: list[str]) -> dict[str, list[str]]:
    """Sample Input:
      q=vincent&
      size=n_80_n&
      filters[0][field]=industries&
      filters[0][values][0]=Banking and Finance&
      filters[0][type]=all&
      filters[1][field]=organisation&
      filters[1][values][0]=Deutsche Bank&
      filters[1][type]=any
    Sample Output:
    {
        'search_query': ['vincent'].
        'industries': ['Banking and Finance'],
        'organization' : ['Deutsche Bank'],
    }"""

    result = defaultdict(list)

    filters = defaultdict(
        lambda: dict(
            field=None,
            values=defaultdict(dict),
        )
    )
    for query in query_list:
        if "=" not in query:
            continue

        key, value = html.unescape(query).split("=")
        if key == "q":
            result["search_query"] = [value]
        elif "filters" in key:
            matches = re.findall(QUERY_INDEX_RE, key)
            if len(matches) < 2:
                continue
            match matches[1]:
                case "field":
                    if not len(matches) == 2:
                        continue
                    i = matches[0]
                    filters[i]["field"] = value

                case "values":
                    if not len(matches) == 3:
                        continue
                    i, j = matches[0], matches[2]
                    filters[i]["values"][j] = value

    for filter in filters.values():
        field, values = filter["field"], filter["values"].values()
        result[field].extend(values)

    return result


def setup_mentors_clicks(cur, columns):
    # Function reads the data from umami and cleans it to the required format
    # 1. Extract the necessary information and format the url to its parameters
    # 2. Convert the url parameters into key-value pairs / json-like object
    cur.sql("""
        CREATE TABLE tmp
        AS
        SELECT created_at,
            parse_url_query(url_params) AS url_params,
            referrer_params,
            visit_id
        FROM
            (
            SELECT created_at,
                list_sort([param FOR param IN regexp_split_to_array(url_query, '&') IF param LIKE 'q%' OR param LIKE 'filters%']) AS url_params,
                list_sort([param FOR param IN regexp_split_to_array(referrer_query, '&') IF param LIKE 'q%' OR param LIKE 'filters%']) AS referrer_params,
                visit_id
            FROM umamidb.website_event
            WHERE event_type = 1 -- clicks
                AND url_path LIKE '/mentors%'
                AND referrer_path LIKE '/mentors%'
                AND url_params <> referrer_params
            QUALIFY row_number() OVER (PARTITION BY url_params, referrer_params, visit_id) = 1
            ORDER BY created_at DESC);
        """)

    # 3. Prepare the SQL query statement to convert the json object into individual columns
    # Basically loop through the columns and extracts out each part in the json obj as a new column
    sql_json_query = ", ".join(
        [
            f"CAST(json_extract(url_params, '{col_name}') AS VARCHAR[]) AS {col_name}"
            for col_name in ["search_query"] + columns
        ]
    )
    # 4. Convert the json-like object to columns
    # 5. Write into memory
    cur.sql(f"""
        CREATE TABLE mentors_clicks
        AS
        SELECT created_at,
            visit_id,
            {sql_json_query}
        FROM tmp;
        DROP TABLE tmp;
    """)

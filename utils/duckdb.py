import duckdb
from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan
import streamlit as st

import atexit
from collections import defaultdict
import html
import json
import os
import re
import tempfile
from typing import Any


_temp_files = []


def cleanup_temp_files():
    for f in _temp_files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except FileNotFoundError:
            pass
        except PermissionError:
            pass
        except OSError:
            pass


@st.cache_resource(ttl=900, max_entries=1)
def get_dbcur() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
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

    atexit.register(cleanup_temp_files)
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

    temp_file = tempfile.mktemp(suffix=".ndjson")
    _temp_files.append(temp_file)

    with open(temp_file, "w") as f:
        for result in scan(
            client,
            index=ELASTICSEARCH_INDEX,
            query={"query": {"match_all": {}}},
        ):
            f.write(json.dumps(result["_source"]) + "\n")

    cur.sql(f"""CREATE TABLE IF NOT EXISTS elasticsearch AS
            SELECT * FROM read_ndjson('{temp_file}');""")


UMAMIDB_HOST = st.secrets.connections.mysql.host
UMAMIDB_PORT = st.secrets.connections.mysql.port
UMAMIDB_DATABASE = st.secrets.connections.mysql.database
UMAMIDB_USERNAME = st.secrets.connections.mysql.username
UMAMIDB_PASSWORD = st.secrets.connections.mysql.password


def parse_mentor_visit_params(query_params: list[str]) -> dict[str, Any]:
    """
    Sample Query Parameters:
    q=vincent&
    size=n_80_n&
    filters[0][field]=industries&
    filters[0][values][0]=Banking and Finance&
    filters[0][type]=all&
    filters[1][field]=organisation&
    filters[1][values][0]=Deutsche Bank&
    filters[1][type]=any

    Sample Input:
    [
        "q=vincent",
        "size=n_80_n",
        "filters[0][field]=industries",
        "filters[0][values][0]=Banking and Finance",
        "filters[0][type]=all",
        "filters[1][field]=organisation",
        "filters[1][values][0]=Deutsche Bank",
        "filters[1][type]=any"
    ]

    Sample Output:
    {
        "q": "vincent",
        "size": "n_80_n",
        "filters": {
            "industries": {
                "type": "all",
                "values": ["Banking and Finance"]
            },
            "organization": {
                "type": "any",
                "values": ["Deutsche Bank"]
            }
        }
    }
    """

    QUERY_INDEX_RE = r"\[(\d+|[a-zA-Z]+)\]"

    result = {}
    filters = defaultdict(
        lambda: dict(
            field=None,
            type=None,
            values=defaultdict(dict),
        )
    )
    for query in query_params:
        if "=" not in query:
            continue

        key, value = html.unescape(query).split("=")
        if key == "q" or key == "size":
            result[key] = value
        elif "filters" in key:
            matches = re.findall(QUERY_INDEX_RE, key)
            if len(matches) < 2:
                continue

            i = matches[0]
            key = matches[1]
            match key:
                case "field" | "type":
                    if not len(matches) == 2:
                        continue
                    filters[i][key] = value

                case "values":
                    if not len(matches) == 3:
                        continue
                    j = matches[2]
                    filters[i][key][j] = value

    if len(filters) > 0:
        result["filters"] = {}
        for filter in filters.values():
            field, type = filter["field"], filter["type"]
            values = list(filter["values"].values())
            result["filters"][field] = {"type": type, "values": values}

    return result


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

    cur.create_function(
        "parse_mentor_visit_params",
        lambda query_params: json.dumps(parse_mentor_visit_params(query_params)),
        [list[str]],
        str,
    )
    cur.sql("""
        CREATE TABLE mentor_visits AS
        SELECT
            event_id,
            json(parse_mentor_visit_params(url_params)) AS url_params,
            json(parse_mentor_visit_params(referrer_params)) AS referrer_params,
            visit_id
        FROM (
            SELECT
                event_id,
                list_sort([
                    param FOR param IN regexp_split_to_array(url_query, '&')
                    IF param LIKE 'q%' OR param LIKE 'filters%'
                ]) AS url_params,
                list_sort([
                    param FOR param IN regexp_split_to_array(referrer_query, '&')
                    IF param LIKE 'q%' OR param LIKE 'filters%'
                ]) AS referrer_params,
                visit_id
            FROM umamidb.website_event
            WHERE
                event_type = 1 -- clicks
                AND url_path LIKE '/mentors%'
                AND referrer_path LIKE '/mentors%'
                AND url_params <> referrer_params
            QUALIFY row_number()
            OVER (PARTITION BY url_params, referrer_params, visit_id) = 1
            ORDER BY created_at ASC
        );
    """)

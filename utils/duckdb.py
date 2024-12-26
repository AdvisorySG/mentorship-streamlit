import duckdb
from elasticsearch.client import Elasticsearch
from elasticsearch.helpers import scan
import streamlit as st

import json
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

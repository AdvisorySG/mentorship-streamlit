import streamlit as st
import duckdb
import seaborn as sns
from utils.duckdb import get_dbcur, get_db

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
                    SELECT date, tmp_db.industries, cumulative_count
                    FROM tmp_db 
                    JOIN top_industries
                    ON tmp_db.industries = top_industries.industries
                    ORDER BY date ASC, tmp_db.industries ASC;""").to_df()
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
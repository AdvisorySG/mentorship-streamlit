import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Home Dashboard")
st.subheader("Demo Dashboard for Streamlit App")


# Initialize connection.
conn = st.connection("mysql", type="sql")

# Perform query.
# event_data, report, session, session_data, team, team_user, user, website, website_event
# df = conn.query('SELECT COUNT(session_id) from website_event;', ttl=600)
# st.dataframe(df)

# df = pd.DataFrame({
# 'Product Category': ['Electronics', 'Clothing', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors',
# 'Electronics', 'Clothing', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors',
# 'Clothing', 'Clothing', 'Clothing', 'Electronics'],
# 'Product Name': ['Smartwatch X1', 'Classic Denim Jacket', 'Stainless Steel Blender', 'Luxury Perfume Set', 'Camping Tent 4-person',
# 'Wireless Headphones', 'Casual T-shirt', 'Coffee Maker', 'Anti-aging Cream', 'Hiking Backpack',
# 'Running Shoes', 'Summer Dress', 'Hoodie Jacket', 'Smartphone X2'],
# 'Price': [129.99, 49.95, 79.99, 89.50, 149.95, 79.99, 19.99, 54.50, 39.95, 89.99, 69.99, 39.95, 59.99, 299.99],
# 'In Stock': np.random.choice([True, False], size=14)
# })

# metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

# metrics_col1.metric('Total Products', len(df))
# avg_price = df['Price'].mean()
# metrics_col2.metric('Average Price', f'${avg_price:.2f}')
# in_stock = df['In Stock'].mean()
# metrics_col3.metric('In Stock Percentage', f'{in_stock * 100:.2f}%')

# pie_chart_col, bar_chart_col = st.columns(2)

# Pie Chart: In Stock vs Out of Stock
# fig_pie = px.pie(df, names='In Stock', title='Product Availability', hole=0.4)
# pie_chart_col.plotly_chart(fig_pie)

# # Bar Chart: Product Categories
# fig_bar = px.bar(df['Product Category'].value_counts(), x=df['Product Category'].value_counts().index, y=df['Product Category'].value_counts().values,
# labels={'x': 'Product Category', 'y': 'Count'}, title='Product Categories', color=df['Product Category'].value_counts().index)
# bar_chart_col.plotly_chart(fig_bar)

# main juicy stuff
from auxiliary_functions import parsing_urls, pie_chart, bar_chart

# st.write(conn.query('SHOW TABLES;'))
df = conn.query("select * from website_event;")

# metric cards
col1, col2, col3 = st.columns(3)
# count of site visitors
import datetime

with col1:
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=24)
    df_filtered = df[(start_time < df["created_at"]) & (df["created_at"] < end_time)]
    st.metric(
        label="Number of unique visitors",
        value=f'{df.nunique()["session_id"]}',
        delta=f'{df_filtered.nunique()["session_id"]} in the last 24h',
    )

with col2:
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=28)
    df_filtered = df[(start_time < df["created_at"]) & (df["created_at"] < end_time)]
    parsed_df = parsing_urls(df)
    parsed_df_filtered = parsing_urls(df_filtered)
    mode = parsed_df["industries"].mode().iloc[0][0]
    value_counts = parsed_df_filtered["industries"].value_counts()
    value_df = pd.DataFrame(
        {"industries": value_counts.index, "count": value_counts.values}
    )
    st.metric(
        label="Most popular filter in the past month",
        value=f"{mode}",
        delta=f"{value_counts.iloc[0]} in the past month",
    )

with col3:
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=28)
    y_values = []
    x_values = []
    for x in range(6):
        x_values.append(end_time)
        df_filtered = df[
            (start_time < df["created_at"]) & (df["created_at"] < end_time)
        ]
        parsed_df_filtered = parsing_urls(df_filtered)
        y_values.append(parsed_df_filtered["industries"].value_counts().iloc[0])
        end_time = start_time
        start_time = end_time - datetime.timedelta(days=28)
    df1 = pd.DataFrame({"date": x_values, "count": y_values})
    fig_line = px.line(
        df1, x="date", y="count", title="frequency of the most popular search filter"
    )
    col3.plotly_chart(fig_line)


# user select graph to be made
st.subheader("Select a graph to represent the data!")


chart_options = ["Pie chart", "Bar chart"]
chart_type = st.multiselect("Select the type of chart:", chart_options)

if chart_type == "Pie chart":
    st.dataframe(pie_chart(df))

else:
    st.dataframe(bar_chart(df))

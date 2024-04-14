import streamlit as st
from st_pages import Page, show_pages, add_page_title
# https://blog.streamlit.io/crafting-a-dashboard-app-in-python-using-streamlit/ a good reference to dashboards in Streamlit

st.set_page_config(page_title="Streamlit Dashboard", page_icon="📈", layout="wide")

show_pages(
    [
        Page("streamlit-app.py", "Home", "🏠"),
        Page("pages/application.py", "Application Analysis", "📄"),
        Page("pages/traffic.py", "Traffic Analysis", "🌐"),
    ]
)

# Home Page Dashboard Starts
import pandas as pd
import plotly.express as px
import numpy as np

st.title('Home Dashboard')
st.subheader("Demo Dashboard for Streamlit App")


# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query.
# event_data, report, session, session_data, team, team_user, user, website, website_event
# df = conn.query('SELECT * from website_event;', ttl=600)
# st.dataframe(df)

df = pd.DataFrame({
    'Product Category': ['Electronics', 'Clothing', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors',
                         'Electronics', 'Clothing', 'Home & Kitchen', 'Beauty & Personal Care', 'Sports & Outdoors',
                         'Clothing', 'Clothing', 'Clothing', 'Electronics'],
    'Product Name': ['Smartwatch X1', 'Classic Denim Jacket', 'Stainless Steel Blender', 'Luxury Perfume Set', 'Camping Tent 4-person',
                     'Wireless Headphones', 'Casual T-shirt', 'Coffee Maker', 'Anti-aging Cream', 'Hiking Backpack',
                     'Running Shoes', 'Summer Dress', 'Hoodie Jacket', 'Smartphone X2'],
    'Price': [129.99, 49.95, 79.99, 89.50, 149.95, 79.99, 19.99, 54.50, 39.95, 89.99, 69.99, 39.95, 59.99, 299.99],
    'In Stock': np.random.choice([True, False], size=14)
})

metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

metrics_col1.metric('Total Products', len(df))
avg_price = df['Price'].mean()
metrics_col2.metric('Average Price', f'${avg_price:.2f}')
in_stock = df['In Stock'].mean()
metrics_col3.metric('In Stock Percentage', f'{in_stock * 100:.2f}%')

pie_chart_col, bar_chart_col = st.columns(2)

# Pie Chart: In Stock vs Out of Stock
fig_pie = px.pie(df, names='In Stock', title='Product Availability', hole=0.4)
pie_chart_col.plotly_chart(fig_pie)

# Bar Chart: Product Categories
fig_bar = px.bar(df['Product Category'].value_counts(), x=df['Product Category'].value_counts().index, y=df['Product Category'].value_counts().values,
                 labels={'x': 'Product Category', 'y': 'Count'}, title='Product Categories', color=df['Product Category'].value_counts().index)
bar_chart_col.plotly_chart(fig_bar)
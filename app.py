import streamlit as st
import pandas as pd
import plotly.express as px

# Set up page config
st.set_page_config(page_title="Sales & Revenue Dashboard", layout="wide")

# App Header
st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("Analyze monthly performance KPIs, dynamic trends, and product rankings.")

# Load Data function
@st.cache_data
def load_data():
    try:
        # Tries loading custom data, falls back to generated mock data
        df = pd.read_csv("sales_data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error("Missing 'sales_data.csv'. Please make sure the data file is placed in the same directory.")
        return None

df = load_data()

if df is not None:
    # --- Sidebar Filtering System ---
    st.sidebar.header("🎛️ Filter Controls")
    
    # Date Range Filter
    min_date = df['Date'].min().to_pydatetime()
    max_date = df['Date'].max().to_pydatetime()
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    # Multiselect Filters
    selected_products = st.sidebar.multiselect("Select Products", options=df['Product'].unique(), default=df['Product'].unique())
    selected_regions = st.sidebar.multiselect("Select Regions", options=df['Region'].unique(), default=df['Region'].unique())
    
    # Apply Filtering
    filtered_df = df[
        (df['Date'] >= pd.to_datetime(start_date)) & 
        (df['Date'] <= pd.to_datetime(end_date)) & 
        (df['Product'].isin(selected_products)) & 
        (df['Region'].isin(selected_regions))
    ]
    
    # --- 1. Metric Callout Cards ---
    st.markdown("### 🔑 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = filtered_df['Total_Sales'].sum()
    total_units = filtered_df['Units_Sold'].sum()
    total_profit = filtered_df['Profit'].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    
    col1.metric("Total Revenue", f"${total_sales:,.2f}")
    col2.metric("Units Sold", f"{total_units:,}")
    col3.metric("Net Profit", f"${total_profit:,.2f}")
    col4.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    st.markdown("---")
    
    # --- 2. Interactive Charts ---
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.markdown("#### 📈 Revenue Trend Over Time")
        # Aggregate monthly/daily trend depending on size
        trend_df = filtered_df.groupby(df['Date'].dt.to_period('M')).agg({'Total_Sales': 'sum'}).reset_index()
        trend_df['Date'] = trend_df['Date'].dt.to_timestamp()
        
        fig_trend = px.line(trend_df, x='Date', y='Total_Sales', 
                            labels={'Total_Sales': 'Revenue ($)', 'Date': 'Timeline'},
                            template='plotly_white', markers=True)
        fig_trend.update_traces(line_color='#1f77b4', line_width=3)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with right_col:
        st.markdown("#### 🏆 Top Performing Products by Revenue")
        product_df = filtered_df.groupby('Product').agg({'Total_Sales': 'sum'}).reset_index().sort_values(by='Total_Sales', ascending=True)
        
        fig_prod = px.bar(product_df, x='Total_Sales', y='Product', orientation='h',
                          labels={'Total_Sales': 'Total Sales ($)', 'Product': 'Product Variant'},
                          template='plotly_white')
        fig_prod.update_traces(marker_color='#2ca02c')
        st.plotly_chart(fig_prod, use_container_width=True)
        
    # --- Regional Analysis Section ---
    st.markdown("#### 🗺️ Regional Distribution Matrix")
    region_df = filtered_df.groupby('Region').agg({'Total_Sales': 'sum', 'Profit': 'sum'}).reset_index()
    
    fig_region = px.pie(region_df, values='Total_Sales', names='Region', 
                        hole=0.4, title="Revenue Share by Region",
                        color_discrete_sequence=px.colors.qualitative.Pastel)
    
    st.plotly_chart(fig_region, use_container_width=True)

    # --- Data Preview Grid ---
    st.markdown("#### 🗂️ Filtered Transactional Preview")
    st.dataframe(filtered_df[['Date', 'Product', 'Region', 'Units_Sold', 'Total_Sales', 'Profit']], use_container_width=True)
else:
    st.warning("Please upload a matching dataset structure to seed the visualization grid.")

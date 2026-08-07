import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

# Set page config for a premium and polished layout
st.set_page_config(
    page_title="Store Performance & Analytics Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 20px;
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 28px;
        color: #2b3e50;
        font-weight: 700;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Data Loading & Preparation
# -------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect("analytics.db")
        # Join orders and customers to fetch date, segment (customer_type), and revenue (order_amount)
        query = """
            SELECT 
                o.order_date AS date, 
                c.customer_type AS segment, 
                o.order_amount AS revenue 
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert date column to datetime
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        # Fallback to generating synthetic data if db is missing or table structure differs
        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        n_days = len(dates)
        
        # Simulate multiple orders per day
        repeated_dates = np.random.choice(dates, size=2000)
        segments = np.random.choice(['SMB', 'Startup', 'Enterprise'], size=2000, p=[0.4, 0.4, 0.2])
        
        revenue = []
        for s in segments:
            if s == 'Enterprise':
                revenue.append(np.random.normal(loc=1200, scale=150))
            elif s == 'SMB':
                revenue.append(np.random.normal(loc=400, scale=50))
            else:  # Startup
                revenue.append(np.random.normal(loc=200, scale=30))
                
        df = pd.DataFrame({
            "date": pd.to_datetime(repeated_dates),
            "segment": segments,
            "revenue": np.maximum(np.array(revenue), 10.0).round(2)
        })
        return df

df = load_data()

# -------------------------------------------------------------
# Filters (Sidebar)
# -------------------------------------------------------------
st.sidebar.header("Filters")

# Task 5: Implement Filter Reset
# Define default values for filters (Task 3: Define Meaningful Default Values)
default_date_range = (df["date"].min().date(), df["date"].max().date())
all_segments = df["segment"].unique().tolist()
default_segments = all_segments
default_rev_range = (int(df["revenue"].min()), int(df["revenue"].max()))

# Using Session State to programmatically manage defaults for reset
if "date_val" not in st.session_state:
    st.session_state.date_val = default_date_range
if "segment_val" not in st.session_state:
    st.session_state.segment_val = default_segments
if "rev_val" not in st.session_state:
    st.session_state.rev_val = default_rev_range

# Reset Filters logic
if st.sidebar.button("Reset Filters"):
    st.session_state.date_val = default_date_range
    st.session_state.segment_val = default_segments
    st.session_state.rev_val = default_rev_range
    st.rerun()

# Widget 1: Date range picker (Task 1 & 3)
date_range = st.sidebar.date_input(
    "Date Range",
    key="date_val"
)

# Widget 2: Multi-select for segments (Task 1 & 3)
selected_segments = st.sidebar.multiselect(
    "Segments", 
    options=all_segments, 
    key="segment_val"
)

# Widget 3: Revenue slider (Task 1 & 3)
min_rev, max_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=int(df["revenue"].min()),
    max_value=int(df["revenue"].max()),
    key="rev_val"
)

# -------------------------------------------------------------
# Data Filtering Logic (Task 2 & 4)
# -------------------------------------------------------------
# Prevent IndexError if date picker is in an intermediate state (only 1 date selected)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if len(date_range) > 0 else default_date_range[0]
    end_date = default_date_range[1]

# Apply filter chain (Task 2)
filtered_df = df[
    (df["date"] >= pd.Timestamp(start_date))
    & (df["date"] <= pd.Timestamp(end_date))
    & (df["segment"].isin(selected_segments))
    & (df["revenue"] >= min_rev)
    & (df["revenue"] <= max_rev)
]

# Task 4: Handle Empty Filter Combinations
if len(filtered_df) == 0:
    st.warning("No data matches the current filters. Try broadening your selection.")
    st.stop()

# -------------------------------------------------------------
# Dashboard Main Content (Aesthetics & Visualizations)
# -------------------------------------------------------------
st.title("🏪 Store Performance & Analytics Dashboard")
st.markdown("Analyze transactions, customer segment dynamics, and revenue growth in real time.")
st.markdown("---")

# KPI Summary Cards
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

total_rev_sum = filtered_df["revenue"].sum()
total_orders = len(filtered_df)
avg_order_val = filtered_df["revenue"].mean() if total_orders > 0 else 0.0
active_segs_count = filtered_df["segment"].nunique()

with kpi_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">${total_rev_sum:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Average Order Value</div>
            <div class="metric-value">${avg_order_val:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi_col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Segments</div>
            <div class="metric-value">{active_segs_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("### 📊 Performance Insights")
vis_col1, vis_col2 = st.columns(2)

with vis_col1:
    st.subheader("Daily Revenue Trend")
    trend_df = filtered_df.groupby("date")["revenue"].sum().reset_index()
    trend_df = trend_df.set_index("date")
    st.line_chart(trend_df, y="revenue", color="#1f77b4")

with vis_col2:
    st.subheader("Revenue by Segment")
    segment_df = filtered_df.groupby("segment")["revenue"].sum().reset_index()
    segment_df = segment_df.set_index("segment")
    st.bar_chart(segment_df, y="revenue", color="#ff7f0e")

# Task 2: Display Row Count and DataFrame Preview
st.markdown("### 📋 Transaction Logs")
st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
st.dataframe(filtered_df.head(20), width='stretch')

# Download Filtered Data Button
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Filtered Data (CSV)",
    data=csv_data,
    file_name="filtered_transactions_export.csv",
    mime="text/csv"
)

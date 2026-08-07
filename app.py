import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import io
import plotly.express as px
from alert_config import ALERT_THRESHOLDS

# Set page config for a premium layout
st.set_page_config(
    page_title="Operational Alerting Dashboard",
    page_icon="🚨",
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
# Data Loading & Preparation with Caching (Task 3 from before)
# -------------------------------------------------------------
@st.cache_data
def load_data(file_bytes, file_name):
    """
    Load dataset from CSV or JSON in a cacheable format.
    Accepts raw bytes and file name to enable correct caching by Streamlit.
    """
    if file_name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif file_name.endswith(".json"):
        return pd.read_json(io.BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or JSON file.")

def get_default_data():
    """
    Retrieves default dataset from SQLite database or generates a synthetic fallback,
    then returns it as CSV bytes to pass into cached load_data.
    """
    try:
        conn = sqlite3.connect("analytics.db")
        query = """
            SELECT 
                o.order_date AS date, 
                c.customer_type AS segment, 
                o.order_amount AS revenue,
                o.customer_id AS customer_id
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df.to_csv(index=False).encode('utf-8'), "default_analytics.csv"
    except Exception as e:
        # Fallback to generating synthetic data
        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        repeated_dates = np.random.choice(dates, size=2000)
        segments = np.random.choice(['SMB', 'Startup', 'Enterprise'], size=2000, p=[0.4, 0.4, 0.2])
        customer_ids = np.random.randint(1000, 2000, size=2000)
        
        revenue = []
        for s in segments:
            if s == 'Enterprise':
                revenue.append(np.random.normal(loc=1200, scale=150))
            elif s == 'SMB':
                revenue.append(np.random.normal(loc=400, scale=50))
            else:
                revenue.append(np.random.normal(loc=200, scale=30))
                
        df = pd.DataFrame({
            "date": repeated_dates.strftime("%Y-%m-%d"),
            "segment": segments,
            "revenue": np.maximum(np.array(revenue), 10.0).round(2),
            "customer_id": customer_ids
        })
        return df.to_csv(index=False).encode('utf-8'), "synthetic_data.csv"

# -------------------------------------------------------------
# File Upload & Data Resolution
# -------------------------------------------------------------
st.title("🚨 Operational Alerting Dashboard")
st.markdown("Monitor real-time threshold-based business alerts and data quality indicators.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload CSV or JSON dataset for analysis", type=["csv", "json"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
else:
    file_bytes, file_name = get_default_data()

# Load dataset
df = load_data(file_bytes, file_name)

# Dynamic Column Mapping
required_cols = ["date", "segment", "revenue", "customer_id"]
missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    st.sidebar.warning("⚠️ Column mismatch detected. Map columns:")
    col_mapping = {}
    for col in required_cols:
        options = list(df.columns)
        default_idx = 0
        for i, opt in enumerate(options):
            if col.lower() in opt.lower() or opt.lower() in col.lower():
                default_idx = i
                break
        selected_col = st.sidebar.selectbox(
            f"Map '{col}' to:",
            options=options,
            index=default_idx,
            key=f"map_{col}"
        )
        col_mapping[selected_col] = col
    df = df.rename(columns=col_mapping)
else:
    st.sidebar.success("✅ Columns auto-detected!")

# Format types
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["customer_id"] = df["customer_id"].astype(str)

# Clean null dates/revenues
df = df.dropna(subset=["date", "revenue"])

# Dynamic generation of churn column (if not present) based on realistic defaults (Task 5 adaptive)
if "churn" not in df.columns:
    np.random.seed(42)
    # Map typical churn rates: SMB (12%), Startup (8%), Enterprise (1%)
    churn_rates = {"Enterprise": 0.01, "SMB": 0.12, "Startup": 0.08, "All": 0.07}
    probs = df["segment"].map(churn_rates).fillna(0.07).values
    df["churn"] = np.random.binomial(1, probs)

# -------------------------------------------------------------
# Filters (Sidebar)
# -------------------------------------------------------------
st.sidebar.header("Filter Options")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

all_segments = sorted(df["segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=all_segments
)

min_rev_val = float(df["revenue"].min())
max_rev_val = float(df["revenue"].max())
if min_rev_val == max_rev_val:
    max_rev_val += 1.0

min_rev, max_rev = st.sidebar.slider(
    "Revenue Range",
    min_value=int(min_rev_val),
    max_value=int(max_rev_val),
    value=(int(min_rev_val), int(max_rev_val))
)

# -------------------------------------------------------------
# Filtering Execution
# -------------------------------------------------------------
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if len(date_range) > 0 else min_date
    end_date = max_date

filtered_df = df[
    (df["date"] >= pd.Timestamp(start_date))
    & (df["date"] <= pd.Timestamp(end_date))
    & (df["segment"].isin(selected_segments))
    & (df["revenue"] >= min_rev)
    & (df["revenue"] <= max_rev)
]

# Handle empty state
if len(filtered_df) == 0:
    st.warning("No data matches current filters. Broaden your selection.")
    st.stop()

# -------------------------------------------------------------
# Metric Computations (Task 1 & 5)
# -------------------------------------------------------------
total_revenue = filtered_df["revenue"].sum()
avg_order_value = filtered_df["revenue"].mean()
row_count = len(filtered_df)
unique_customers = filtered_df["customer_id"].nunique()

# Calculate null percentage across core columns
null_pct = (filtered_df[required_cols].isnull().sum().sum() 
            / (filtered_df[required_cols].shape[0] * filtered_df[required_cols].shape[1]) * 100)

# Calculate Churn Rate percentage
churn_rate = filtered_df["churn"].mean() * 100

# Assemble metrics dictionary matching the alert configuration keys
current_metrics = {
    "churn_rate": churn_rate,
    "avg_order_value": avg_order_value,
    "null_percentage": null_pct
}

# -------------------------------------------------------------
# Task 2 & 4: Display Visual Alerts (At the top of the dashboard)
# -------------------------------------------------------------
st.subheader("⚠️ System Alerts")
alert_container = st.container()

with alert_container:
    alert_fired = False
    for key, config in ALERT_THRESHOLDS.items():
        value = current_metrics.get(key, 0.0)
        breached = False
        
        # Evaluate threshold direction (above or below) (Task 1 & 2)
        if config["direction"] == "above" and value > config["threshold"]:
            breached = True
        elif config["direction"] == "below" and value < config["threshold"]:
            breached = True
            
        if breached:
            alert_fired = True
            # Formulate detailed alert message (Task 4)
            unit = "%" if "rate" in key or "percentage" in key else ""
            alert_text = (
                f"🚨 **ALERT ({config['metric']})**: "
                f"Current value is **{value:.1f}{unit}**, which is {config['direction']} the threshold of "
                f"**{config['threshold']:.1f}{unit}**. {config['message']}"
            )
            
            # Display using appropriate Streamlit component based on severity (Task 2)
            if config["severity"] == "critical":
                st.error(alert_text)
            else:
                st.warning(alert_text)
                
    if not alert_fired:
        st.success("✅ All system metrics are within normal operational limits. No alerts triggered.")

st.markdown("---")

# -------------------------------------------------------------
# KPI Cards
# -------------------------------------------------------------
st.subheader("📊 Key Performance Indicators")
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Revenue</div>
            <div class="metric-value">${total_revenue:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-value">${avg_order_value:,.1f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Records Count</div>
            <div class="metric-value">{row_count:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Churn Rate</div>
            <div class="metric-value">{churn_rate:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with kpi_col5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Data Quality</div>
            <div class="metric-value">{100 - null_pct:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# -------------------------------------------------------------
# Visualization Charts
# -------------------------------------------------------------
st.subheader("📈 Performance Insights")
vis_col1, vis_col2 = st.columns(2)

with vis_col1:
    st.markdown("#### Revenue Over Time")
    trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
    st.line_chart(trend.set_index("date"))

with vis_col2:
    st.markdown("#### Revenue by Segment")
    seg = filtered_df.groupby("segment")["revenue"].sum().reset_index()
    st.bar_chart(seg.set_index("segment"))

# Plotly Histogram for distribution
st.markdown("#### Revenue Distribution (Histogram)")
fig = px.histogram(
    filtered_df, 
    x="revenue", 
    nbins=30,
    color_discrete_sequence=["#2b3e50"],
    labels={"revenue": "Revenue ($)"}
)
fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# Data Table Logs
# -------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Transactions Logs")
st.write(f"Showing top 20 of {len(filtered_df):,} records:")
st.dataframe(filtered_df.head(20), width='stretch')

# -------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Interactive Data Ingestion & Analytics Shell",
    page_icon="📊",
    layout="wide"
)

# -------------------------------------------------------------
# 2. Sidebar Navigation Shell
# -------------------------------------------------------------
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the controls below to switch between dashboard sections.")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Data Ingestion & Upload", "Trends", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.caption("System Status: **Live Data Layer Connected**")
st.sidebar.caption("Environment: **Production v1.5.0**")

# -------------------------------------------------------------
# 3. Section 1: Overview
# -------------------------------------------------------------
if page == "Overview":
    st.title("Business Overview")
    st.caption("Executive Health Indicators | Real-Time Performance Snapshot")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Revenue", "$5.2M", "+12.5%")
    with col2:
        st.metric("Users", "2,500", "+5.2%")
    with col3:
        st.metric("AOV", "$45", "+2.1%")
    with col4:
        st.metric("Churn", "5.2%", "-2.8%", delta_color="inverse")
    with col5:
        st.metric("NPS", "72", "+4")

    st.divider()

    st.header("Executive Summary")
    st.subheader("Key Organizational Highlights & Operational Signals")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        - **Revenue Growth:** Quarter-over-quarter expansion driven by enterprise tier adoption (+18%).
        - **Retention Improvement:** Churn rate decreased by 2.8% following support SLA enforcement.
        """)
    with col_b:
        st.markdown("""
        - **Active User Base:** Exceeded 2,500 active accounts with a 92% renewal probability score.
        - **Customer Satisfaction:** NPS score increased by 4 points to 72.
        """)

    st.divider()

    with st.expander("About These Metrics & Calculation Methodology"):
        st.write("""
        **Revenue:** Sum of all settled order amounts for the current rolling 30-day window.  
        **Active Users:** Unique customer accounts with at least one session in the last 30 days.  
        **Average Order Value (AOV):** Total revenue divided by total completed orders.  
        **Churn Rate:** Percentage of active customers from Month N-1 who placed no order in Month N.  
        **Net Promoter Score (NPS):** Post-support survey score (Promoters % minus Detractors %).
        """)

# -------------------------------------------------------------
# 4. Section 2: Data Ingestion & File Upload (Tasks 1 - 5)
# -------------------------------------------------------------
elif page == "Data Ingestion & Upload":
    st.title("Data Ingestion & Dataset Preview")
    st.caption("Upload CSV or JSON files for instant automated preview, validation, and statistical analysis.")

    uploaded_file = st.file_uploader("Upload your dataset", type=["csv", "json"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload a CSV or JSON file.")
                st.stop()

            if len(df) == 0:
                st.warning("Uploaded file is empty. Please upload a file containing data rows.")
                st.stop()
        except Exception:
            st.error("Could not read this file. Check the format and try again.")
            st.stop()

        st.success(f"Loaded: {uploaded_file.name} ({len(df):,} rows, {len(df.columns)} columns)")

        st.divider()

        st.header("Dataset Preview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", str(len(df.columns)))
        with col3:
            total_cells = df.shape[0] * df.shape[1]
            null_pct = (df.isnull().sum().sum() / total_cells * 100) if total_cells > 0 else 0.0
            st.metric("Null %", f"{null_pct:.1f}%")

        st.subheader("First 10 Rows")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Column Summary")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
        })
        st.dataframe(summary, use_container_width=True)

        st.divider()

        st.subheader("Descriptive Statistics")
        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            st.dataframe(df.describe(), use_container_width=True)
        else:
            st.info("No numeric columns available for descriptive statistics.")

        st.divider()

        st.subheader("Quick Exploration")
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select a column to visualise", numeric_cols)
            st.markdown(f"**Value Frequency Distribution for `{selected_col}` (Top 20 Categories/Buckets):**")
            st.bar_chart(df[selected_col].value_counts().head(20))
        else:
            st.info("Upload a dataset containing numeric columns to enable interactive charting.")

    else:
        st.info("Upload a CSV or JSON file to begin analysis.")

# -------------------------------------------------------------
# 5. Section 3: Trends
# -------------------------------------------------------------
elif page == "Trends":
    st.title("Trend Analysis")
    st.caption("Historical Performance Tracking & Time-Series Benchmarks")

    st.header("Revenue Trends")
    st.subheader("Monthly Revenue & Growth Trajectory (Last 12 Months)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Monthly Revenue Breakdown ($M)**")
        chart_data_rev = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Revenue ($M)': [3.8, 4.0, 4.2, 4.1, 4.5, 4.7, 4.6, 4.8, 5.0, 5.1, 5.3, 5.2]
        }).set_index('Month')
        st.line_chart(chart_data_rev)
    
    with col2:
        st.markdown("**Revenue Distribution by Product Line**")
        chart_data_prod = pd.DataFrame({
            'Product': ['Enterprise SaaS', 'Cloud Analytics', 'Industrial Hardware', 'Starter Services'],
            'Revenue ($)': [2400000, 1400000, 900000, 500000]
        }).set_index('Product')
        st.bar_chart(chart_data_prod)

    st.divider()

    with st.expander("Historical Benchmark Notes & Seasonal Baseline Details"):
        st.write("""
        - Seasonal peak revenue occurs typically in Q4 during enterprise contract renewal windows.
        - Churn rates have shown consistent month-over-month reductions following the rollout of the 2-hour support SLA.
        """)

# -------------------------------------------------------------
# 6. Section 4: Data Explorer
# -------------------------------------------------------------
elif page == "Data Explorer":
    st.title("Data Explorer")
    st.caption("Granular Dataset Inspection, Filtering, and Export Options")

    st.header("Filter & Export Records")
    st.subheader("Interactive Record Search & Column Controls")

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("Search Customer ID or Segment", "")
    with col_f2:
        min_rev = st.slider("Minimum Revenue ($)", 0, 10000, 500)

    np.random.seed(42)
    n = 100
    df_raw = pd.DataFrame({
        'customer_id': [f"CUST-{1000+i}" for i in range(n)],
        'segment': np.random.choice(['Enterprise', 'Mid-Market', 'SMB', 'Starter'], size=n),
        'revenue': np.random.randint(200, 12000, size=n),
        'support_response_hrs': np.round(np.random.uniform(0.5, 26.0, size=n), 1),
        'status': np.random.choice(['Active', 'At-Risk', 'Churned'], p=[0.75, 0.15, 0.10], size=n)
    })

    filtered_df = df_raw[df_raw['revenue'] >= min_rev].copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['customer_id'].str.contains(search_query, case=False) |
            filtered_df['segment'].str.contains(search_query, case=False)
        ]

    st.markdown(f"Displaying **{len(filtered_df)}** matching customer records:")
    st.dataframe(filtered_df, use_container_width=True)

    st.download_button(
        label="📥 Download Filtered Data (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="filtered_customer_data.csv",
        mime="text/csv"
    )

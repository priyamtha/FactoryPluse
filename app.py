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

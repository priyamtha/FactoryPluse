import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import io
import plotly.express as px

# Set page config for a premium and polished layout
st.set_page_config(
    page_title="Reactive Analytics Dashboard",
    page_icon="📈",
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
# Task 3: Apply @st.cache_data to Data Loading
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

# -------------------------------------------------------------
# Default Data Loader (Querying analytics.db)
# -------------------------------------------------------------
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
# File Upload & Data Resolution (Task 5)
# -------------------------------------------------------------
st.title("📈 Reactive Analytics Dashboard")
st.markdown("Upload any transactional dataset (CSV/JSON) to visualize KPIs and charts instantly.")
st.markdown("---")

uploaded_file = st.file_uploader("Upload CSV or JSON dataset", type=["csv", "json"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
else:
    # Use default dataset
    file_bytes, file_name = get_default_data()

# Load data through the cached function
df = load_data(file_bytes, file_name)

# Ensure columns exist and map them dynamically if they are named differently (Task 5 Validation)
required_cols = ["date", "segment", "revenue", "customer_id"]
missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    st.sidebar.warning("⚠️ Column mismatch detected. Please map your columns below:")
    col_mapping = {}
    for col in required_cols:
        options = list(df.columns)
        # Try to find a good guess index
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
    st.sidebar.success("✅ Columns auto-detected successfully!")

# Ensure data types are parsed correctly
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
df["customer_id"] = df["customer_id"].astype(str)

# Clean out records with unparseable dates or revenues
df = df.dropna(subset=["date", "revenue"])

# -------------------------------------------------------------
# Reactive Filter Widgets (Sidebar)
# -------------------------------------------------------------
st.sidebar.header("Filter Options")

# Date range limits
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Segments selection
all_segments = sorted(df["segment"].dropna().unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Segments",
    options=all_segments,
    default=all_segments
)

# Revenue range limits
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
# Data Filtering Execution
# -------------------------------------------------------------
# Prevent IndexError on date picker intermediate states
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = date_range[0] if len(date_range) > 0 else min_date
    end_date = max_date

# Filter DataFrame reactively
filtered_df = df[
    (df["date"] >= pd.Timestamp(start_date))
    & (df["date"] <= pd.Timestamp(end_date))
    & (df["segment"].isin(selected_segments))
    & (df["revenue"] >= min_rev)
    & (df["revenue"] <= max_rev)
]

# -------------------------------------------------------------
# Task 4: Handle Empty Filtered Results
# -------------------------------------------------------------
if len(filtered_df) == 0:
    st.warning("No data matches current filters. Broaden your selection.")
    st.stop()

# -------------------------------------------------------------
# Task 1: Display Five Reactive KPI Metrics
# -------------------------------------------------------------
total_revenue = filtered_df["revenue"].sum()
avg_order = filtered_df["revenue"].mean()
row_count = len(filtered_df)
unique_customers = filtered_df["customer_id"].nunique()
null_pct = (filtered_df.isnull().sum().sum()
            / (filtered_df.shape[0] * filtered_df.shape[1]) * 100)

kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
with kpi_col1:
    st.metric("Revenue", f"${total_revenue:,.0f}")
with kpi_col2:
    st.metric("Avg Order", f"${avg_order:,.0f}")
with kpi_col3:
    st.metric("Records", f"{row_count:,}")
with kpi_col4:
    st.metric("Customers", f"{unique_customers:,}")
with kpi_col5:
    st.metric("Quality", f"{100 - null_pct:.1f}%")

st.markdown("---")

# -------------------------------------------------------------
# Task 2: Include Three Chart Types
# -------------------------------------------------------------
st.markdown("### 📊 Performance Charts")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Chart 1: Line chart (trend)
    st.subheader("Revenue Over Time")
    trend = filtered_df.groupby("date")["revenue"].sum().reset_index()
    st.line_chart(trend.set_index("date"))

with chart_col2:
    # Chart 2: Bar chart (comparison)
    st.subheader("Revenue by Segment")
    seg = filtered_df.groupby("segment")["revenue"].sum().reset_index()
    st.bar_chart(seg.set_index("segment"))

# Chart 3: Plotly histogram (distribution)
st.subheader("Revenue Distribution (Histogram)")
fig = px.histogram(
    filtered_df, 
    x="revenue", 
    nbins=30,
    color_discrete_sequence=["#1f77b4"],
    labels={"revenue": "Revenue ($)"}
)
fig.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# Transaction Logs Preview
# -------------------------------------------------------------
st.markdown("---")
st.subheader("📋 Transaction Logs Preview")
st.write(f"Showing top 20 of {len(filtered_df):,} filtered records:")
st.dataframe(filtered_df.head(20), width='stretch')

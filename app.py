import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

# Set page config for a premium layout
st.set_page_config(
    page_title="Segment Analysis Workflow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for KPI cards and layout
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
    .workflow-box {
        background-color: #f1f3f5;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2b3e50;
        margin-bottom: 15px;
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
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        # Fallback to generating synthetic data if db is missing or table structure differs
        np.random.seed(42)
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
        n_days = len(dates)
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
# Task 1 & 2 & 5: Session State Initialization & Documentation
# -------------------------------------------------------------
# Safe initialization with 'not in' checks to prevent overwriting values on reruns.
# Descriptive keys are used to ensure code clarity.

# "selected_segment" - stores the user's segment choice from Step 1
# so it survives reruns when the user interacts with Step 2 widgets.
if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"

# "workflow_step" - tracks which step the user has completed.
# Prevents Step 2 from displaying before Step 1 is confirmed.
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1

# "analysis_result" - caches the computation from Step 2 so
# it does not recompute when unrelated widgets are changed.
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# -------------------------------------------------------------
# Sidebar Navigation & Reset
# -------------------------------------------------------------
st.sidebar.header("Workflow Control")

# Task 4: Implement Session State Reset
if st.sidebar.button("Reset Workflow"):
    for key in ["selected_segment", "workflow_step", "analysis_result"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Display current workflow status in sidebar for context
st.sidebar.markdown("---")
st.sidebar.subheader("Workflow Status")
st.sidebar.markdown(f"**Current Step:** {st.session_state['workflow_step']}")
st.sidebar.markdown(f"**Selected Segment:** `{st.session_state['selected_segment']}`")
st.sidebar.markdown(f"**Cached Result:** `{'Yes' if st.session_state['analysis_result'] is not None else 'No'}`")

# -------------------------------------------------------------
# Main Application Layout
# -------------------------------------------------------------
st.title("⚡ Segment Analysis Workflow")
st.markdown("A guided multi-step analytics dashboard using persisted Streamlit session state.")
st.markdown("---")

# -------------------------------------------------------------
# Task 3: Step 1: Select Segment
# -------------------------------------------------------------
st.header("Step 1: Select Segment")

# Available segments to choose from (matches database unique values + Mid-Market for testing empty states)
segments_list = ["All", "Enterprise", "Mid-Market", "SMB", "Startup"]

# Selectbox retrieves the current selected segment as default index if it was already selected
default_idx = segments_list.index(st.session_state["selected_segment"]) if st.session_state["selected_segment"] in segments_list else 0

segment = st.selectbox("Segment", options=segments_list, index=default_idx)

if st.button("Confirm Segment"):
    st.session_state["selected_segment"] = segment
    st.session_state["workflow_step"] = 2
    # Invalidate cached results on segment change to force recomputation
    st.session_state["analysis_result"] = None
    st.rerun()

st.markdown("---")

# -------------------------------------------------------------
# Task 3: Step 2: Analysis (rendered only if Step 1 is complete)
# -------------------------------------------------------------
if st.session_state["workflow_step"] >= 2:
    st.header("Step 2: Analysis")
    chosen = st.session_state["selected_segment"]
    st.write("Analysing: " + chosen)
    
    # Task 5: Compute and cache results in "analysis_result" to prevent unnecessary recomputation
    if st.session_state["analysis_result"] is None:
        # Filter dataframe by chosen segment
        if chosen == "All":
            filtered_df = df
        else:
            filtered_df = df[df["segment"] == chosen]
            
        # Perform computation
        total_rev = filtered_df["revenue"].sum()
        total_orders = len(filtered_df)
        avg_rev = filtered_df["revenue"].mean() if total_orders > 0 else 0.0
        
        # Save metrics to analysis_result cache
        st.session_state["analysis_result"] = {
            "total_revenue": total_rev,
            "total_orders": total_orders,
            "avg_revenue": avg_rev,
            # We also store the filtered data for visualization
            "data": filtered_df.to_json(orient="split", date_format="iso")
        }
        st.info("🔄 Computed analytics and cached results in session state.")
    else:
        st.success("✅ Displaying cached analysis results (No recomputation).")
        
    # Read computed metrics from session state
    cached_metrics = st.session_state["analysis_result"]
    total_rev = cached_metrics["total_revenue"]
    total_orders = cached_metrics["total_orders"]
    avg_rev = cached_metrics["avg_revenue"]
    
    # Load data from json
    filtered_df = pd.read_json(cached_metrics["data"], orient="split")
    filtered_df["date"] = pd.to_datetime(filtered_df["date"])
    
    # Handle empty filtered dataframe (e.g. Mid-Market has 0 rows)
    if total_orders == 0:
        st.warning("⚠️ No data matches the selected segment. Try selecting another segment in Step 1.")
    else:
        # Render metrics layout
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Revenue</div>
                    <div class="metric-value">${total_rev:,.2f}</div>
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
                    <div class="metric-value">${avg_rev:,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        # Render a trend line chart
        st.subheader("Daily Revenue Trend for Segment")
        trend_df = filtered_df.groupby("date")["revenue"].sum().reset_index()
        trend_df = trend_df.set_index("date")
        st.line_chart(trend_df, y="revenue", color="#2b3e50")
        
        # Display sample transaction details
        st.subheader("Segment Data Log")
        st.write(f"Showing top 20 of {total_orders:,} records:")
        st.dataframe(filtered_df.head(20), width='stretch')

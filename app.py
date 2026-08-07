import streamlit as st
import pandas as pd
import numpy as np

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

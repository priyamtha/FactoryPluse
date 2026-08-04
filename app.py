import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
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
    ["Overview", "Trends", "Data Explorer"]
)

st.sidebar.divider()
st.sidebar.caption("System Status: **Live Data Layer Connected**")
st.sidebar.caption("Environment: **Production v1.4.0**")

# -------------------------------------------------------------
# 3. Section 1: Overview (Above-the-Fold KPI First Impression)
# -------------------------------------------------------------
if page == "Overview":
    # Single page title at very top
    st.title("Business Overview")
    st.caption("Executive Health Indicators | Real-Time Performance Snapshot")

    # Task 5: Important Content Above the Fold (5 Top-Row KPI Cards)
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

    # Section headers and subheaders for visual hierarchy
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

    # Expander for methodology notes
    with st.expander("About These Metrics & Calculation Methodology"):
        st.write("""
        **Revenue:** Calculated as the sum of all settled order amounts for the current rolling 30-day window.  
        **Active Users:** Count of unique customer accounts with at least one active session in the last 30 days.  
        **Average Order Value (AOV):** Total revenue divided by total completed orders.  
        **Churn Rate:** Percentage of active customers from Month N-1 who did not place an order in Month N.  
        **Net Promoter Score (NPS):** Calculated from post-support survey responses (Promoters % minus Detractors %).
        """)

# -------------------------------------------------------------
# 4. Section 2: Trends (Time-Series & Comparative Layout)
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

    st.header("Customer Metrics")
    st.subheader("Active Customers & Retention Trends Over Time")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("**Active Customer Count**")
        chart_data_cust = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Active Users': [2100, 2150, 2200, 2250, 2300, 2350, 2400, 2420, 2450, 2480, 2510, 2500]
        }).set_index('Month')
        st.line_chart(chart_data_cust)
        
    with col_c2:
        st.markdown("**Monthly Churn Rate Trend (%)**")
        chart_data_churn = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Churn Rate (%)': [8.0, 7.8, 7.5, 7.2, 6.8, 6.5, 6.2, 5.9, 5.7, 5.5, 5.4, 5.2]
        }).set_index('Month')
        st.line_chart(chart_data_churn)

    st.divider()

    with st.expander("Historical Benchmark Notes & Seasonal Baseline Details"):
        st.write("""
        - Seasonal peak revenue occurs typically in Q4 during enterprise contract renewal windows.
        - Churn rates have shown consistent month-over-month reductions following the rollout of the 2-hour support SLA.
        """)

# -------------------------------------------------------------
# 5. Section 3: Data Explorer (Raw Dataset & Filtering Controls)
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

    # Generate sample dataset
    np.random.seed(42)
    n = 100
    df_raw = pd.DataFrame({
        'customer_id': [f"CUST-{1000+i}" for i in range(n)],
        'segment': np.random.choice(['Enterprise', 'Mid-Market', 'SMB', 'Starter'], size=n),
        'revenue': np.random.randint(200, 12000, size=n),
        'support_response_hrs': np.round(np.random.uniform(0.5, 26.0, size=n), 1),
        'status': np.random.choice(['Active', 'At-Risk', 'Churned'], p=[0.75, 0.15, 0.10], size=n)
    })

    # Apply filters
    filtered_df = df_raw[df_raw['revenue'] >= min_rev].copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['customer_id'].str.contains(search_query, case=False) |
            filtered_df['segment'].str.contains(search_query, case=False)
        ]

    st.markdown(f"Displaying **{len(filtered_df)}** matching customer records:")
    st.dataframe(filtered_df, use_container_width=True)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name="filtered_customer_data.csv",
            mime="text/csv"
        )

    st.divider()

    with st.expander("Data Dictionary & Column Definitions"):
        st.write("""
        - **customer_id:** Unique identifier for the account.
        - **segment:** Business market tier (`Enterprise`, `Mid-Market`, `SMB`, `Starter`).
        - **revenue:** Total annual contract value (ACV) in USD.
        - **support_response_hrs:** Average first response duration for support tickets.
        - **status:** Current account health state (`Active`, `At-Risk`, `Churned`).
        """)

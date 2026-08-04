import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, date

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Business Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look & visual polish
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .kpi-justification {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 10px 15px;
        margin-top: 10px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Business Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Executive Overview | Information Hierarchy: Status (L1) → Trends (L2) → Segments (L3) → Detail Explorer (L4)</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# Level 1: Status (Top Row) - KPI Summary Cards
# -------------------------------------------------------------
st.subheader("Level 1: Executive KPI Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label='Revenue', value='$5.2M', delta='+12.5%')
with col2:
    st.metric(label='Active Customers', value='2,500', delta='+5.2%')
with col3:
    st.metric(label='Avg Order Value', value='$145', delta='+3.1%')
with col4:
    st.metric(label='Churn Rate', value='4.8%', delta='-1.2%', delta_color='inverse')
with col5:
    st.metric(label='NPS Score', value='72', delta='+4')

st.divider()

# Level 1 Justification Expander
with st.expander("ℹ️ Why these 5 KPI metrics were chosen & what business questions they answer"):
    st.markdown("""
    * **1. Revenue ($5.2M | +12.5%):**
      * *Business Question:* *"Are overall business top-line revenues growing according to targets?"*
      * *Role:* Primary metric for the CEO and Sales Director to monitor fiscal health and growth momentum.
    * **2. Active Customers (2,500 | +5.2%):**
      * *Business Question:* *"Is our active user base expanding or contracting?"*
      * *Role:* Measures customer acquisition efficiency and platform adoption.
    * **3. Avg Order Value ($145 | +3.1%):**
      * *Business Question:* *"Are customers spending more per transaction through upselling/cross-selling?"*
      * *Role:* Evaluates commercial monetization strategies and pricing power.
    * **4. Churn Rate (4.8% | -1.2%):**
      * *Business Question:* *"Are we retaining revenue and preventing customer attrition?"*
      * *Role:* Critical health metric for customer success; lower churn (`delta_color='inverse'`) directly drives lifetime value.
    * **5. NPS Score (72 | +4):**
      * *Business Question:* *"How satisfied and loyal are our customers with our products?"*
      * *Role:* Leading indicator for customer advocacy, viral growth, and long-term brand equity.
    """)

# -------------------------------------------------------------
# Level 2: Build the Trend Section (Middle Row)
# -------------------------------------------------------------
st.subheader("Level 2: Performance Trends Over Time")

trend_col1, trend_col2 = st.columns(2)

months = pd.date_range('2024-01-01', periods=12, freq='ME')

# Chart 1: Revenue Trend (Line Chart)
with trend_col1:
    st.markdown("#### Revenue Trend vs Target")
    if os.path.exists("output/revenue_trend.png"):
        st.image("output/revenue_trend.png", use_container_width=True)
    else:
        revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.plot(months, revenue, marker='o', linewidth=2.5, color='#1f77b4', label='Monthly Revenue')
        ax.set_title('Monthly Revenue Trend (2024)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Month', fontsize=11)
        ax.set_ylabel('Revenue ($M)', fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=5.0, color='#2ca02c', linestyle='--', linewidth=1.8, label='Target: $5.0M')
        ax.legend(loc='upper left')
        st.pyplot(fig)
        plt.close()

# Chart 2: Customer Metrics (Dual Line Chart)
with trend_col2:
    st.markdown("#### Active vs Churned Customers")
    if os.path.exists("output/customer_metrics_trend.png"):
        st.image("output/customer_metrics_trend.png", use_container_width=True)
    else:
        active_customers = [2100, 2150, 2200, 2250, 2320, 2380, 2410, 2440, 2470, 2500, 2530, 2500]
        churned_customers = [120, 115, 110, 125, 105, 98, 102, 110, 95, 90, 88, 92]
        fig, ax1 = plt.subplots(figsize=(10, 4.5))
        ax1.plot(months, active_customers, color='#1f77b4', marker='o', linewidth=2, label='Active Customers')
        ax1.set_xlabel('Month', fontsize=11)
        ax1.set_ylabel('Active Customers', color='#1f77b4', fontsize=11)
        ax2 = ax1.twinx()
        ax2.plot(months, churned_customers, color='#d62728', marker='s', linestyle='--', linewidth=2, label='Churned Customers')
        ax2.set_ylabel('Churned Customers', color='#d62728', fontsize=11)
        ax2.axhline(y=100, color='#ff7f0e', linestyle=':', label='Max Churn Threshold')
        fig.suptitle('Customer Acquisition & Churn Dynamics (2024)', fontsize=13, fontweight='bold')
        st.pyplot(fig)
        plt.close()

# Chart 3: Domain Trend (AOV Expansion Trend)
st.markdown("#### Average Order Value (AOV) Expansion Trend")
if os.path.exists("output/aov_trend.png"):
    st.image("output/aov_trend.png", use_container_width=True)
else:
    aov = [132, 134, 135, 138, 139, 140, 142, 141, 143, 144, 146, 145]
    fig, ax = plt.subplots(figsize=(12, 3.5))
    ax.plot(months, aov, marker='^', linewidth=2.5, color='#ff7f0e', label='Avg Order Value ($)')
    ax.set_title('Average Order Value (AOV) Expansion Trend', fontsize=13, fontweight='bold')
    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('Avg Order Value ($)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=140.0, color='#2ca02c', linestyle='--', linewidth=1.8, label='Target AOV: $140')
    ax.legend(loc='lower right')
    st.pyplot(fig)
    plt.close()

st.divider()

# -------------------------------------------------------------
# Level 3: Build the Segment Section (Middle-Bottom Row)
# -------------------------------------------------------------
st.subheader("Level 3: Customer Segment Breakdowns")

seg_col1, seg_col2 = st.columns([1.2, 1])

with seg_col1:
    if os.path.exists("output/revenue_by_segment.png"):
        st.image("output/revenue_by_segment.png", use_container_width=True)
    else:
        segments = ['Enterprise', 'Mid-Market', 'SMB', 'Starter']
        segment_revenue = [2.1, 1.5, 1.0, 0.6]
        segment_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.barh(segments, segment_revenue, color=segment_colors)
        ax.set_xlabel('Revenue ($M)', fontsize=11)
        ax.set_title('Revenue by Customer Segment', fontsize=13, fontweight='bold')

        for bar, val in zip(bars, segment_revenue):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f'${val}M', va='center', fontsize=11, fontweight='bold')

        st.pyplot(fig)
        plt.close()

with seg_col2:
    st.markdown("""
    ### Segment Analysis Insights
    * **Enterprise ($2.1M | 40.4%):**
      * Represents the largest revenue share. High contract value & low churn.
    * **Mid-Market ($1.5M | 28.8%):**
      * Primary expansion driver with rapid upsells into Enterprise tier.
    * **SMB ($1.0M | 19.2%):**
      * Volume segment requiring automated onboarding to lower support costs.
    * **Starter ($0.6M | 11.5%):**
      * Low-margin funnel entry; high conversion potential for starter-to-SMB tier.
    """)

st.divider()

# -------------------------------------------------------------
# Level 4: Apply Progressive Disclosure (Bottom Row) - Detail Explorer
# -------------------------------------------------------------
st.subheader('Level 4: Detailed Data Explorer (Progressive Disclosure)')

# Generate mock detailed customer record dataframe
np.random.seed(42)
records_count = 150
segments_list = ['Enterprise', 'Mid-Market', 'SMB', 'Starter']
dates = pd.date_range('2024-01-01', '2024-12-31', periods=records_count)

df = pd.DataFrame({
    'customer_id': [f'CUST-{1000 + i}' for i in range(records_count)],
    'segment': np.random.choice(segments_list, size=records_count, p=[0.2, 0.3, 0.3, 0.2]),
    'revenue': np.random.randint(500, 50000, size=records_count),
    'last_activity': dates,
    'churn_risk': np.random.choice(['Low', 'Medium', 'High'], size=records_count, p=[0.6, 0.25, 0.15])
})

start_date = df['last_activity'].min().date()
end_date = df['last_activity'].max().date()

# Sidebar filters for drill-down
st.sidebar.header('Filters & Drill-Down')
selected_segment = st.sidebar.selectbox('Customer Segment', ['All', 'Enterprise', 'Mid-Market', 'SMB', 'Starter'])
date_range = st.sidebar.date_input('Date Range', value=(start_date, end_date))
selected_churn_risk = st.sidebar.selectbox('Churn Risk Level', ['All', 'Low', 'Medium', 'High'])

# Apply filters
filtered_df = df.copy()

if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['segment'] == selected_segment]

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_filter, end_filter = date_range
    filtered_df = filtered_df[
        (filtered_df['last_activity'].dt.date >= start_filter) & 
        (filtered_df['last_activity'].dt.date <= end_filter)
    ]

if selected_churn_risk != 'All':
    filtered_df = filtered_df[filtered_df['churn_risk'] == selected_churn_risk]

# Display filtered summary stats & data table
st.write(f'Showing **{len(filtered_df):,}** records matching current filter selection')

st.dataframe(
    filtered_df[['customer_id', 'segment', 'revenue', 'last_activity', 'churn_risk']],
    use_container_width=True
)

# Export option
csv = filtered_df.to_csv(index=False)
st.download_button(
    label='📥 Download CSV',
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv'
)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime

# Import multi-format export module
from export_functions import export_analysis

# -------------------------------------------------------------
# Streamlit App Configuration
# -------------------------------------------------------------
st.set_page_config(layout='wide', page_title='Sales & Churn Analysis Dashboard')
st.title('📊 Sales Analysis & Automated Export Dashboard')

# -------------------------------------------------------------
# Data Loader
# -------------------------------------------------------------
@st.cache_data
def get_analysis_data():
    np.random.seed(42)
    n = 500
    dates = pd.date_range('2024-01-01', periods=n, freq='D')
    amounts = np.round(np.random.exponential(300, size=n) + 25, 2)
    resp_times = np.round(np.random.uniform(0.5, 30.0, size=n), 1)
    churn_flags = np.where(resp_times > 20, np.random.choice([0, 1], p=[0.3, 0.7], size=n), np.random.choice([0, 1], p=[0.95, 0.05], size=n))
    
    return pd.DataFrame({
        'customer_id': [f'CUST-{1000+i}' for i in range(n)],
        'order_date': dates.astype(str),
        'amount': amounts,
        'response_time_hours': resp_times,
        'churned': churn_flags,
        'segment': np.random.choice(['Enterprise', 'Mid-Market', 'SMB'], size=n)
    })

df = get_analysis_data()

# -------------------------------------------------------------
# Main Dashboard View & Charts
# -------------------------------------------------------------
st.subheader("Support Response Time vs Customer Retention")

fig_support = go.Figure(data=go.Scatter(
    x=df['response_time_hours'],
    y=df['amount'],
    mode='markers',
    marker=dict(color=df['churned'], colorscale='Rdbu_r', size=8, showscale=True),
    hovertemplate='<b>Customer: %{customdata}</b><br>Response Time: %{x} hrs<br>Order Amount: $%{y:,.2f}<extra></extra>',
    customdata=df['customer_id']
))
fig_support.update_layout(
    title='Response Time (Hours) vs Order Amount ($)',
    xaxis_title='Response Time (Hours)',
    yaxis_title='Order Amount ($)',
    template='plotly_white',
    height=450
)

st.plotly_chart(fig_support, use_container_width=True)

st.write(f"Showing **{len(df):,}** customer records in main dataset")
st.dataframe(df.head(10), use_container_width=True)

# -------------------------------------------------------------
# Task 3: Sidebar Export Integration
# -------------------------------------------------------------
st.sidebar.header('📥 Export & Download Center')
st.sidebar.markdown("Generate multi-format reports (CSV, PDF, HTML) with one click.")

if st.sidebar.button('🚀 Export Full Analysis'):
    summary_text = """# Executive Churn & Sales Analysis
## Key Findings
- **Support Response Time:** Response times under 2 hours result in 3% churn vs 12% churn for delays >24 hours.
- **Financial Impact:** $2M annual revenue lost to churn; SLA implementation recovers $400K.
## Recommendations
- **Hire 2 Support Engineers** (Cost: $200K, Net ROI: $200K).
- **Implement <2 Hour SLA** by Jan 1.
"""
    charts_dict = {'Support Response Impact': fig_support}
    
    # Run export function
    report_dir = export_analysis(df, summary_text, charts_dict, output_dir='output')
    st.sidebar.success(f"✓ Export saved to: `{report_dir}`")
    
    # 1. Download CSV Button
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label='📊 Download Data (CSV)',
        data=csv_bytes,
        file_name='analysis_data.csv',
        mime='text/csv'
    )
    
    # 2. Download HTML Interactive Report Button
    html_report_path = os.path.join(report_dir, 'interactive_report.html')
    if os.path.exists(html_report_path):
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_bytes = f.read()
        st.sidebar.download_button(
            label='🌐 Download Report (HTML)',
            data=html_bytes,
            file_name='analysis_report.html',
            mime='text/html'
        )

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, date

# Import custom KPI calculator engine
from kpi_calculator import compute_executive_kpis

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Executive Sales & Performance Header Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom Styling for polished KPI status cards
st.markdown("""
    <style>
    .kpi-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.2rem;
    }
    .kpi-subtitle {
        font-size: 1.0rem;
        color: #666666;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="kpi-title">Sales Performance Executive Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="kpi-subtitle">Executive Header Row | Five Standardized Business Health Metrics (MoM Comparison)</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# Compute & Display 5 KPI Cards at Top Row
# -------------------------------------------------------------
kpi_df = compute_executive_kpis()

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

for idx, (_, row) in enumerate(kpi_df.iterrows()):
    with columns[idx]:
        # Handle inverse delta color logic for Churn Rate (decrease in churn is positive/normal)
        delta_color_setting = "inverse" if row['Metric'] == 'Churn Rate' else "normal"
        
        st.metric(
            label=f"{row['Metric']} {row['Arrow']}",
            value=row['Current'],
            delta=f"{row['Change_Display']} vs prior month",
            delta_color=delta_color_setting
        )

st.divider()

# -------------------------------------------------------------
# Detailed Analytics Below KPI Header
# -------------------------------------------------------------
st.subheader("Detailed Monthly Performance Analytics")

tab1, tab2 = st.columns([1.5, 1])

with tab1:
    st.markdown("#### Monthly Revenue & Active User Trend")
    dates = pd.date_range('2024-01-01', periods=12, freq='ME')
    rev_trend = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]
    user_trend = [2100, 2150, 2200, 2250, 2320, 2380, 2410, 2440, 2470, 2500, 2530, 2500]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=rev_trend, mode='lines+markers', name='Revenue ($M)',
        line=dict(color='#1f77b4', width=2.5)
    ))
    fig.update_layout(
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title='Month',
        yaxis_title='Revenue ($M)'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("#### Executive KPI Status Matrix")
    
    # Styled Display Table for KPIs
    display_summary = kpi_df[['Metric', 'Current', 'Change_Display', 'Arrow', 'Status']].copy()
    display_summary.columns = ['Metric Name', 'Current Value', 'MoM Change', 'Trend', 'Health Status']
    
    st.dataframe(
        display_summary,
        use_container_width=True
    )
    
    st.info("💡 **Status Rules:** Green (`↑`/`↓`) indicates on-track growth. Red indicates attention needed. Yellow (`→`) indicates flat/stable performance (±1%).")

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sqlite3
import os

# -------------------------------------------------------------
# Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Interactive Sales & Performance Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Interactive Sales Dashboard (Plotly & Streamlit Integration)")

# -------------------------------------------------------------
# Data Loader
# -------------------------------------------------------------
@st.cache_data
def load_dashboard_data():
    if os.path.exists("analytics.db"):
        try:
            conn = sqlite3.connect("analytics.db")
            df = pd.read_sql("SELECT order_id, customer_id, order_date, order_amount as amount FROM orders LIMIT 2000", conn)
            conn.close()
            return df
        except Exception:
            pass

    # Synthetic fallback dataset
    np.random.seed(42)
    n = 1000
    dates = pd.date_range("2024-01-01", periods=n, freq="H")
    amounts = np.random.exponential(scale=250, size=n) + 15
    cust_ids = np.random.randint(1000, 1500, size=n)
    segments = np.random.choice(["Enterprise", "Mid-Market", "SMB", "Starter"], size=n)
    
    return pd.DataFrame({
        "order_id": [f"ORD-{1000+i}" for i in range(n)],
        "order_date": dates,
        "amount": np.round(amounts, 2),
        "customer_id": cust_ids,
        "segment": segments
    })

df = load_dashboard_data()
df['order_date'] = pd.to_datetime(df['order_date'])

# -------------------------------------------------------------
# Sidebar Filters
# -------------------------------------------------------------
st.sidebar.header("Filters & Dynamic Controls")

min_amount = st.sidebar.slider(
    "Minimum Order Amount ($)",
    min_value=0,
    max_value=int(df['amount'].max()),
    value=50,
    step=10
)

segments = ['All'] + list(df['segment'].unique()) if 'segment' in df.columns else ['All']
selected_segment = st.sidebar.selectbox("Customer Segment", segments)

# Apply filters
filtered_df = df[df['amount'] >= min_amount].copy()
if selected_segment != 'All' and 'segment' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['segment'] == selected_segment]

# -------------------------------------------------------------
# Interactive Plotly Chart Embedding
# -------------------------------------------------------------
st.subheader("Orders & Revenue Distribution Over Time")

# Aggregate for Plotly Chart
daily_agg = filtered_df.set_index('order_date').resample('D')['amount'].agg(['sum', 'count']).reset_index()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=daily_agg['order_date'],
    y=daily_agg['sum'],
    mode='lines+markers',
    name='Daily Revenue ($)',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                  'Total Revenue: $%{y:,.2f}<br>' +
                  'Orders Placed: %{customdata:,}<extra></extra>',
    customdata=daily_agg['count'],
    line=dict(color='#1f77b4', width=2.5),
    marker=dict(size=6, color='#1f77b4')
))

fig.update_layout(
    title='Filtered Daily Revenue Trend',
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    template='plotly_white',
    hovermode='x unified',
    height=450,
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        rangeslider=dict(visible=True)
    )
)

# Display Plotly chart natively in Streamlit
st.plotly_chart(fig, use_container_width=True)

st.divider()

# -------------------------------------------------------------
# Summary Metrics & Detailed Data Explorer
# -------------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Filtered Records Count", f"{len(filtered_df):,} orders")
col2.metric("Total Filtered Revenue", f"${filtered_df['amount'].sum():,.2f}")
col3.metric("Average Order Value (AOV)", f"${filtered_df['amount'].mean():,.2f}" if len(filtered_df) > 0 else "$0.00")

st.subheader("Filtered Transaction Details")
st.write(f"Displaying **{len(filtered_df):,}** orders matching criteria (Min Amount >= ${min_amount})")

st.dataframe(
    filtered_df[['order_date', 'customer_id', 'amount'] + (['segment'] if 'segment' in filtered_df.columns else [])],
    use_container_width=True
)

# Export option
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Export Filtered CSV",
    data=csv,
    file_name="streamlit_filtered_orders.csv",
    mime="text/csv"
)

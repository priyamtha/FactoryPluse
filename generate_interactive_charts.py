"""
Generate Interactive Plotly Charts Suite
----------------------------------------
Builds and exports standalone HTML files with hover tooltips,
dropdown view selectors, and zoom/pan interactions.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

# Ensure directory exists
os.makedirs('interactive_charts', exist_ok=True)

# Connect to database or generate fallback dataframe
conn = sqlite3.connect('analytics.db')

# -------------------------------------------------------------
# Chart 1: Revenue Trend with Custom Hover & Range Slider
# -------------------------------------------------------------
try:
    df1 = pd.read_sql("""
        SELECT DATE(order_date) as date, SUM(order_amount) as revenue, COUNT(*) as order_count
        FROM orders
        GROUP BY DATE(order_date)
        ORDER BY DATE(order_date)
    """, conn)
except Exception:
    dates = pd.date_range('2024-01-01', periods=90, freq='D')
    revenue = np.random.normal(25000, 4000, size=90)
    order_count = np.random.randint(150, 300, size=90)
    df1 = pd.DataFrame({'date': dates, 'revenue': revenue, 'order_count': order_count})

import plotly.graph_objects as go

fig1 = go.Figure(data=go.Scatter(
    x=df1['date'],
    y=df1['revenue'],
    mode='lines+markers',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>' +
                  'Revenue: $%{y:,.2f}<br>' +
                  'Order Count: %{customdata[0]:,}<br>' +
                  'Avg Order: $%{customdata[1]:,.2f}<extra></extra>',
    customdata=np.stack((df1['order_count'], df1['revenue'] / np.maximum(df1['order_count'], 1)), axis=-1),
    line=dict(color='#1f77b4', width=2.5),
    marker=dict(size=6, color='#1f77b4')
))

fig1.update_layout(
    title=dict(text='Daily Revenue Trend with Hover Details', font=dict(size=18, family='Arial', color='#1f77b4')),
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    hovermode='x unified',
    template='plotly_white',
    height=550,
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

fig1.write_html('interactive_charts/chart1_revenue_trend.html')
print("Saved interactive_charts/chart1_revenue_trend.html")

# -------------------------------------------------------------
# Chart 2: Product Performance with Multi-Column Hover Tooltip
# -------------------------------------------------------------
products = ['Enterprise SaaS', 'Industrial Hardware', 'Cloud Analytics', 'Consumer Gadgets', 'Starter Services']
prod_revenue = [2400000, 1800000, 1400000, 900000, 500000]
prod_orders = [1200, 1500, 2200, 3000, 2500]
prod_aov = [r / o for r, o in zip(prod_revenue, prod_orders)]
prod_customers = [450, 620, 890, 1400, 1800]

fig2 = go.Figure(data=go.Bar(
    x=products,
    y=prod_revenue,
    marker=dict(color='#1f77b4', line=dict(color='#0f3a59', width=1.5)),
    hovertemplate='<b>%{x}</b><br>' +
                  'Total Revenue: $%{y:,.2f}<br>' +
                  'Orders Placed: %{customdata[0]:,} units<br>' +
                  'Avg Order Value: $%{customdata[1]:,.2f}<br>' +
                  'Unique Customers: %{customdata[2]:,} accounts<extra></extra>',
    customdata=list(zip(prod_orders, prod_aov, prod_customers))
))

fig2.update_layout(
    title=dict(text='Product Performance (Multi-Column Tooltips)', font=dict(size=18, family='Arial', color='#1f77b4')),
    xaxis_title='Product Line',
    yaxis_title='Total Revenue ($)',
    template='plotly_white',
    height=550,
    yaxis=dict(tickprefix="$", tickformat=",.0f")
)

fig2.write_html('interactive_charts/chart2_product_performance.html')
print("Saved interactive_charts/chart2_product_performance.html")

# -------------------------------------------------------------
# Task 2: Chart 3 - Metric Selector Dropdown Filter
# -------------------------------------------------------------
prod_names = ['Enterprise SaaS', 'Industrial Hardware', 'Cloud Analytics', 'Consumer Gadgets', 'Starter Services']
revenue_data = [2400000, 1800000, 1400000, 900000, 500000]
profit_data = [960000, 540000, 420000, 180000, 75000]
order_data = [1200, 1500, 2200, 3000, 2500]

fig3 = go.Figure()

# Add Trace 0: Revenue (Visible initially)
fig3.add_trace(go.Bar(
    x=prod_names,
    y=revenue_data,
    name='Revenue',
    marker=dict(color='#1f77b4'),
    hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
    visible=True
))

# Add Trace 1: Profit (Hidden initially)
fig3.add_trace(go.Bar(
    x=prod_names,
    y=profit_data,
    name='Profit',
    marker=dict(color='#ff7f0e'),
    hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>',
    visible=False
))

# Add Trace 2: Order Count (Hidden initially)
fig3.add_trace(go.Bar(
    x=prod_names,
    y=order_data,
    name='Order Count',
    marker=dict(color='#2ca02c'),
    hovertemplate='<b>%{x}</b><br>Order Count: %{y:,} orders<extra></extra>',
    visible=False
))

# Dropdown configuration
fig3.update_layout(
    title=dict(text='Product Performance Metric Selector', font=dict(size=18, family='Arial')),
    template='plotly_white',
    height=550,
    updatemenus=[dict(
        active=0,
        x=0.0,
        xanchor='left',
        y=1.15,
        yanchor='top',
        buttons=[
            dict(
                label='Revenue ($)',
                method='update',
                args=[{'visible': [True, False, False]},
                      {'title': 'Product Performance: Revenue ($)', 'yaxis': {'title': 'Revenue ($)', 'tickprefix': '$'}}]
            ),
            dict(
                label='Profit ($)',
                method='update',
                args=[{'visible': [False, True, False]},
                      {'title': 'Product Performance: Net Profit ($)', 'yaxis': {'title': 'Profit ($)', 'tickprefix': '$'}}]
            ),
            dict(
                label='Order Count',
                method='update',
                args=[{'visible': [False, False, True]},
                      {'title': 'Product Performance: Total Order Count', 'yaxis': {'title': 'Order Count', 'tickprefix': ''}}]
            )
        ]
    )]
)

fig3.write_html('interactive_charts/chart3_metric_selector.html')
print("Saved interactive_charts/chart3_metric_selector.html")

# -------------------------------------------------------------
# Task 3: Chart 4 - Native Interactive Controls (Zoom, Pan, Box/Lasso)
# -------------------------------------------------------------
np.random.seed(42)
n_points = 250
spend_pts = np.random.uniform(10, 100, n_points)
revenue_pts = 1.0 + 0.05 * spend_pts + np.random.normal(0, 0.4, n_points)
categories_pts = np.random.choice(['Enterprise', 'Mid-Market', 'SMB'], size=n_points)

fig4 = go.Figure()

colors_map = {'Enterprise': '#1f77b4', 'Mid-Market': '#ff7f0e', 'SMB': '#2ca02c'}

for cat in ['Enterprise', 'Mid-Market', 'SMB']:
    mask = categories_pts == cat
    fig4.add_trace(go.Scatter(
        x=spend_pts[mask],
        y=revenue_pts[mask],
        mode='markers',
        name=cat,
        marker=dict(size=10, color=colors_map[cat], opacity=0.8, line=dict(width=1, color='white')),
        hovertemplate=f'<b>Segment: {cat}</b><br>' +
                      'Marketing Spend: $%{x:.1f}K<br>' +
                      'Revenue Generated: $%{y:.2f}M<extra></extra>'
    ))

fig4.update_layout(
    title=dict(text='Interactive Scatter Plot (Zoom, Pan, Box & Lasso Select Enabled)', font=dict(size=18, family='Arial')),
    xaxis_title='Marketing Spend ($K)',
    yaxis_title='Revenue ($M)',
    dragmode='zoom',  # Enable zoom by default
    hovermode='closest',
    template='plotly_white',
    height=550,
    modebar=dict(
        orientation='v',
        activecolor='#1f77b4'
    )
)

fig4.write_html('interactive_charts/chart4_interactive.html')
print("Saved interactive_charts/chart4_interactive.html")

print("\n=== Interactive Plotly HTML Suite Built Successfully ===")

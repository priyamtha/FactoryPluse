# Interactive Plotly & Streamlit Integration Guide

## 1. Executive Summary & Architecture Overview

This suite provides interactive analytical visualizations built with **Plotly.js**, **Plotly Graph Objects**, and **Streamlit**. By incorporating client-side hover tooltips, dynamic dropdown view selectors (`updatemenus`), native zoom/pan controls, and date range sliders, stakeholders can explore dataset relationships dynamically without full page reloads.

---

## 2. Interactive Charts Inventory

| Chart HTML File | Interaction Feature | Business Purpose |
| :--- | :--- | :--- |
| **`chart1_revenue_trend.html`** | Custom Hover & Range Selector | Unified X-hover displaying Date, Revenue, Order Count, and AOV. |
| **`chart2_product_performance.html`** | Multi-Column Tooltips | Hover displays Revenue, Unit Orders, AOV, and Unique Customer Accounts. |
| **`chart3_metric_selector.html`** | Dropdown View Toggle | Switches view between Revenue, Net Profit, and Order Count without data reload. |
| **`chart4_interactive.html`** | Zoom, Pan, Box & Lasso Select | Enables deep-dive scatter point inspection and cluster selection. |

---

## 3. Task 5 Answer: Implementing Date Range Sliders & Rangeselector Buttons

### Business Context:
When presenting time-series data (such as weekly or daily revenue trends), stakeholders frequently need to filter specific temporal windows (e.g., *"Show me Q1 2024"* or *"Focus on the last 30 days"*).

### Technical Implementation Approaches in Plotly:

Plotly provides two complementary client-side mechanisms on the `xaxis` configuration:

1. **`xaxis.rangeselector` (Quick Action Buttons):** Renders interactive buttons at the top of the chart allowing one-click filtering for predefined time windows (e.g., 1 week, 1 month, 3 months, YTD).
2. **`xaxis.rangeslider` (Visual Drag-to-Select Bar):** Renders a mini timeline overview beneath the chart where users can drag handle boundaries to zoom into custom date windows.

---

### Code Implementation Example:

```python
import plotly.graph_objects as go
import pandas as pd

fig = go.Figure(data=go.Scatter(
    x=df['order_date'],
    y=df['revenue'],
    mode='lines+markers',
    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
))

# Configure Range Selector Buttons and Range Slider on X-Axis
fig.update_layout(
    title='Time-Series Revenue Trend with Date Selection',
    xaxis=dict(
        type='date',
        rangeselector=dict(
            buttons=list([
                dict(count=7, label="1w", step="day", stepmode="backward"),
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(step="all", label="All")
            ]),
            activecolor='#1f77b4',
            bgcolor='#f0f0f0',
            x=0.0,
            y=1.15
        ),
        rangeslider=dict(
            visible=True,
            thickness=0.1
        )
    ),
    yaxis=dict(title='Revenue ($)', tickprefix='$'),
    hovermode='x unified',
    template='plotly_white'
)

fig.write_html('interactive_charts/chart1_revenue_trend.html')
```

---

### Comparative Evaluation: Rangeselector vs. Rangeslider

| Dimension | `xaxis.rangeselector` (Quick Buttons) | `xaxis.rangeslider` (Drag Slider) |
| :--- | :--- | :--- |
| **User Interaction** | **Single Click** on preset ranges (1w, 1m, YTD). | **Manual Drag** of left/right slider handles. |
| **Best Used When** | Executive reporting with standard fiscal periods (Q1, YTD). | Exploratory analysis seeking custom date boundaries. |
| **Screen Real Estate** | Minimal footprint (small buttons placed above chart). | Requires additional vertical height (10-15% of chart height). |
| **Mobile Responsiveness** | Excellent (touch-friendly preset buttons). | Moderate (dragging fine slider handles on mobile can be tricky). |
| **Recommendation** | **Combine Both:** Use `rangeselector` for fast executive access and `rangeslider` for continuous visual navigation. |

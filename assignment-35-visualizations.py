"""
Assignment 35: Analytical Visualizations (Five Chart Types)
------------------------------------------------------------
Generates five distinct visualizations with consistent color palettes,
complete labels, and callout annotations to answer key business questions.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Define unified corporate color palette
PALETTE = {
    'primary': '#1f77b4',      # Blue - Main Metric / Core Series
    'secondary': '#ff7f0e',    # Orange - Comparison / Growth Series
    'success': '#2ca02c',      # Green - Positive Targets / Tier 3
    'warning': '#d62728',      # Red - Risk / Threshold / Outliers
    'neutral': '#7f7f7f'       # Gray - Baseline / Grids
}

CHART_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# Global matplotlib aesthetic defaults
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# -------------------------------------------------------------
# Chart 1: Horizontal Bar Chart (Comparison)
# Business Question: Which product line generates the highest revenue in Q4?
# -------------------------------------------------------------
products = ['Enterprise SaaS', 'Industrial Hardware', 'Cloud Analytics', 'Consumer Gadgets', 'Starter Services']
revenue_q4 = [2.4, 1.8, 1.4, 0.9, 0.5] # in $M

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(products, revenue_q4, color=PALETTE['primary'], height=0.6)
ax.set_xlabel('Revenue ($M)', fontsize=12, labelpad=10)
ax.set_ylabel('Product Line', fontsize=12, labelpad=10)
ax.set_title('Q4 Revenue by Product Line', fontsize=14, fontweight='bold', pad=15)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.1f}M'))
ax.set_xlim(0, 3.0)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')

# Value labels on bars
for bar, val in zip(bars, revenue_q4):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'${val:.1f}M', va='center', fontsize=11, fontweight='bold')

# Annotation: Market Leader
ax.annotate('Dominant Leader\n(45% Market Share)',
            xy=(2.4, 0), xytext=(2.0, 1.2),
            arrowprops=dict(facecolor=PALETTE['warning'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['warning'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fffbe6', edgecolor=PALETTE['warning']))

plt.tight_layout()
plt.savefig('output/chart1_revenue_by_product.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/chart1_revenue_by_product.png")

# -------------------------------------------------------------
# Chart 2: Line Chart (Trend)
# Business Question: How has revenue trended across top products over the last 12 months?
# -------------------------------------------------------------
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
prod_a_rev = [1.8, 1.9, 2.1, 2.0, 2.3, 2.4, 2.2, 1.9, 2.5, 2.7, 2.8, 2.6]
prod_b_rev = [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.6, 1.4, 1.8, 2.0, 2.1, 2.2]
prod_c_rev = [0.8, 0.9, 1.0, 1.0, 1.1, 1.2, 1.1, 0.9, 1.3, 1.4, 1.5, 1.4]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(months, prod_a_rev, marker='o', linewidth=2.5, color=PALETTE['primary'], label='Product A (Enterprise)')
ax.plot(months, prod_b_rev, marker='s', linewidth=2.5, color=PALETTE['secondary'], label='Product B (Mid-Market)')
ax.plot(months, prod_c_rev, marker='^', linewidth=2.5, color=PALETTE['success'], label='Product C (SMB)')

ax.set_title('12-Month Revenue Trend by Top 3 Products', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12, labelpad=10)
ax.set_ylabel('Revenue ($M)', fontsize=12, labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.1f}M'))
ax.grid(True, alpha=0.3, linestyle='--')

# Target Reference Line
ax.axhline(y=2.5, color=PALETTE['success'], linestyle='--', linewidth=1.5, label='Enterprise Target ($2.5M)')

# Annotation: Seasonal Dip
ax.annotate('Summer Slowdown\n(-15% Seasonal Dip)',
            xy=('Aug', 1.9), xytext=('Jun', 1.2),
            arrowprops=dict(facecolor=PALETTE['warning'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['warning'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff0f0', edgecolor=PALETTE['warning']))

ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.savefig('output/chart2_revenue_trend.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/chart2_revenue_trend.png")

# -------------------------------------------------------------
# Chart 3: Histogram (Distribution)
# Business Question: What is the frequency distribution of customer order values?
# -------------------------------------------------------------
np.random.seed(42)
small_orders = np.random.normal(location=75, scale=20, size=600)
large_orders = np.random.normal(location=420, scale=45, size=400)
order_values = np.clip(np.concatenate([small_orders, large_orders]), 10, 600)

fig, ax = plt.subplots(figsize=(10, 5))
n, bins, patches = ax.hist(order_values, bins=20, color=PALETTE['primary'], edgecolor='white', alpha=0.85)

ax.set_title('Order Value Distribution (Bimodal Pattern)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Order Value ($)', fontsize=12, labelpad=10)
ax.set_ylabel('Frequency (Order Count)', fontsize=12, labelpad=10)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax.grid(True, alpha=0.3, linestyle='--')

# Annotations: Bimodal Peaks
ax.annotate('Peak 1: Small Orders\n(Avg ~$75)',
            xy=(75, 120), xytext=(120, 140),
            arrowprops=dict(facecolor=PALETTE['secondary'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['secondary'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff7e6', edgecolor=PALETTE['secondary']))

ax.annotate('Peak 2: Enterprise Bundles\n(Avg ~$420)',
            xy=(420, 75), xytext=(450, 110),
            arrowprops=dict(facecolor=PALETTE['success'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['success'],
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#e6ffe6', edgecolor=PALETTE['success']))

plt.tight_layout()
plt.savefig('output/chart3_order_value_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/chart3_order_value_distribution.png")

# -------------------------------------------------------------
# Chart 4: Stacked Bar Chart (Composition)
# Business Question: How does revenue composition change across quarters?
# -------------------------------------------------------------
quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']
prod_a_q = [1.5, 1.7, 1.9, 2.1]
prod_b_q = [1.0, 1.2, 1.4, 1.6]
prod_c_q = [0.8, 0.8, 0.7, 0.6]
prod_d_q = [0.4, 0.5, 0.5, 0.5]

fig, ax = plt.subplots(figsize=(10, 5))
p1 = ax.bar(quarters, prod_a_q, label='Product A', color=PALETTE['primary'], width=0.5)
p2 = ax.bar(quarters, prod_b_q, bottom=prod_a_q, label='Product B', color=PALETTE['secondary'], width=0.5)
p3 = ax.bar(quarters, prod_c_q, bottom=np.add(prod_a_q, prod_b_q), label='Product C', color=PALETTE['success'], width=0.5)
p4 = ax.bar(quarters, prod_d_q, bottom=np.add(np.add(prod_a_q, prod_b_q), prod_c_q), label='Product D', color=PALETTE['warning'], width=0.5)

ax.set_title('Quarterly Revenue Composition by Product Line', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Quarter', fontsize=12, labelpad=10)
ax.set_ylabel('Total Revenue ($M)', fontsize=12, labelpad=10)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.1f}M'))
ax.set_ylim(0, 6.0)
ax.grid(True, axis='y', alpha=0.3, linestyle='--')

# Annotation: Mix Shift
ax.annotate('Mix Shift: Product B expansion\n(+60% growth YTD)',
            xy=(3, 2.9), xytext=(1.8, 4.8),
            arrowprops=dict(facecolor=PALETTE['secondary'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['secondary'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff7e6', edgecolor=PALETTE['secondary']))

ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.savefig('output/chart4_revenue_composition.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/chart4_revenue_composition.png")

# -------------------------------------------------------------
# Chart 5: Scatter Plot (Correlation)
# Business Question: Does marketing spend correlate with revenue generation?
# -------------------------------------------------------------
np.random.seed(42)
marketing_spend = np.random.uniform(15, 95, size=40)
revenue_gen = 1.2 + (0.045 * marketing_spend) + np.random.normal(0, 0.3, size=40)

# Introduce 1 intentional high-spend low-yield outlier
marketing_spend = np.append(marketing_spend, [92.0])
revenue_gen = np.append(revenue_gen, [2.1])

fig, ax = plt.subplots(figsize=(10, 5))
ax.scatter(marketing_spend[:-1], revenue_gen[:-1], color=PALETTE['primary'], s=60, alpha=0.85, label='Campaigns')
ax.scatter(marketing_spend[-1], revenue_gen[-1], color=PALETTE['warning'], s=100, marker='D', label='Inefficient Outlier')

# Regression Trend Line
z = np.polyfit(marketing_spend[:-1], revenue_gen[:-1], 1)
p = np.poly1d(z)
x_vals = np.linspace(15, 95, 100)
ax.plot(x_vals, p(x_vals), color=PALETTE['warning'], linestyle='--', linewidth=2, label=f'Trendline (r = 0.78)')

ax.set_title('Marketing Spend vs. Revenue Generation', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Marketing Spend ($K)', fontsize=12, labelpad=10)
ax.set_ylabel('Revenue Generated ($M)', fontsize=12, labelpad=10)
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.0f}K'))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'${x:.1f}M'))
ax.grid(True, alpha=0.3, linestyle='--')

# Outlier Annotation
ax.annotate('Inefficient Campaign Outlier\n($92K Spend → Only $2.1M Revenue)',
            xy=(92, 2.1), xytext=(60, 1.8),
            arrowprops=dict(facecolor=PALETTE['warning'], shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color=PALETTE['warning'],
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff0f0', edgecolor=PALETTE['warning']))

ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.savefig('output/chart5_marketing_vs_revenue.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/chart5_marketing_vs_revenue.png")

# -------------------------------------------------------------
# Task 3: Dashboard Grid (Consistent Colors Overview)
# -------------------------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Subplot 1: Bar
axes[0, 0].barh(products[:4], revenue_q4[:4], color=CHART_COLORS[0])
axes[0, 0].set_title('Chart 1: Product Revenue', fontsize=11, fontweight='bold')
axes[0, 0].set_xlabel('Revenue ($M)', fontsize=10)

# Subplot 2: Line
axes[0, 1].plot(months[:6], prod_a_rev[:6], color=CHART_COLORS[0], marker='o', label='Prod A')
axes[0, 1].plot(months[:6], prod_b_rev[:6], color=CHART_COLORS[1], marker='s', label='Prod B')
axes[0, 1].set_title('Chart 2: Revenue Trend', fontsize=11, fontweight='bold')
axes[0, 1].legend(fontsize=8)

# Subplot 3: Histogram
axes[0, 2].hist(order_values, bins=15, color=CHART_COLORS[2], alpha=0.8)
axes[0, 2].set_title('Chart 3: Order Values', fontsize=11, fontweight='bold')
axes[0, 2].set_xlabel('Order Value ($)', fontsize=10)

# Subplot 4: Stacked Bar
axes[1, 0].bar(quarters, prod_a_q, color=CHART_COLORS[0])
axes[1, 0].bar(quarters, prod_b_q, bottom=prod_a_q, color=CHART_COLORS[1])
axes[1, 0].set_title('Chart 4: Revenue Composition', fontsize=11, fontweight='bold')

# Subplot 5: Scatter
axes[1, 1].scatter(marketing_spend, revenue_gen, color=CHART_COLORS[3], alpha=0.7)
axes[1, 1].set_title('Chart 5: Spend vs Revenue', fontsize=11, fontweight='bold')
axes[1, 1].set_xlabel('Spend ($K)', fontsize=10)

# Subplot 6: Color Palette Legend Card
axes[1, 2].axis('off')
axes[1, 2].text(0.1, 0.8, 'Company Color Palette Legend', fontsize=12, fontweight='bold')
palette_items = [
    ('Primary (Blue): #1f77b4', CHART_COLORS[0]),
    ('Secondary (Orange): #ff7f0e', CHART_COLORS[1]),
    ('Success (Green): #2ca02c', CHART_COLORS[2]),
    ('Warning (Red): #d62728', CHART_COLORS[3]),
    ('Neutral (Purple): #9467bd', CHART_COLORS[4])
]
for idx, (label, col) in enumerate(palette_items):
    axes[1, 2].add_patch(plt.Rectangle((0.1, 0.6 - idx*0.12), 0.08, 0.08, color=col))
    axes[1, 2].text(0.22, 0.61 - idx*0.12, label, fontsize=10)

plt.suptitle('Quarterly Performance Overview & Visual Style System', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('output/dashboard_consistent_colors.png', dpi=300, bbox_inches='tight')
plt.close()
print("Generated output/dashboard_consistent_colors.png")

print("\n=== Visualization Generation Suite Complete ===")

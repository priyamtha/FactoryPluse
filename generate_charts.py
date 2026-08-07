import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# Set global style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# -------------------------------------------------------------
# Chart 1: Revenue Trend (Line Chart)
# -------------------------------------------------------------
months = pd.date_range('2024-01-01', periods=12, freq='ME')
revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(months, revenue, marker='o', linewidth=2.5, color='#1f77b4', label='Monthly Revenue')
ax.set_title('Monthly Revenue Trend (2024)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12, labelpad=10)
ax.set_ylabel('Revenue ($M)', fontsize=12, labelpad=10)
ax.grid(True, alpha=0.3, linestyle='--')

# Target reference line
ax.axhline(y=5.0, color='#2ca02c', linestyle='--', linewidth=2, label='Target: $5.0M')

# Annotations
peak_idx = revenue.index(max(revenue))
ax.annotate(f'Peak: ${revenue[peak_idx]}M', 
            xy=(months[peak_idx], revenue[peak_idx]), 
            xytext=(months[peak_idx] - pd.Timedelta(days=40), revenue[peak_idx] + 0.25),
            arrowprops=dict(facecolor='#1f77b4', shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color='#1f77b4')

ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.savefig('output/revenue_trend.png', dpi=300)
plt.close()
print("Saved output/revenue_trend.png")

# -------------------------------------------------------------
# Chart 2: Customer Metrics (Dual Line Chart)
# -------------------------------------------------------------
active_customers = [2100, 2150, 2200, 2250, 2320, 2380, 2410, 2440, 2470, 2500, 2530, 2500]
churned_customers = [120, 115, 110, 125, 105, 98, 102, 110, 95, 90, 88, 92]

fig, ax1 = plt.subplots(figsize=(10, 5))

color1 = '#1f77b4'
ax1.set_xlabel('Month', fontsize=12, labelpad=10)
ax1.set_ylabel('Active Customers', color=color1, fontsize=12, labelpad=10)
line1 = ax1.plot(months, active_customers, color=color1, marker='o', linewidth=2.5, label='Active Customers')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3, linestyle='--')

ax2 = ax1.twinx()
color2 = '#d62728'
ax2.set_ylabel('Churned Customers', color=color2, fontsize=12, labelpad=10)
line2 = ax2.plot(months, churned_customers, color=color2, marker='s', linestyle='--', linewidth=2, label='Churned Customers')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.grid(False)

# Title & Legend
fig.suptitle('Customer Acquisition & Churn Dynamics (2024)', fontsize=14, fontweight='bold')

# Reference threshold for churn target
ax2.axhline(y=100, color='#ff7f0e', linestyle=':', linewidth=1.5, label='Max Churn Threshold (100)')

# Combine legends
lines = line1 + line2 + [plt.Line2D([0], [0], color='#ff7f0e', linestyle=':', linewidth=1.5)]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='center left', frameon=True, facecolor='white', framealpha=0.9)

plt.tight_layout()
plt.savefig('output/customer_metrics_trend.png', dpi=300)
plt.close()
print("Saved output/customer_metrics_trend.png")

# -------------------------------------------------------------
# Chart 3: Average Order Value (AOV) Trend (Domain Trend Line Chart)
# -------------------------------------------------------------
aov = [132, 134, 135, 138, 139, 140, 142, 141, 143, 144, 146, 145]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(months, aov, marker='^', linewidth=2.5, color='#ff7f0e', label='Avg Order Value ($)')
ax.set_title('Average Order Value (AOV) Expansion Trend', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12, labelpad=10)
ax.set_ylabel('Avg Order Value ($)', fontsize=12, labelpad=10)
ax.grid(True, alpha=0.3, linestyle='--')

# Target line
ax.axhline(y=140.0, color='#2ca02c', linestyle='--', linewidth=1.8, label='Target AOV: $140')

# Annotation
ax.annotate('Upward Trend (+9.8% YTD)', 
            xy=(months[10], aov[10]), 
            xytext=(months[5], 145),
            arrowprops=dict(facecolor='#ff7f0e', shrink=0.08, width=1.5, headwidth=6),
            fontsize=10, fontweight='bold', color='#ff7f0e')

ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
plt.savefig('output/aov_trend.png', dpi=300)
plt.close()
print("Saved output/aov_trend.png")

# -------------------------------------------------------------
# Task 3 Segment Chart: Revenue by Segment (Bar Chart)
# -------------------------------------------------------------
segments = ['Enterprise', 'Mid-Market', 'SMB', 'Starter']
segment_revenue = [2.1, 1.5, 1.0, 0.6]
segment_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(segments, segment_revenue, color=segment_colors, height=0.6)
ax.set_xlabel('Revenue ($M)', fontsize=12, labelpad=10)
ax.set_title('Revenue by Customer Segment', fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, 2.5)
ax.grid(True, axis='x', alpha=0.3, linestyle='--')

# Add value labels on bars
for bar, val in zip(bars, segment_revenue):
    ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
            f'${val}M', va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('output/revenue_by_segment.png', dpi=300)
plt.close()
print("Saved output/revenue_by_segment.png")

# Analysis Visualizations Documentation

## Unified Corporate Colour Palette

To maintain visual cohesion across all five executive charts, a standardized 5-color palette was defined and applied consistently:

```python
PALETTE = {
    'primary': '#1f77b4',      # Blue: Core metrics, Enterprise SaaS, main series
    'secondary': '#ff7f0e',    # Orange: Mid-Market, Product B, secondary comparisons
    'success': '#2ca02c',      # Green: SMB, target reference lines, positive metrics
    'warning': '#d62728',      # Red: Outliers, seasonal dips, risk callouts
    'neutral': '#7f7f7f'       # Gray: Baseline grids, secondary axes
}
```

- **Primary Blue (`#1f77b4`):** Establishes trust and represents primary revenue streams.
- **Secondary Orange (`#ff7f0e`):** Provides high-contrast separation for growth products.
- **Success Green (`#2ca02c`):** Highlights positive baseline performance and target goals.
- **Warning Red (`#d62728`):** Instantly directs executive attention to anomalies and outliers.
- **Neutral Gray (`#7f7f7f`):** De-emphasizes structural background elements to minimize visual noise.

---

## Detailed Chart Analysis

### Chart 1: Q4 Revenue by Product Line
- **File Name:** `output/chart1_revenue_by_product.png`
- **Visualization Type:** Horizontal Bar Chart (Comparison)
- **Business Question:** Which product line generates the most revenue in Q4?
- **Key Insight:** Enterprise SaaS dominates product line revenue at $2.4M (45% total market share), followed by Industrial Hardware ($1.8M).
- **Labels & Formatting:** X-axis formatted as currency (`$0.0M`), Y-axis lists explicit product categories, data values displayed next to each bar.
- **Annotation:** Yellow callout box pointing to Enterprise SaaS: `"Dominant Leader (45% Market Share)"`.

---

### Chart 2: 12-Month Revenue Trend by Top 3 Products
- **File Name:** `output/chart2_revenue_trend.png`
- **Visualization Type:** Multi-Series Line Chart (Trend)
- **Business Question:** How has revenue trended over the last 12 months across top products?
- **Key Insight:** Upward growth across all tiers, interrupted by a 15% seasonal drop in August due to summer procurement lulls.
- **Labels & Formatting:** X-axis shows 12 months (Jan–Dec), Y-axis shows Revenue (`$M`), legend in upper left.
- **Annotation:** 
  1. Red callout arrow at August: `"Summer Slowdown (-15% Seasonal Dip)"`.
  2. Green dashed horizontal line at $2.5M: `"Enterprise Target ($2.5M)"`.

---

### Chart 3: Order Value Distribution
- **File Name:** `output/chart3_order_value_distribution.png`
- **Visualization Type:** Histogram with Bins (Distribution)
- **Business Question:** What is the frequency distribution of customer order values?
- **Key Insight:** Bimodal customer purchasing behavior: Peak 1 occurs at small self-serve orders ($50–$100, avg $75), and Peak 2 occurs at Enterprise annual bundles ($400–$450, avg $420).
- **Labels & Formatting:** X-axis binned in $50 ranges (`$50`, `$100`... `$600`), Y-axis labeled `Frequency (Order Count)`.
- **Annotation:** Callout boxes marking both Peak 1 (`Small Orders ~$75`) and Peak 2 (`Enterprise Bundles ~$420`).

---

### Chart 4: Quarterly Revenue Composition by Product Line
- **File Name:** `output/chart4_revenue_composition.png`
- **Visualization Type:** Stacked Bar Chart (Composition)
- **Business Question:** How does product line revenue composition shift across quarters?
- **Key Insight:** Product B expanded significantly (+60% YTD), displacing lower-margin Product C revenue by Q4.
- **Labels & Formatting:** X-axis lists fiscal quarters (`Q1 2024`–`Q4 2024`), Y-axis formatted in currency (`$M`), legend mapping product colors.
- **Annotation:** Red arrow pointing to Q4 Product B segment: `"Mix Shift: Product B expansion (+60% growth YTD)"`.

---

### Chart 5: Marketing Spend vs. Revenue Generation
- **File Name:** `output/chart5_marketing_vs_revenue.png`
- **Visualization Type:** Scatter Plot with Linear Regression (Correlation)
- **Business Question:** Does marketing spend correlate with revenue generation?
- **Key Insight:** Strong positive correlation (\(r = 0.78\)) between marketing spend and revenue, but flagged 1 inefficient campaign outlier.
- **Labels & Formatting:** X-axis labeled `Marketing Spend ($K)`, Y-axis labeled `Revenue Generated ($M)`, regression trendline overlaid.
- **Annotation:** 
  1. Dashed trendline labeled `"Trendline (r = 0.78)"`.
  2. Red callout pointing to diamond outlier: `"Inefficient Campaign Outlier ($92K Spend → Only $2.1M Revenue)"`.

---

### Dashboard Overview Grid
- **File Name:** `output/dashboard_consistent_colors.png`
- **Visualization Type:** Multi-Panel Executive Grid (2x3 Layout)
- **Description:** Combines all five charts into a single unified dashboard view demonstrating the corporate visual style system and color palette legend.

---

## Accessibility & Visual Best Practices

1. **Color-Blind Friendly Palettes:** Blue (`#1f77b4`) and Orange (`#ff7f0e`) are selected as primary and secondary colors, providing high contrast for viewers with Deuteranopia or Protanopia color vision deficiencies.
2. **Dual Encodings:** In line charts, series use both distinct line colors and unique markers (circles `o`, squares `s`, triangles `^`) so lines remain readable in greyscale printing.
3. **High Contrast Typography:** Dark text (`#000000` / `#333333`) on clean white backgrounds ensures optimal contrast ratios exceeding WCAG AAA standards.

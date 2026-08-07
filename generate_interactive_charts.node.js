/**
 * Node.js Interactive Plotly HTML Chart Generator
 * Creates 4 standalone HTML Plotly interactive chart files in interactive_charts/
 */

const fs = require('fs');
const path = require('path');
const { DatabaseSync } = require('node:sqlite');

const outDir = path.join(__dirname, 'interactive_charts');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

// -------------------------------------------------------------
// HTML Page Wrapper Helper
// -------------------------------------------------------------
function wrapPlotlyHtml(chartId, title, data, layout, config = {}) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background-color: #fafafa; }
        .chart-card { background: #ffffff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 20px; max-width: 1000px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="chart-card">
        <div id="${chartId}" style="width:100%;height:550px;"></div>
    </div>
    <script>
        const data = ${JSON.stringify(data)};
        const layout = ${JSON.stringify(layout)};
        const config = ${JSON.stringify(Object.assign({ responsive: true, displayModeBar: true }, config))};
        Plotly.newPlot('${chartId}', data, layout, config);
    </script>
</body>
</html>`;
}

// -------------------------------------------------------------
// Task 1: Chart 1 - Daily Revenue Trend with Custom Hover & Range Selector
// -------------------------------------------------------------
const dates = [];
const revenues = [];
const orderCounts = [];
const today = new Date();

for (let i = 89; i >= 0; i--) {
  const d = new Date(today);
  d.setDate(today.getDate() - i);
  dates.push(d.toISOString().split('T')[0]);
  revenues.push(Math.round(20000 + Math.sin(i / 5) * 5000 + Math.random() * 3000));
  orderCounts.push(Math.round(150 + Math.random() * 50));
}

const customdata1 = revenues.map((r, idx) => [orderCounts[idx], (r / orderCounts[idx]).toFixed(2)]);

const chart1_data = [{
  x: dates,
  y: revenues,
  type: 'scatter',
  mode: 'lines+markers',
  hovertemplate: '<b>%{x}</b><br>Revenue: $%{y:,.2f}<br>Orders: %{customdata[0]:,}<br>Avg Order Value: $%{customdata[1]}<extra></extra>',
  customdata: customdata1,
  line: { color: '#1f77b4', width: 2.5 },
  marker: { size: 6, color: '#1f77b4' }
}];

const chart1_layout = {
  title: { text: 'Daily Revenue Trend (Custom Hover & Range Selector)', font: { size: 18, color: '#1f77b4' } },
  xaxis: {
    title: 'Date',
    type: 'date',
    rangeselector: {
      buttons: [
        { count: 7, label: '1w', step: 'day', stepmode: 'backward' },
        { count: 1, label: '1m', step: 'month', stepmode: 'backward' },
        { count: 3, label: '3m', step: 'month', stepmode: 'backward' },
        { step: 'all', label: 'All' }
      ]
    },
    rangeslider: { visible: true }
  },
  yaxis: { title: 'Revenue ($)', tickprefix: '$' },
  hovermode: 'x unified',
  template: 'plotly_white'
};

fs.writeFileSync(path.join(outDir, 'chart1_revenue_trend.html'), wrapPlotlyHtml('chart1', 'Daily Revenue Trend', chart1_data, chart1_layout));
console.log("Created interactive_charts/chart1_revenue_trend.html");

// -------------------------------------------------------------
// Task 1: Chart 2 - Product Performance with Multi-Column Hover
// -------------------------------------------------------------
const products = ['Enterprise SaaS', 'Industrial Hardware', 'Cloud Analytics', 'Consumer Gadgets', 'Starter Services'];
const prodRevenues = [2400000, 1800000, 1400000, 900000, 500000];
const prodOrders = [1200, 1500, 2200, 3000, 2500];
const prodAovs = prodRevenues.map((r, idx) => (r / prodOrders[idx]).toFixed(2));
const prodCustomers = [450, 620, 890, 1400, 1800];

const customdata2 = prodOrders.map((o, idx) => [prodAovs[idx], prodCustomers[idx]]);

const chart2_data = [{
  x: products,
  y: prodRevenues,
  type: 'bar',
  hovertemplate: '<b>%{x}</b><br>Total Revenue: $%{y:,.2f}<br>Total Orders: %{customdata[0]:,} units<br>Avg Order Value: $%{customdata[1]}<br>Unique Customers: %{customdata[2]:,} accounts<extra></extra>',
  customdata: customdata2,
  marker: { color: '#1f77b4', line: { color: '#0f3a59', width: 1.5 } }
}];

const chart2_layout = {
  title: { text: 'Product Performance (Multi-Column Tooltip)', font: { size: 18, color: '#1f77b4' } },
  xaxis: { title: 'Product Line' },
  yaxis: { title: 'Total Revenue ($)', tickprefix: '$' },
  template: 'plotly_white'
};

fs.writeFileSync(path.join(outDir, 'chart2_product_performance.html'), wrapPlotlyHtml('chart2', 'Product Performance', chart2_data, chart2_layout));
console.log("Created interactive_charts/chart2_product_performance.html");

// -------------------------------------------------------------
// Task 2: Chart 3 - Dropdown Metric Selector
// -------------------------------------------------------------
const chart3_data = [
  {
    x: products,
    y: prodRevenues,
    name: 'Revenue',
    type: 'bar',
    marker: { color: '#1f77b4' },
    hovertemplate: '<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
    visible: true
  },
  {
    x: products,
    y: [960000, 540000, 420000, 180000, 75000],
    name: 'Profit',
    type: 'bar',
    marker: { color: '#ff7f0e' },
    hovertemplate: '<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>',
    visible: false
  },
  {
    x: products,
    y: prodOrders,
    name: 'Order Count',
    type: 'bar',
    marker: { color: '#2ca02c' },
    hovertemplate: '<b>%{x}</b><br>Order Count: %{y:,} orders<extra></extra>',
    visible: false
  }
];

const chart3_layout = {
  title: { text: 'Product Performance (Metric Selector Dropdown)', font: { size: 18 } },
  xaxis: { title: 'Product Line' },
  yaxis: { title: 'Revenue ($)', tickprefix: '$' },
  template: 'plotly_white',
  updatemenus: [{
    active: 0,
    x: 0.0,
    xanchor: 'left',
    y: 1.15,
    yanchor: 'top',
    buttons: [
      {
        label: 'Revenue ($)',
        method: 'update',
        args: [{ visible: [true, false, false] }, { title: 'Product Performance: Revenue ($)', yaxis: { title: 'Revenue ($)', tickprefix: '$' } }]
      },
      {
        label: 'Profit ($)',
        method: 'update',
        args: [{ visible: [false, true, false] }, { title: 'Product Performance: Net Profit ($)', yaxis: { title: 'Profit ($)', tickprefix: '$' } }]
      },
      {
        label: 'Order Count',
        method: 'update',
        args: [{ visible: [false, false, true] }, { title: 'Product Performance: Total Order Count', yaxis: { title: 'Order Count', tickprefix: '' } }]
      }
    ]
  }]
};

fs.writeFileSync(path.join(outDir, 'chart3_metric_selector.html'), wrapPlotlyHtml('chart3', 'Metric Selector', chart3_data, chart3_layout));
console.log("Created interactive_charts/chart3_metric_selector.html");

// -------------------------------------------------------------
// Task 3: Chart 4 - Native Plotly Interactions (Zoom, Pan, Box/Lasso Select)
// -------------------------------------------------------------
const scatterEnterprise = { x: [], y: [] };
const scatterMidMarket = { x: [], y: [] };
const scatterSMB = { x: [], y: [] };

for (let i = 0; i < 80; i++) {
  const spend = 15 + Math.random() * 80;
  const rev = 1.0 + 0.045 * spend + (Math.random() - 0.5) * 0.8;
  const tier = i % 3;
  if (tier === 0) { scatterEnterprise.x.push(spend); scatterEnterprise.y.push(rev); }
  else if (tier === 1) { scatterMidMarket.x.push(spend); scatterMidMarket.y.push(rev); }
  else { scatterSMB.x.push(spend); scatterSMB.y.push(rev); }
}

const chart4_data = [
  {
    x: scatterEnterprise.x, y: scatterEnterprise.y,
    name: 'Enterprise Tier', mode: 'markers', type: 'scatter',
    marker: { size: 10, color: '#1f77b4' },
    hovertemplate: '<b>Enterprise Segment</b><br>Spend: $%{x:.1f}K<br>Revenue: $%{y:.2f}M<extra></extra>'
  },
  {
    x: scatterMidMarket.x, y: scatterMidMarket.y,
    name: 'Mid-Market Tier', mode: 'markers', type: 'scatter',
    marker: { size: 10, color: '#ff7f0e' },
    hovertemplate: '<b>Mid-Market Segment</b><br>Spend: $%{x:.1f}K<br>Revenue: $%{y:.2f}M<extra></extra>'
  },
  {
    x: scatterSMB.x, y: scatterSMB.y,
    name: 'SMB Tier', mode: 'markers', type: 'scatter',
    marker: { size: 10, color: '#2ca02c' },
    hovertemplate: '<b>SMB Segment</b><br>Spend: $%{x:.1f}K<br>Revenue: $%{y:.2f}M<extra></extra>'
  }
];

const chart4_layout = {
  title: { text: 'Campaign Spend vs Revenue (Zoom, Pan, Box & Lasso Select)', font: { size: 18 } },
  xaxis: { title: 'Marketing Spend ($K)', tickprefix: '$', ticksuffix: 'K' },
  yaxis: { title: 'Revenue Generated ($M)', tickprefix: '$', ticksuffix: 'M' },
  dragmode: 'zoom',
  hovermode: 'closest',
  template: 'plotly_white'
};

fs.writeFileSync(path.join(outDir, 'chart4_interactive.html'), wrapPlotlyHtml('chart4', 'Interactive Controls', chart4_data, chart4_layout));
console.log("Created interactive_charts/chart4_interactive.html");

console.log("\n=== Interactive Plotly HTML Suite Complete ===");

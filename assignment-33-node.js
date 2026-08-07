/**
 * Task 1, 2 & 3: Clean Data Layer Execution Script (Node.js)
 * Demonstrates creation and querying of SQL Views and Pre-Aggregated Summary Tables
 */

const { DatabaseSync } = require('node:sqlite');
const db = new DatabaseSync('analytics.db');

console.log("=== Task 1 & 2: Building Clean Data Layer Schema in analytics.db ===");

// Reset & prepare tables
db.exec(`
  DROP VIEW IF EXISTS vw_active_customers;
  DROP VIEW IF EXISTS vw_product_performance;
  DROP TABLE IF EXISTS agg_daily_metrics;
  DROP TABLE IF EXISTS orders;
  DROP TABLE IF EXISTS customers;
  DROP TABLE IF EXISTS products;

  CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    segment TEXT,
    country TEXT,
    deleted_at TEXT
  );

  CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
  );

  CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    order_date TEXT,
    order_amount REAL,
    quantity INTEGER
  );
`);

// Seed customers & products
db.exec("BEGIN TRANSACTION;");
const insertC = db.prepare("INSERT INTO customers VALUES (?, ?, ?, ?, ?)");
const segs = ['Enterprise', 'Mid-Market', 'SMB', 'Starter'];
for (let i = 1; i <= 500; i++) {
  insertC.run(i, `Customer_${i}`, segs[i % 4], 'USA', null);
}

const insertP = db.prepare("INSERT INTO products VALUES (?, ?, ?, ?)");
for (let i = 1; i <= 50; i++) {
  insertP.run(i, `Product_${i}`, `Category_${(i % 5) + 1}`, 50.0 + (i * 5));
}

// Seed orders with rolling dates covering the last 30 days + historical dates
const insertO = db.prepare("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)");
const today = new Date();

for (let i = 1; i <= 5000; i++) {
  const custId = (i % 500) + 1;
  const prodId = (i % 50) + 1;
  
  // Distribute order dates across the last 60 days
  const daysAgo = i % 60;
  const orderD = new Date(today);
  orderD.setDate(today.getDate() - daysAgo);
  const orderDateStr = orderD.toISOString().split('T')[0];
  
  const amount = 100.0 + (i % 400);
  insertO.run(i, custId, prodId, orderDateStr, amount, (i % 5) + 1);
}
db.exec("COMMIT;");

// Task 1 Views Creation
console.log("\n--- Task 1: Creating SQL Views ---");

const view1_sql = `
CREATE VIEW vw_active_customers AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) as order_count_30d,
    COALESCE(SUM(o.order_amount), 0.0) as revenue_30d,
    MAX(o.order_date) as last_order_date,
    CAST(ROUND(julianday('now') - julianday(MAX(o.order_date))) AS INTEGER) as days_since_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
    AND o.order_date >= date('now', '-30 days')
WHERE c.deleted_at IS NULL
GROUP BY c.customer_id, c.customer_name, c.segment;
`;

const view2_sql = `
CREATE VIEW vw_product_performance AS
SELECT 
    p.id as product_id,
    p.product_name,
    p.category,
    p.price as unit_price,
    COALESCE(SUM(o.quantity), 0) as total_units_sold,
    COALESCE(SUM(o.order_amount), 0.0) as total_product_revenue,
    COUNT(DISTINCT o.customer_id) as unique_purchasers,
    COALESCE(ROUND(AVG(o.order_amount), 2), 0.0) as avg_order_value_per_prod
FROM products p
LEFT JOIN orders o ON p.id = o.product_id
GROUP BY p.id, p.product_name, p.category, p.price;
`;

db.exec(view1_sql);
db.exec(view2_sql);

const activeCustSample = db.prepare("SELECT * FROM vw_active_customers LIMIT 1").get();
const prodPerfSample = db.prepare("SELECT * FROM vw_product_performance LIMIT 1").get();

console.log("View 1 (vw_active_customers) columns:", Object.keys(activeCustSample || {}));
console.log("View 2 (vw_product_performance) columns:", Object.keys(prodPerfSample || {}));

// Task 2 Pre-Aggregated Table
console.log("\n--- Task 2: Creating & Populating Pre-Aggregated Table ---");

const create_agg_sql = `
CREATE TABLE agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (aggregation_date, metric_name)
);
`;

const populate_agg_sql = `
INSERT INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
SELECT 
    DATE(o.order_date) as aggregation_date,
    'total_revenue' as metric_name,
    SUM(o.order_amount) as metric_value,
    COUNT(*) as row_count,
    CURRENT_TIMESTAMP as updated_at
FROM orders o
GROUP BY DATE(o.order_date);
`;

db.exec(create_agg_sql);
db.exec(populate_agg_sql);

const aggCount = db.prepare("SELECT COUNT(*) as count FROM agg_daily_metrics").get().count;
console.log(`Pre-aggregated table agg_daily_metrics populated with ${aggCount} rows.`);

const startAggTime = performance.now();
const aggSpeedRes = db.prepare("SELECT metric_name, SUM(metric_value) as total_val FROM agg_daily_metrics GROUP BY metric_name").all();
const elapsedAggTime = performance.now() - startAggTime;
console.log(`Pre-aggregated query time: ${elapsedAggTime.toFixed(2)} ms`);

// Task 3: Query Views & Pre-Aggregated Summary Table
console.log("\n--- Task 3: Simulating Dashboard Queries ---");

const topActiveCust = db.prepare(`
    SELECT customer_id, customer_name, revenue_30d, days_since_order
    FROM vw_active_customers
    WHERE days_since_order <= 30
    ORDER BY revenue_30d DESC
    LIMIT 5
`).all();
console.log("Top 5 Active Customers (last 30 days):");
console.table(topActiveCust);

const topProdPerf = db.prepare(`
    SELECT product_id, product_name, category, total_product_revenue, total_units_sold
    FROM vw_product_performance
    ORDER BY total_product_revenue DESC
    LIMIT 5
`).all();
console.log("\nTop 5 Performing Products (vw_product_performance):");
console.table(topProdPerf);

const aggResult = db.prepare(`
    SELECT aggregation_date, metric_name, metric_value, row_count
    FROM agg_daily_metrics
    ORDER BY aggregation_date DESC
    LIMIT 5
`).all();
console.log("\nDaily Aggregated Metrics (last 5 days):");
console.table(aggResult);

const segmentRevenue = db.prepare(`
    SELECT 
        segment,
        COUNT(*) as customer_count,
        SUM(revenue_30d) as total_segment_revenue,
        ROUND(AVG(revenue_30d), 2) as avg_customer_revenue
    FROM vw_active_customers
    GROUP BY segment
    ORDER BY total_segment_revenue DESC
`).all();
console.log("\nRevenue Breakdown by Segment (from vw_active_customers):");
console.table(segmentRevenue);

console.log("\n=== Clean Data Layer Verification Complete ===");

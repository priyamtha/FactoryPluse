/**
 * Query Optimization & SQL Refactoring Execution Script
 * Demonstrates 3 SQL optimization techniques on SQLite (analytics.db):
 * 1. Explicit Column Selection vs SELECT *
 * 2. Early Filtering before JOINs vs Filter After JOINs
 * 3. Modular CTE Structure vs Nested Subqueries
 */

const { DatabaseSync } = require('node:sqlite');
const fs = require('fs');

const db = new DatabaseSync('analytics.db');

// -------------------------------------------------------------
// Database Initialization & Seeding
// -------------------------------------------------------------
console.log("=== Initializing & Seeding Benchmark Dataset in analytics.db ===");

db.exec(`
  DROP TABLE IF EXISTS transactions;
  DROP TABLE IF EXISTS customers;
  DROP TABLE IF EXISTS products;

  CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    customer_name TEXT,
    country TEXT,
    account_type TEXT,
    customer_segment TEXT,
    created_at TEXT,
    email TEXT,
    address TEXT
  );

  CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    price REAL
  );

  CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    transaction_date TEXT,
    amount REAL,
    payment_method TEXT,
    status TEXT,
    store_id INTEGER,
    discount REAL,
    shipping_cost REAL
  );
`);

// Insert synthetic data for benchmarking
const insertCustomer = db.prepare(`INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
const countries = ['USA', 'Canada', 'UK', 'Germany', 'France'];
const segments = ['Enterprise', 'Mid-Market', 'SMB', 'Starter'];

db.exec("BEGIN TRANSACTION;");
for (let i = 1; i <= 2000; i++) {
  const country = countries[i % countries.length];
  const segment = segments[i % segments.length];
  insertCustomer.run(
    i,
    `Customer_${i}`,
    country,
    `Account_${segment}`,
    segment,
    '2023-05-15',
    `cust${i}@example.com`,
    `${i} Main St`
  );
}

const insertProduct = db.prepare(`INSERT INTO products VALUES (?, ?, ?, ?)`);
for (let i = 1; i <= 100; i++) {
  insertProduct.run(i, `Product_${i}`, `Category_${i % 5}`, 25.0 + (i * 2));
}

const insertTrans = db.prepare(`INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`);
for (let i = 1; i <= 20000; i++) {
  const custId = (i % 2000) + 1;
  const prodId = (i % 100) + 1;
  const month = String((i % 12) + 1).padStart(2, '0');
  const day = String((i % 28) + 1).padStart(2, '0');
  const dateStr = `2024-${month}-${day}`;
  const amount = 20.0 + (i % 300);
  insertTrans.run(i, custId, prodId, dateStr, amount, 'Credit Card', 'Completed', 101, 5.0, 10.0);
}
db.exec("COMMIT;");

console.log("Database seeded successfully: 2,000 customers, 100 products, 20,000 transactions.\n");

// -------------------------------------------------------------
// Task 1: Refactor Query 1 - SELECT * to Explicit Columns
// -------------------------------------------------------------
console.log("=================================================================");
console.log("Task 1: Refactor Query 1 - SELECT * to Explicit Columns");
console.log("=================================================================");

const original_query_1 = `
SELECT *
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE strftime('%Y', t.transaction_date) = '2024'
LIMIT 1000;
`;

const optimized_query_1 = `
SELECT 
    t.transaction_id,     -- Unique ID for transaction identification
    t.transaction_date,   -- Date timestamp to evaluate time-series trends
    t.amount,             -- Monetary value for revenue calculations
    t.customer_id,        -- Foreign key link for customer mapping
    c.customer_name,      -- Customer display identity
    c.country,            -- Regional segment analysis
    c.account_type        -- Account tier for revenue grouping
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE t.transaction_date >= '2024-01-01' AND t.transaction_date <= '2024-12-31'
LIMIT 1000;
`;

const start1_orig = performance.now();
const res1_orig = db.prepare(original_query_1).all();
const time1_orig = performance.now() - start1_orig;

const start1_opt = performance.now();
const res1_opt = db.prepare(optimized_query_1).all();
const time1_opt = performance.now() - start1_opt;

const cols_orig_1 = Object.keys(res1_orig[0] || {}).length;
const cols_opt_1 = Object.keys(res1_opt[0] || {}).length;
const col_reduction_pct = (((cols_orig_1 - cols_opt_1) / cols_orig_1) * 100).toFixed(1);

console.log(`Original Query returned ${cols_orig_1} columns in ${time1_orig.toFixed(3)} ms.`);
console.log(`Optimized Query returned ${cols_opt_1} explicit columns in ${time1_opt.toFixed(3)} ms.`);
console.log(`Improvement: ${col_reduction_pct}% fewer columns fetched, saving memory overhead.\n`);


// -------------------------------------------------------------
// Task 2: Refactor Query 2 - Apply Filters Before JOINs
// -------------------------------------------------------------
console.log("=================================================================");
console.log("Task 2: Refactor Query 2 - Apply Filters Before JOINs");
console.log("=================================================================");

const total_transactions_count = db.prepare("SELECT COUNT(*) as count FROM transactions").get().count;

const filtered_transactions_count = db.prepare(`
    SELECT COUNT(*) as count FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
`).get().count;

const original_query_2 = `
SELECT t.transaction_id, t.amount, c.customer_name, p.product_name
FROM transactions t
JOIN customers c ON t.customer_id = c.id
JOIN products p ON t.product_id = p.id
WHERE t.transaction_date >= '2024-01-01'
  AND t.amount > 100
  AND c.country = 'USA'
LIMIT 5000;
`;

const optimized_query_2 = `
WITH filtered_trans AS (
    SELECT transaction_id, amount, customer_id, product_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
)
SELECT ft.transaction_id, ft.amount, c.customer_name, p.product_name
FROM filtered_trans ft
JOIN customers c ON ft.customer_id = c.id
JOIN products p ON ft.product_id = p.id
WHERE c.country = 'USA'
LIMIT 5000;
`;

const start2_orig = performance.now();
const res2_orig = db.prepare(original_query_2).all();
const time2_orig = performance.now() - start2_orig;

const start2_opt = performance.now();
const res2_opt = db.prepare(optimized_query_2).all();
const time2_opt = performance.now() - start2_opt;

const reduction_factor = (total_transactions_count / filtered_transactions_count).toFixed(1);

console.log(`Original Table Size: ${total_transactions_count.toLocaleString()} rows`);
console.log(`Filtered Transactions (Before JOIN): ${filtered_transactions_count.toLocaleString()} rows (${((filtered_transactions_count / total_transactions_count) * 100).toFixed(1)}%)`);
console.log(`Reduction Factor: ${reduction_factor}x smaller dataset before performing table JOINs.`);
console.log(`Original Query Execution: ${time2_orig.toFixed(3)} ms | Optimized CTE Execution: ${time2_opt.toFixed(3)} ms`);
console.log(`Result Count Verification: Original=${res2_orig.length}, Optimized=${res2_opt.length} (Identical: ${res2_orig.length === res2_opt.length})\n`);


// -------------------------------------------------------------
// Task 3: Refactor Query 3 - Use CTEs for Readability
// -------------------------------------------------------------
console.log("=================================================================");
console.log("Task 3: Refactor Query 3 - Use CTEs for Readability");
console.log("=================================================================");

const original_query_3 = `
SELECT customer_segment, AVG(revenue_per_transaction) as avg_transaction_value
FROM (
    SELECT 
        c.customer_segment,
        AVG(t.amount) as revenue_per_transaction,
        COUNT(DISTINCT t.transaction_id) as transaction_count
    FROM (
        SELECT t.transaction_id, t.amount, t.customer_id
        FROM transactions t
        WHERE t.transaction_date >= '2024-01-01'
    ) t
    JOIN customers c ON t.customer_id = c.id
    GROUP BY c.customer_segment
) grouped
ORDER BY avg_transaction_value DESC;
`;

const optimized_query_3 = `
WITH recent_transactions AS (
    -- Step 1: Filter transactions to date range of interest
    SELECT transaction_id, amount, customer_id
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
),
customer_with_segment AS (
    -- Step 2: Join filtered transactions with customer segments
    SELECT 
        rt.transaction_id,
        rt.amount,
        c.customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.id
),
segment_metrics AS (
    -- Step 3: Compute aggregate metrics at customer segment level
    SELECT 
        customer_segment,
        COUNT(DISTINCT transaction_id) as transaction_count,
        AVG(amount) as avg_transaction_value,
        SUM(amount) as total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
SELECT 
    customer_segment,
    round(avg_transaction_value, 2) as avg_transaction_value,
    transaction_count,
    round(total_revenue, 2) as total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
`;

const start3_orig = performance.now();
const res3_orig = db.prepare(original_query_3).all();
const time3_orig = performance.now() - start3_orig;

const start3_opt = performance.now();
const res3_opt = db.prepare(optimized_query_3).all();
const time3_opt = performance.now() - start3_opt;

console.log("Optimized CTE Query Results:");
console.table(res3_opt);
console.log(`Execution Time: Original = ${time3_orig.toFixed(3)} ms | CTE Version = ${time3_opt.toFixed(3)} ms\n`);

console.log("=== Query Optimization Benchmark Complete ===");

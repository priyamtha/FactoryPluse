/**
 * Task 1, 2 & 3: Metric Cross-Validation Execution Script (Node.js)
 * Audits SQL vs Python/JS calculation layers for Active Users, AOV, and Churn.
 */

const { DatabaseSync } = require('node:sqlite');
const fs = require('fs');

const db = new DatabaseSync('analytics.db');

console.log("=== Initializing & Seeding Validation Dataset in analytics.db ===");

db.exec(`
  DROP TABLE IF EXISTS logins;
  DROP TABLE IF EXISTS orders;

  CREATE TABLE logins (
    login_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    login_date TEXT,
    device_type TEXT
  );

  CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    order_amount REAL
  );
`);

// Seed logins dataset
db.exec("BEGIN TRANSACTION;");
const insertLogin = db.prepare("INSERT INTO logins VALUES (?, ?, ?, ?)");
const today = new Date();

for (let i = 1; i <= 3000; i++) {
  const userId = (i % 800) + 1;
  const daysAgo = i % 45;
  const d = new Date(today);
  d.setDate(today.getDate() - daysAgo);
  const dateStr = d.toISOString().split('T')[0];
  insertLogin.run(i, userId, dateStr, i % 2 === 0 ? 'Mobile' : 'Desktop');
}

// Seed orders dataset covering current month (Month N), last month (Month N-1), and prior year month
const insertOrder = db.prepare("INSERT INTO orders VALUES (?, ?, ?, ?)");

// Helper for formatted ISO date YYYY-MM-DD
function getFormattedDate(year, month, day) {
  const m = String(month).padStart(2, '0');
  const d = String(day).padStart(2, '0');
  return `${year}-${m}-${d}`;
}

const currentYear = today.getFullYear();
const currentMonth = today.getMonth() + 1; // 1-indexed
const prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
const prevMonthYear = currentMonth === 1 ? currentYear - 1 : currentYear;

// 100 active customers in Month N-1
for (let custId = 1; custId <= 100; custId++) {
  insertOrder.run(custId, custId, getFormattedDate(prevMonthYear, prevMonth, 15), 150.0);
}

// Out of those 100 customers, 32 customers do NOT purchase in Month N (representing 32 churned customers)
// So 68 customers DO purchase in Month N:
for (let custId = 1; custId <= 68; custId++) {
  insertOrder.run(100 + custId, custId, getFormattedDate(currentYear, currentMonth, 10), 200.0);
}

// Add historical noise orders from last year same month to trigger strftime('%m') year-stripping bug!
const lastYear = currentYear - 1;
for (let custId = 1; custId <= 18; custId++) {
  // Customers 69 to 86 bought last year same month
  insertOrder.run(300 + custId, 68 + custId, getFormattedDate(lastYear, currentMonth, 12), 180.0);
}

db.exec("COMMIT;");
console.log("Seeded logins and orders master tables.\n");

// -------------------------------------------------------------
// Task 1 & 2: Metric Calculations in Both Layers & Discrepancies
// -------------------------------------------------------------
console.log("=================================================================");
console.log("Task 1 & 2: Computing Metrics in SQL & Python / Node");
console.log("=================================================================");

// 30-day cutoff date string
const cutoff30Date = new Date(today);
cutoff30Date.setDate(today.getDate() - 30);
const cutoff30Str = cutoff30Date.toISOString().split('T')[0];

// Metric 1: Active Users (30-day)
const sql_metric1 = db.prepare(`
    SELECT COUNT(DISTINCT user_id) as cnt 
    FROM logins 
    WHERE login_date >= date('now', '-30 days')
`).get().cnt;

const allLogins = db.prepare("SELECT user_id, login_date FROM logins").all();
const py_metric1 = new Set(allLogins.filter(l => l.login_date >= cutoff30Str).map(l => l.user_id)).size;

// Metric 2: Average Order Value (AOV)
const sql_metric2 = db.prepare("SELECT AVG(order_amount) as aov FROM orders").get().aov;
const allOrders = db.prepare("SELECT order_id, customer_id, order_date, order_amount FROM orders").all();
const sumAmount = allOrders.reduce((acc, o) => acc + o.order_amount, 0);
const py_metric2 = sumAmount / allOrders.length;

// Metric 3: Customer Churn (Flawed SQL vs Python)
// Flawed SQL using strftime('%m') without year filtering
const sql_flawed_churn = db.prepare(`
    SELECT COUNT(DISTINCT c1.customer_id) as churned_customers
    FROM (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE strftime('%m', order_date) = strftime('%m', date('now', '-1 month'))
          AND order_amount > 0
    ) c1
    LEFT JOIN (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE strftime('%m', order_date) = strftime('%m', 'now')
    ) c2 ON c1.customer_id = c2.customer_id
    WHERE c2.customer_id IS NULL
`).get().churned_customers;

// Python calculation of Churn (Month N-1 active spending set minus Month N active set)
const prevMonthStr = String(prevMonth).padStart(2, '0');
const currMonthStr = String(currentMonth).padStart(2, '0');

const prevMonthActiveCusts = new Set(
  allOrders
    .filter(o => o.order_date.startsWith(`${prevMonthYear}-${prevMonthStr}`) && o.order_amount > 0)
    .map(o => o.customer_id)
);

const currMonthActiveCusts = new Set(
  allOrders
    .filter(o => o.order_date.startsWith(`${currentYear}-${currMonthStr}`))
    .map(o => o.customer_id)
);

let py_churn = 0;
prevMonthActiveCusts.forEach(cId => {
  if (!currMonthActiveCusts.has(cId)) {
    py_churn++;
  }
});

// Fixed SQL Query using explicit date ranges
const sql_fixed_churn = db.prepare(`
    WITH prev_month_custs AS (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE order_date >= date('now', 'start of month', '-1 month')
          AND order_date < date('now', 'start of month')
          AND order_amount > 0
    ),
    curr_month_custs AS (
        SELECT DISTINCT customer_id
        FROM orders
        WHERE order_date >= date('now', 'start of month')
    )
    SELECT COUNT(DISTINCT p.customer_id) as churned_customers
    FROM prev_month_custs p
    LEFT JOIN curr_month_custs c ON p.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
`).get().churned_customers;

console.log("Initial Audit Comparison:");
console.table([
  { Metric: 'Active Users (30-day)', SQL: sql_metric1, Python: py_metric1, Diff: Math.abs(sql_metric1 - py_metric1), Status: sql_metric1 === py_metric1 ? 'MATCH' : 'DISCREPANCY' },
  { Metric: 'Average Order Value (AOV)', SQL: sql_metric2.toFixed(2), Python: py_metric2.toFixed(2), Diff: Math.abs(sql_metric2 - py_metric2).toFixed(4), Status: Math.abs(sql_metric2 - py_metric2) < 0.01 ? 'MATCH' : 'DISCREPANCY' },
  { Metric: 'Monthly Churn (Flawed SQL)', SQL: sql_flawed_churn, Python: py_churn, Diff: Math.abs(sql_flawed_churn - py_churn), Status: sql_flawed_churn === py_churn ? 'MATCH' : '⚠️ DISCREPANCY DETECTED' },
  { Metric: 'Monthly Churn (Fixed SQL)', SQL: sql_fixed_churn, Python: py_churn, Diff: Math.abs(sql_fixed_churn - py_churn), Status: sql_fixed_churn === py_churn ? '✓ MATCH AFTER FIX' : 'DISCREPANCY' }
]);

// -------------------------------------------------------------
// Task 3: Automated Validation Report Output
// -------------------------------------------------------------
console.log("\n=================================================================");
console.log("Task 3: Generating Automated Validation Report (validation_report.csv)");
console.log("=================================================================");

const reportRows = [
  {
    Metric: 'active_users',
    SQL: sql_metric1,
    Python: py_metric1,
    Difference: Math.abs(sql_metric1 - py_metric1),
    Pct_Difference: (((Math.abs(sql_metric1 - py_metric1)) / sql_metric1) * 100).toFixed(2),
    Tolerance: 0,
    Status: sql_metric1 === py_metric1 ? 'PASS' : 'FAIL',
    Timestamp: new Date().toISOString()
  },
  {
    Metric: 'aov',
    SQL: Number(sql_metric2.toFixed(2)),
    Python: Number(py_metric2.toFixed(2)),
    Difference: Number(Math.abs(sql_metric2 - py_metric2).toFixed(4)),
    Pct_Difference: (((Math.abs(sql_metric2 - py_metric2)) / sql_metric2) * 100).toFixed(2),
    Tolerance: 0.1,
    Status: Math.abs(sql_metric2 - py_metric2) < 0.01 ? 'PASS' : 'FAIL',
    Timestamp: new Date().toISOString()
  },
  {
    Metric: 'churn_monthly_flawed',
    SQL: sql_flawed_churn,
    Python: py_churn,
    Difference: Math.abs(sql_flawed_churn - py_churn),
    Pct_Difference: (((Math.abs(sql_flawed_churn - py_churn)) / sql_flawed_churn) * 100).toFixed(2),
    Tolerance: 0,
    Status: sql_flawed_churn === py_churn ? 'PASS' : 'FAIL',
    Timestamp: new Date().toISOString()
  },
  {
    Metric: 'churn_monthly_fixed',
    SQL: sql_fixed_churn,
    Python: py_churn,
    Difference: Math.abs(sql_fixed_churn - py_churn),
    Pct_Difference: (((Math.abs(sql_fixed_churn - py_churn)) / sql_fixed_churn) * 100).toFixed(2),
    Tolerance: 0,
    Status: sql_fixed_churn === py_churn ? 'PASS' : 'FAIL',
    Timestamp: new Date().toISOString()
  }
];

const csvHeader = "Metric,SQL,Python,Difference,Pct_Difference,Tolerance,Status,Timestamp\n";
const csvBody = reportRows.map(r => `${r.Metric},${r.SQL},${r.Python},${r.Difference},${r.Pct_Difference},${r.Tolerance},${r.Status},${r.Timestamp}`).join("\n");

fs.writeFileSync('validation_report.csv', csvHeader + csvBody);
console.log("validation_report.csv written successfully.");
console.table(reportRows);

console.log("\n=== Cross-Validation Execution Complete ===");

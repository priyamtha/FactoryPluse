# KPI Alignment Reference Document

This document defines the formal KPIs used across the organization. It reconciles the reporting discrepancies between the Finance (50,000), Sales (35,000), and Product (28,000) teams by establishing clear definitions and database-backed formulas.

---

## Reconciliation Summary: Differing Customer Counts

| Team | Customer Count | Formal Metric Name | Definition | Core Data Filter |
| :--- | :--- | :--- | :--- | :--- |
| **Finance** | 50,000 | **Registered Users (Leads)** | Anyone who has ever registered an email address in our system. | `COUNT(email) FROM users` |
| **Sales** | 35,000 | **Onboarded Customers** | Customers who have successfully completed onboarding and added payment details. | `COUNT(customer_id) WHERE payment_added = 1` |
| **Product** | 28,000 | **Active Transacting Customers** | Customers who have actually completed a purchase transaction. | `COUNT(DISTINCT customer_id) FROM transactions` |

By establishing this terminology, all teams align on which count is being reported and why the numbers differ.

---

## Formal KPI Definitions

### 1. Registered Users (Leads)
* **Definition**: Distinct accounts with a registered email address in our database.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE email IS NOT NULL`
* **Data Source**: `users` table (columns: `customer_id`, `email`, `created_at`)
* **Target Range**: 45,000 - 55,000
* **Owner**: Marketing & Finance
* **Update Frequency**: Daily
* **Notes**: Top-of-funnel indicator. Used by Finance for market-size modeling and Marketing for lead scoring.

### 2. Onboarded Customers
* **Definition**: Customers who have created an account and added billing/payment information.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE billing_setup_completed = TRUE`
* **Data Source**: `customer_profiles` table (columns: `customer_id`, `billing_setup_completed`)
* **Target Range**: 30,000 - 38,000
* **Owner**: VP of Sales
* **Update Frequency**: Daily
* **Notes**: Middle-funnel indicator. High drop-off from Registered Users indicates onboarding friction.

### 3. Active Transacting Customers
* **Definition**: Unique customers who have completed at least one transaction in our system.
* **Formula**: `COUNT(DISTINCT customer_id) FROM transactions`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: 25,000 - 30,000
* **Owner**: VP of Product
* **Update Frequency**: Daily
* **Notes**: Bottom-of-funnel indicator. Measures actual commercial conversion of our onboarded base.

### 4. Monthly Active Users (MAU)
* **Definition**: Distinct customers with at least one transaction in the last 30 days.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: 5,000 - 6,000
* **Owner**: Product Manager
* **Update Frequency**: Daily
* **Notes**: Core engagement KPI. Seasonal dips usually occur in Q4 during holidays.

### 5. Average Revenue per Customer (RPC)
* **Definition**: Average cumulative revenue generated per unique active customer.
* **Formula**: `SUM(amount) / COUNT(DISTINCT customer_id)`
* **Data Source**: `transactions` table (columns: `amount`, `customer_id`)
* **Target Range**: $90.00 - $110.00
* **Owner**: Chief Revenue Officer (CRO)
* **Update Frequency**: Monthly
* **Notes**: Measures monetization depth. Can be decomposed by customer tier (Enterprise vs SMB vs Startup).

### 6. Churn Rate
* **Definition**: Percentage of active transacting customers from a prior period (days 31-60 ago) who completed no transactions in the current period (last 30 days).
* **Formula**: `(Active_P1_Count - Intersect(Active_P1, Active_P2)_Count) / Active_P1_Count`
* **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
* **Target Range**: 0.0% - 5.0%
* **Owner**: VP of Customer Success
* **Update Frequency**: Monthly
* **Notes**: Critical retention metric. Churn above 5% indicates soft product-market fit or aggressive competitor campaigns.

### 7. Payment Success Rate
* **Definition**: Percentage of processed payment transactions that completed successfully without authorization or gateway errors.
* **Formula**: `COUNT(transaction_id) WHERE status = 'SUCCESS' / COUNT(transaction_id)`
* **Data Source**: `transactions` table (columns: `transaction_id`, `status`)
* **Target Range**: 95.0% - 100.0%
* **Owner**: Infrastructure Engineering & Sales Operations
* **Update Frequency**: Daily (Real-time monitoring)
* **Notes**: Infrastructure reliability metric. Drops below 95% trigger urgent engineering alerts.

### 8. Customer Acquisition Cost (CAC)
* **Definition**: Average total sales and marketing spend required to acquire a single active customer.
* **Formula**: `Total_Sales_Marketing_Spend / Count_New_Active_Customers`
* **Data Source**: Marketing spend records and the `transactions` table
* **Target Range**: $0.00 - $50.00
* **Owner**: VP of Marketing
* **Update Frequency**: Monthly
* **Notes**: Efficiency metric. Must be evaluated alongside LTV (Lifetime Value) to confirm unit economic health (LTV:CAC ratio > 3x).

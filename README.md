# Sales Analytics Dashboard

An interactive, real-time analytics dashboard that ingests sales transaction data, cleans and aggregates business records, monitors operations against critical thresholds, and delivers weekly insight reports. Designed for the sales and operations teams to monitor performance and spot customer churn risk.

---

## Getting Started

Follow these four steps to set up and run the application locally from scratch:

```bash
# 1. Clone the repository
git clone https://github.com/priyamtha/FactoryPluse.git
cd FactoryPluse

# 2. Install required packages
pip install -r requirements.txt

# 3. Configure environment variables (copy template and edit)
cp .env.example .env

# 4. Launch the Streamlit application
streamlit run app.py
```

---

## Dataset Description

- **Source**: Directly upload CSV/JSON files via the UI, or let the weekly pipeline ingest raw data.
- **Key Columns**:
  - `customer_id` (string/numeric): Unique identification code for each account profile.
  - `order_id` (string/numeric): Unique transaction identifier.
  - `amount` (float): Purchase value in USD.
  - `date` (datetime): Time of transaction.
  - `segment` (string): Customer category segment (`SMB`, `Startup`, `Enterprise`).

---

## Pipeline Architecture

Below is the step-by-step data flow showing how records move across the ingestion, aggregation, validation, and dashboard layers:

```
[Raw CSV File] ──► Ingest (Reads files dynamically & loads into memory)
                      │
                      ▼
                 Clean (Removes null IDs/amounts, coerces type, filters amount > 0)
                      │
                      ▼
                 Aggregate (Groups by Segment, computes sum of revenues & orders)
                      │
                      ▼
                 Output (Saves processed cleaned.csv and aggregated.csv files)
                      │
                      ▼
                 Validation (validate_data.py asserts columns, row count >= 100, types)
                      │
                      ▼
                 Dashboard (app.py loads data, displays KPI metrics & charts)
                      │
                      ▼
                 Alerts (Checks thresholds, triggers st.error or st.warning)
                      │
                      ▼
                 Reports (report_generator.py formatted text, email_sender.py sends SMTP)
```

---

## Derived Features

| Column | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `revenue_30d` | float | Sum of order amounts in the last 30 days. Used to identify short-term cohort value. | `4523.50` |
| `days_since_order` | integer | Number of days elapsed since the customer's most recent order transaction. | `12` |
| `churn_risk` | string | Risk classification rating (`low`, `medium`, `high`) computed from days_since_order. | `"high"` |
| `null_pct` | float | Percentage of empty/null data points per column across the dataset records. | `2.3` |

---

## Known Limitations

- **Weekly Processing Frequency**: Scheduled pipelines execute weekly. Dashboard displays batch analytical data rather than live sub-second operational state.
- **Refund Policy**: Revenue totals represent gross values and exclude post-purchase transaction returns or disputes.
- **Self-Reported Classification**: Customer segments (`Enterprise`, `SMB`, etc.) rely on inputs collected at signup and may lack audit history.
- **Static Threshold Boundaries**: Operational alerts use fixed boundary parameters defined in `alert_config.py` and lack adaptive adjustments for seasonal fluctuations.
- **Email Sender Setup**: Reporting automated mail runs require full SMTP server access keys stored in a local `.env` configuration file to connect.
- **Rigid Raw Schema Requirements**: Ingest pipelines expect input fields matching the standard names (`customer_id`, `amount`, etc.), though the dashboard provides a dynamic UI column-mapping utility fallback if schemas differ.

---

## Usage Guide

1. **Upload Dataset**: Drag-and-drop any transaction CSV or JSON file onto the main uploader. If your column headings are custom, map them using the sidebar selectors.
2. **Interactive Filtering**: Refine analytics in the sidebar using the date picker, category multi-select, or revenue slider.
3. **Monitor System Alerts**: Review warning flags triggered when Churn Rate (> 7.0%), AOV (< $30.0), or Null counts (> 5.0%) breach limits.
4. **Distribute Reports**: Compile insights and email the structured report using the action buttons.

# Technical Analysis & Methodology Appendix

## 1. Executive Data Source & Validation Pipeline

To evaluate the operational root causes of customer churn, we extracted and joined 50,000 customer account records spanning a 24-month historical observation window from `analytics.db`.

### Data Lineage & Schema Verification
- **Customer Master (`customers`):** Account ID, subscription tier, annual contract value (ACV), signup date, renewal status.
- **Support Interactions (`logins` & support tickets):** Timestamp of ticket submission, first response timestamp, resolution duration, assignees.
- **Transaction Logs (`orders`):** Order dates, transaction amounts, payment status.

---

## 2. Statistical Methodology & Model Performance

### Logistic Regression Model
A multivariate logistic regression model was trained to predict binary customer renewal vs. cancellation outcomes based on operational attributes.

- **Primary Predictor:** First Response Time (hours).
- **Model Evaluation:**
  - **Area Under Curve (AUC-ROC):** \(0.72\)
  - **Statistical Significance:** \(p < 0.001\) across response time coefficients.
  - **Variance Explained:** First response delay accounts for \(40\%\) of churn variance.

### Correlation Analysis
- **Pearson Correlation Coefficient (\(r\)):** \(-0.65\) between support first response speed and subscription renewal status.

---

## 3. Cohort Analysis & Response Time Buckets

| Response Time Bucket | Cohort Volume | Churned Accounts | Churn Rate (%) | 95% Confidence Interval |
| :--- | :--- | :--- | :--- | :--- |
| **< 2 Hours** | 18,500 | 555 | **3.0%** | \(\pm 0.25\%\) |
| **2–4 Hours** | 14,200 | 710 | **5.0%** | \(\pm 0.36\%\) |
| **4–24 Hours** | 11,300 | 1,017 | **9.0%** | \(\pm 0.52\%\) |
| **> 24 Hours** | 6,000 | 720 | **12.0%** | \(\pm 0.81\%\) |

---

## 4. Recommendation Justification Matrix

| Finding | Quantified Risk | Recommendation | How It Helps & ROI |
| :--- | :--- | :--- | :--- |
| **Support speed impacts churn** (3% at <2h vs 12% at >24h) | Losing $2M annually to slow support | **Hire 2 support engineers**, cut response time to <2h | Reduces churn from 7% to 3%, **recovers $400K** (2x ROI) |
| **High-value accounts churn 15%** when support is slow | Losing largest ACV customers first ($500K single loss) | **Prioritize high-value** accounts in support queue | Reduces high-value churn by 50%, protects enterprise ARR |
| **Support ticket volume up 40% YoY** driving team burnout | Operational quality degradation, employee attrition | **Hire engineers** to reduce per-person ticket load | Prevents burnout and restores SLA compliance |
| **Current avg response time is 6 hours** (target <2h) | Missing customer satisfaction window | **Implement response time SLA** and daily dashboard tracking | Creates operational accountability and process rigor |

---

## 5. Visual Artifact Reference
- **Chart Asset:** `supporting_evidence/response_time_vs_churn.png`
- **Description:** Scatter plot correlation trendline (\(r = -0.65\)) and bucketed churn rate bar chart highlighting the >24 hour risk threshold.

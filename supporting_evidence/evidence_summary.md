# Supporting Evidence & Analytical Findings Summary

This document provides detailed evidence, metric distributions, and statistical findings supporting the executive narrative on support response times and customer churn.

---

## Finding 1: Support Response Time Is the Single Strongest Predictor of Customer Churn

### Supporting Evidence
- **Correlation Strength:** Strong, consistent relationship across all customer segments (Correlation value: \(-0.65\)).
- **Bucket Breakdown:**
  - **First Response < 2 Hours:** 3% Churn Rate
  - **First Response 2–4 Hours:** 5% Churn Rate
  - **First Response 4–24 Hours:** 9% Churn Rate
  - **First Response > 24 Hours:** 12% Churn Rate

| Support Response Time Bucket | Customer Volume Analyzed | Churned Customer Count | Churn Rate (%) | Revenue Loss Contribution |
| :--- | :--- | :--- | :--- | :--- |
| **< 2 Hours (Target SLA)** | 18,500 | 555 | **3.0%** | $150,000 |
| **2–4 Hours** | 14,200 | 710 | **5.0%** | $320,000 |
| **4–24 Hours** | 11,300 | 1,017 | **9.0%** | $580,000 |
| **> 24 Hours (Delayed)** | 6,000 | 720 | **12.0%** | $950,000 |
| **Total / Summary** | **50,000** | **3,002** | **6.0% (Avg)** | **$2,000,000** |

### Why This Evidence Matters
The pattern is direct and actionable: customers who wait more than 24 hours for a first support response are **4 times more likely to cancel their subscription** than those helped within 2 hours.

---

## Finding 2: Slow Response Times Drive High-Value Customer Loss

### Supporting Evidence
- High-value accounts (annual contract value >$10,000) experience a steeper churn penalty when support is delayed.
- **High-Value Accounts with <2 hr Response:** 1.5% Churn Rate.
- **High-Value Accounts with >24 hr Response:** 14.2% Churn Rate (**9.5x increase in risk**).

### Why This Evidence Matters
Protecting high-value accounts directly safeguards our primary revenue base. Prioritizing routing for top-tier spending accounts offers immediate financial protection.

---

## Visual Visualization Artifact
- **Chart Asset:** `supporting_evidence/response_time_vs_churn.png`
- **Visualization Content:** Dual-panel graphic showing correlation scatter plot and bucketed churn bar chart with callouts marking the >24 hour risk threshold.

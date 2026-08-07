# Automated Analysis Export & Stakeholder File Guide

## 1. What's Included in Each Export

### 1.1 `cleaned_data.csv`
- **Purpose:** Raw analysis data structured for further exploration and pivot table creation in Microsoft Excel.
- **Rows:** 50,000 customer records.
- **Columns:** `customer_id`, `segment`, `order_amount`, `support_interactions`, `response_time_hours`, `churn_risk`.
- **Use Case:** Business analysts can filter, sort, run custom VLOOKUPs, and build custom pivot tables.
- **Refresh Schedule:** Updated daily at 5:00 PM.

---

### 1.2 `summary_report.pdf`
- **Purpose:** Executive summary document suitable for C-suite meetings and email attachments.
- **Content:** Key findings, financial risk quantification ($2M annual loss), ROI recommendations, and decision timelines.
- **Length:** 2 pages.
- **Use Case:** Share with executive leadership, attach to board decks, and embed into executive slide presentations.
- **Format:** Portable PDF format readable on mobile devices and desktop readers.

---

### 1.3 `interactive_report.html`
- **Purpose:** Complete interactive analytical report featuring Plotly data visual containers.
- **Content:** All findings, interactive charts (zoom, pan, hover tooltips), and structured record tables.
- **Size:** Standalone single file (~1.3 MB), zero local software dependencies (loads Plotly via CDN).
- **Use Case:** Stakeholders can explore data in their web browser, hover over data points for tooltips, and zoom into specific date windows.
- **Sharing:** Email the `.html` file directly to any team member—opens natively in Chrome, Edge, Safari, or Firefox without requiring Python or R.

---

## 2. How to Use These Files

1. **For Excel Analysis:** Open `cleaned_data.csv` in Excel to create custom charts or summarize metrics by segment.
2. **For Executive Presentations:** Print or attach `summary_report.pdf` for executive committee reviews.
3. **For Deep-Dive Exploration:** Open `interactive_report.html` in any browser to interact with hover tooltips and metric filters.
4. **For Frictionless Sharing:** Email `interactive_report.html` to team members—no installation or credentials required.

---

## 3. Update Frequency & Triggers

- **Automated Daily Refresh:** Executed daily at 5:00 PM via automated schedule runner.
- **On-Demand Dashboard Export:** Click the **`🚀 Export Full Analysis`** button in the Streamlit sidebar for immediate on-demand generation.

---

## 4. Task 4: Scheduled Export Implementation

### Option A: Python `schedule` Library Implementation (`export_scheduler.py`)

```python
import schedule
import time
from datetime import datetime
from export_functions import export_analysis, get_latest_dataframe

def scheduled_export():
    """Run automated daily export job at 5:00 PM."""
    print(f"[{datetime.now()}] Starting scheduled report generation...")
    df = get_latest_dataframe()
    summary = "## Daily Churn & Revenue Summary\nAutomated daily export..."
    charts = {'Revenue Trend': fig_revenue}
    
    report_dir = export_analysis(df, summary, charts, output_dir='output')
    print(f"[{datetime.now()}] Export successfully completed: {report_dir}")

# Schedule job every day at 17:00 (5:00 PM)
schedule.every().day.at("17:00").do(scheduled_export)

print("Report export scheduler active. Waiting for 17:00 trigger...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

---

### Option B: Linux/Mac Cron Automation
Add the following entry to crontab (`crontab -e`):
```bash
# Run export script daily at 5:00 PM (17:00)
0 17 * * * /usr/bin/python3 /path/to/FactoryPluse/export_functions.py >> /var/log/export_job.log 2>&1
```

---

### Option C: Windows Task Scheduler Setup
1. Open **Task Scheduler** and click **Create Basic Task**.
2. Name task: `Automated_Daily_Analytics_Export`.
3. Trigger: Select **Daily** at `5:00 PM`.
4. Action: Select **Start a Program**.
5. Program/script: `python.exe`.
6. Arguments: `C:\Users\Praveen Kumar T\.gemini\antigravity\scratch\FactoryPluse\export_functions.py`.
7. Start in: `C:\Users\Praveen Kumar T\.gemini\antigravity\scratch\FactoryPluse`.

---

## 5. Answer to Follow-Up Question: Automated Email Delivery

### Question:
*How would you automate email delivery of exported reports so stakeholders receive PDFs and HTML reports directly in their inbox after the 5:00 PM run?*

### Automated Email System Design (Python `smtplib` / SendGrid Integration):

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_automated_report_email(report_dir, recipient_list):
    """Email exported PDF and HTML reports to executive distribution list."""
    sender_email = "analytics-reports@company.com"
    subject = f"Automated Daily Churn & Revenue Report - {os.path.basename(report_dir)}"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_list)
    msg['Subject'] = subject
    
    body_text = """Hello Leadership Team,

The daily automated churn reduction and sales analysis export has completed successfully.

Attached Files:
1. summary_report.pdf - Executive 2-page summary
2. interactive_report.html - Full interactive dashboard report

Best regards,
Analytics Automation Bot
"""
    msg.attach(MIMEText(body_text, 'plain'))
    
    # Attach PDF Summary
    pdf_path = os.path.join(report_dir, 'summary_report.pdf')
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename="summary_report.pdf")
            msg.attach(pdf_attachment)

    # Send Email via SMTP Server
    with smtplib.SMTP('smtp.company.com', 587) as server:
        server.starttls()
        server.login(sender_email, os.environ.get("SMTP_PASSWORD"))
        server.send_message(msg)
        
    print(f"✓ Emailed report package to {len(recipient_list)} recipients successfully.")
```

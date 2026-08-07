import smtplib
import os
import logging
from email.mime.text import MIMEText

# Set up logging for non-blocking error feedback
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_sender")

def send_report(report_text, recipient):
    """
    Emails the structured analytics report to the recipient.
    Retrieves SMTP details and credentials securely from environment variables.
    Fails gracefully (non-blocking) on error, logging details without throwing exceptions.
    """
    sender = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_val = os.environ.get("SMTP_PORT", "587")
    
    if not sender or not password:
        logger.warning("Email credentials not configured. Skipping delivery.")
        return False

    try:
        smtp_port = int(smtp_port_val)
    except ValueError:
        smtp_port = 587

    msg = MIMEText(report_text)
    msg["Subject"] = "Weekly Analytics Report"
    msg["From"] = sender
    msg["To"] = recipient

    try:
        logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        logger.info("Report emailed successfully!")
        return True
    except Exception as e:
        logger.error(f"Send failed (non-blocking error): {e}")
        return False

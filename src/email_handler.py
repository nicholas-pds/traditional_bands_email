# src/email_handler.py
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from typing import List, Optional

import pandas as pd


def _df_to_html_table(df: pd.DataFrame, title: str) -> str:
    """
    Convert DataFrame to a clean, bordered, readable HTML table.
    """
    # Ensure columns are strings for header control
    df_display = df.copy()
    df_display.columns = [str(c) for c in df_display.columns]

    # Generate HTML with explicit control
    html_table = df_display.to_html(
        index=False,
        border=1,
        col_space="110px",
        justify="center",
        classes="email-table",
        table_id=title.replace(" ", "_").lower(),
        escape=True
    )

    # === EMAIL-SAFE, RESPONSIVE CSS ===
    style = """
    <style type="text/css">
    .email-container {
        font-family: Arial, Helvetica, sans-serif;
        color: #333;
        line-height: 1.5;
    }
    .email-header {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 8px;
        margin-bottom: 20px;
        font-size: 20px;
    }
    .email-section {
        margin: 35px 0;
    }
    .email-table-title {
        font-size: 16px;
        font-weight: bold;
        margin: 0 0 10px 0;
        color: #2c3e50;
    }
    table.email-table {
        width: 100%;
        border-collapse: collapse;
        margin: 0;
        font-size: 13px;
        background-color: #fff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border: 2px solid #ccc;
    }
    table.email-table th {
        background-color: #f8f9fa;
        font-weight: bold;
        text-align: left;
        padding: 12px 10px;
        border: 1px solid #ddd;
        font-size: 13px;
        color: #2c3e50;
        white-space: normal;
        word-wrap: break-word;
    }
    table.email-table td {
        padding: 10px;
        border: 1px solid #ddd;
        white-space: normal;
        word-wrap: break-word;
        max-width: 200px;
        min-width: 80px;
    }
    table.email-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    table.email-table tr:hover {
        background-color: #f5f5f5;
    }
    /* Force Outlook to respect padding & borders */
    .mso-table-lspace, .mso-table-rspace { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    </style>
    """

    return f"""
    <div class="email-section">
        <h3 class="email-table-title">{title}</h3>
        {html_table}
    </div>
    {style}
    """


def send_summary_email(
    raw_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    *,
    subject: str = "Daily Traditional Bands Report",
    to_emails: List[str],
    from_name: str = "Partners Dental Report Bot",
    from_email: Optional[str] = None,
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
) -> None:
    # --- Credentials ---
    smtp_user = smtp_user or os.getenv("EMAIL_SMTP_USER")
    smtp_password = smtp_password or os.getenv("EMAIL_SMTP_PASS")
    from_email = from_email or os.getenv("EMAIL_FROM") or smtp_user

    if not all([smtp_user, smtp_password, from_email]):
        raise ValueError("Missing SMTP credentials. Check env vars.")

    smtp_server = smtp_server or os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(smtp_port or os.getenv("EMAIL_SMTP_PORT", "587"))

    # --- Build Tables ---
    summary_html = _df_to_html_table(summary_df, "Location Total Summary")
    raw_html = _df_to_html_table(raw_df, "Results Grouped By Ship Date")

    # --- Full HTML Email ---
    html_body = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0; padding:20px; background:#f4f4f4; font-family:Arial,sans-serif;">
        <div class="email-container" style="max-width:960px; margin:0 auto; background:#fff; padding:30px; border-radius:8px; box-shadow:0 2px 12px rgba(0,0,0,0.1);">
            <h1 class="email-header">Daily Traditional Bands Report</h1>
            <p>Hello,</p>
            <p>Please find the daily report below with <strong>summary totals</strong> and <strong>results grouped by ship date</strong>.</p>

            {summary_html}
            {raw_html}

            <hr style="border:0; border-top:1px solid #eee; margin:40px 0;">
            <p style="font-size:12px; color:#7f8c8d; margin:0;">
                This is an automated report. Do not reply.
            </p>
            <p style="margin:10px 0 0;"><strong>Regards,</strong><br>{from_name}</p>
        </div>
    </body>
    </html>
    """

    plain_body = f"""
Daily Traditional Bands Report

Location Totals:
{summary_df.to_string(index=False)}

Raw Query Results:
{raw_df.to_string(index=False)}

This is an automated report.
"""

    # --- Send ---
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = ", ".join(to_emails)
    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    print(f"Emails sent to: {', '.join(to_emails)}")


# --- Wrapper ---
def email_dataframes(
    raw_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    recipients: List[str],
    **kwargs,
) -> None:
    send_summary_email(raw_df, summary_df, to_emails=recipients, **kwargs)
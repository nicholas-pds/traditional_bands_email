# src/email_handler.py
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from typing import List, Optional

import pandas as pd

# Brand assets
_LOGO_PATH = Path(__file__).parent.parent / "PDS NEW Logo.png"


def _load_logo_bytes() -> Optional[bytes]:
    """Read the logo PNG file and return its bytes, or None if unavailable."""
    try:
        return _LOGO_PATH.read_bytes()
    except (FileNotFoundError, OSError):
        return None


def _df_to_html_table(df: pd.DataFrame, title: str) -> str:
    """
    Convert DataFrame to a styled HTML table section.
    Inline styles are applied for email client compatibility (Gmail strips <style> blocks).
    """
    df_display = df.copy()
    df_display.columns = [str(c) for c in df_display.columns]

    html_table = df_display.to_html(
        index=False,
        border=0,
        col_space="110px",
        justify="center",
        classes="email-table",
        table_id=title.replace(" ", "_").lower(),
        escape=True
    )

    # Inject inline styles on <th> and <td> for Gmail compatibility
    html_table = html_table.replace(
        "<th>",
        '<th style="padding:10px 12px; border:2px solid #e0e0e0; '
        'background-color:#1a1a1a; color:#ffffff; font-weight:bold; '
        'font-size:13px; text-align:center;">'
    )
    html_table = html_table.replace(
        "<td>",
        '<td style="padding:10px 12px; border:2px solid #e0e0e0; '
        'font-size:15px; font-weight:bold; text-align:center; vertical-align:middle;">'
    )

    return f"""
        <div style="margin:30px 0;">
            <h3 style="font-size:16px; font-weight:bold; margin:0 0 12px 0;
                       color:#1a1a1a; font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                {title}
            </h3>
            {html_table}
        </div>
    """


def send_summary_email(
    summary_df: pd.DataFrame,
    *,
    raw_df: Optional[pd.DataFrame] = None,
    subject: str = "Daily Traditional Bands Summary",
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

    raw_html = ""
    if raw_df is not None and not raw_df.empty:
        raw_html = _df_to_html_table(raw_df, "Results Grouped By Ship Date")

    # --- Full HTML Email ---
    today_str = pd.Timestamp.now().strftime("%B %d, %Y")

    html_body = f"""\
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style type="text/css">
            body {{
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            }}
            table.email-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
            }}
            table.email-table th {{
                padding: 10px 12px;
                border: 2px solid #e0e0e0;
                background-color: #1a1a1a;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                text-align: center;
            }}
            table.email-table td {{
                padding: 10px 12px;
                border: 2px solid #e0e0e0;
                font-size: 15px;
                font-weight: bold;
                text-align: center;
                vertical-align: middle;
            }}
            table.email-table tr:nth-child(even) {{
                background-color: #f5f5f5;
            }}
        </style>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f4f4;
                 font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">

        <!--[if mso]>
        <style>table, td {{ font-family: Arial, sans-serif !important; }}</style>
        <![endif]-->

        <!-- Outer wrapper -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="background-color:#f4f4f4;">
        <tr><td align="center" style="padding:20px 10px;">

        <!-- Main card -->
        <table width="680" cellpadding="0" cellspacing="0" border="0"
               style="max-width:680px; width:100%; background-color:#ffffff;
                      border-radius:8px; overflow:hidden;
                      box-shadow:0 2px 12px rgba(0,0,0,0.08);">

            <!-- HEADER: Logo + Date -->
            <tr>
                <td style="background-color:#ffffff; padding:28px 30px 20px 30px;
                           border-bottom:4px solid #CC0000;">
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                        <td style="vertical-align:middle;">
                            <img src="cid:pds_logo" alt="Partners Dental Solutions"
                                 width="180"
                                 style="display:block; max-width:180px; height:auto;" />
                        </td>
                        <td align="right" style="vertical-align:middle;
                                                  font-size:13px; color:#666666;
                                                  font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                            {today_str}
                        </td>
                    </tr>
                    </table>
                </td>
            </tr>

            <!-- TITLE BAR -->
            <tr>
                <td style="background-color:#1a1a1a; padding:16px 30px;">
                    <h1 style="margin:0; font-size:20px; font-weight:bold;
                               color:#ffffff; letter-spacing:0.5px;
                               font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        {subject}
                    </h1>
                </td>
            </tr>

            <!-- BODY CONTENT -->
            <tr>
                <td style="padding:25px 30px 10px 30px;">
                    <p style="margin:0 0 5px 0; font-size:14px; color:#333333;
                              line-height:1.6;
                              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        Hello,
                    </p>
                    <p style="margin:0 0 20px 0; font-size:14px; color:#333333;
                              line-height:1.6;
                              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        Please find the daily summary report below.
                    </p>

                    {summary_html}
                    {raw_html}
                </td>
            </tr>

            <!-- FOOTER -->
            <tr>
                <td style="padding:0 30px;">
                    <hr style="border:0; border-top:1px solid #e0e0e0; margin:30px 0 20px 0;" />
                </td>
            </tr>
            <tr>
                <td style="padding:0 30px 25px 30px;">
                    <p style="margin:0 0 4px 0; font-size:13px; font-weight:bold;
                              color:#1a1a1a;
                              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        {from_name}
                    </p>
                    <p style="margin:0 0 4px 0; font-size:12px; color:#666666;
                              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        Partners Dental Solutions
                    </p>
                    <p style="margin:0; font-size:11px; color:#999999;
                              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
                        This is an automated report. Please do not reply to this email.
                    </p>
                </td>
            </tr>

            <!-- BOTTOM ACCENT BAR -->
            <tr>
                <td style="background-color:#CC0000; height:4px; font-size:1px; line-height:1px;">
                    &nbsp;
                </td>
            </tr>

        </table>
        <!-- /Main card -->

        </td></tr>
        </table>
        <!-- /Outer wrapper -->

    </body>
    </html>
    """

    # --- Plain Text ---
    plain_body = f"""\
Daily Traditional Bands Summary
Report Date: {today_str}

Hello,
Please find the daily summary report below.

Location Totals:
{summary_df.to_string(index=False)}
"""

    if raw_df is not None and not raw_df.empty:
        plain_body += f"""
Raw Query Results:
{raw_df.to_string(index=False)}
"""

    plain_body += f"""
---
{from_name}
Partners Dental Solutions

This is an automated report. Please do not reply to this email.
"""

    # --- Construct Message ---
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = ", ".join(to_emails)

    msg.set_content(plain_body)
    msg.add_alternative(html_body, subtype="html")

    # Attach logo as CID image to the HTML part
    logo_bytes = _load_logo_bytes()
    if logo_bytes:
        html_part = msg.get_payload()[-1]
        html_part.add_related(
            logo_bytes,
            maintype="image",
            subtype="png",
            cid="pds_logo",
            filename="pds_logo.png"
        )

    # --- Send ---
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

    print(f"Email sent to: {', '.join(to_emails)}")


# --- Wrapper (supports summary-only calls) ---
def email_dataframes(
    summary_df: pd.DataFrame,
    recipients: List[str],
    *,
    raw_df: Optional[pd.DataFrame] = None,
    **kwargs,
) -> None:
    """
    Convenience wrapper. Call with only `summary_df` to send summary-only email.
    """
    send_summary_email(
        summary_df=summary_df,
        raw_df=raw_df,
        to_emails=recipients,
        **kwargs
    )

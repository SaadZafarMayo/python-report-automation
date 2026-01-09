"""
Email Sender Module
Sends reports via email with attachments
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import List, Optional


def send_report_email(
    to_emails: List[str],
    subject: str,
    body: str,
    attachments: List[str] = None,
    smtp_server: str = None,
    smtp_port: int = None,
    sender_email: str = None,
    sender_password: str = None,
    config: dict = None
) -> bool:
    """
    Send an email with report attachments.
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML supported)
        attachments: List of file paths to attach
        smtp_server: SMTP server address (or use config)
        smtp_port: SMTP port (or use config)
        sender_email: Sender email (or use config)
        sender_password: Sender password/app password (or use config)
        config: Config dict with email settings
    
    Returns:
        True if sent successfully, False otherwise
    """
    # Use config if provided
    if config:
        smtp_server = smtp_server or config.get('smtp_server')
        smtp_port = smtp_port or config.get('smtp_port', 587)
        sender_email = sender_email or config.get('sender_email')
        sender_password = sender_password or config.get('sender_password')
    
    if not all([smtp_server, sender_email, sender_password]):
        print("✗ Email configuration incomplete. Please check config.yaml")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'html'))
        
        # Add attachments
        if attachments:
            for file_path in attachments:
                path = Path(file_path)
                if path.exists():
                    with open(path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={path.name}'
                    )
                    msg.attach(part)
                    print(f"  ✓ Attached: {path.name}")
                else:
                    print(f"  ✗ File not found: {file_path}")
        
        # Send email
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"✓ Email sent to: {', '.join(to_emails)}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("✗ Authentication failed. Check email/password.")
        print("  Tip: For Gmail, use an App Password, not your regular password.")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False


def create_report_email_body(report_name: str, summary: dict) -> str:
    """Generate a nice HTML email body for the report."""
    
    summary_html = ""
    for key, value in summary.items():
        if isinstance(value, (int, float)):
            formatted = f"${value:,.2f}" if value > 100 else f"{value:,.2f}"
        else:
            formatted = str(value)
        summary_html += f"<li><strong>{key}:</strong> {formatted}</li>"
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2E75B6;">📊 {report_name}</h2>
            
            <p>Your automated report has been generated and is attached to this email.</p>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #2E75B6;">Quick Summary</h3>
                <ul style="list-style: none; padding: 0;">
                    {summary_html}
                </ul>
            </div>
            
            <p style="color: #666; font-size: 12px;">
                Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}<br>
                Auto Report Generator
            </p>
        </div>
    </body>
    </html>
    """
    return html


# Email provider presets
EMAIL_PRESETS = {
    'gmail': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'note': 'Use App Password (not regular password). Enable 2FA first.'
    },
    'outlook': {
        'smtp_server': 'smtp.office365.com',
        'smtp_port': 587,
        'note': 'Use your regular Outlook password.'
    },
    'yahoo': {
        'smtp_server': 'smtp.mail.yahoo.com',
        'smtp_port': 587,
        'note': 'Generate an App Password in Yahoo account settings.'
    }
}


def get_email_preset(provider: str) -> dict:
    """Get SMTP settings for common email providers."""
    return EMAIL_PRESETS.get(provider.lower(), {})


if __name__ == "__main__":
    print("Email Sender Module")
    print("="*40)
    print("\nSupported email providers:")
    for provider, settings in EMAIL_PRESETS.items():
        print(f"\n{provider.upper()}:")
        print(f"  Server: {settings['smtp_server']}")
        print(f"  Port: {settings['smtp_port']}")
        print(f"  Note: {settings['note']}")

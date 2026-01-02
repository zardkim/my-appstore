import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """Email sender using SMTP"""

    @staticmethod
    def send_invitation_email(to_email: str, invitation_code: str) -> bool:
        """
        Send invitation email with registration link

        Args:
            to_email: Recipient email address
            invitation_code: Invitation code for registration

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if SMTP is configured
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                logger.warning("SMTP not configured. Email not sent.")
                return False

            # Create invitation link
            invitation_link = f"{settings.APP_URL}/register?code={invitation_code}"

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'{settings.SMTP_FROM_NAME} 초대장'
            msg['From'] = f'{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>'
            msg['To'] = to_email

            # HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f9fafb;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .code-box {{
                        background: #e5e7eb;
                        padding: 15px;
                        border-radius: 8px;
                        font-family: monospace;
                        font-size: 14px;
                        word-break: break-all;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        color: #6b7280;
                        font-size: 12px;
                        margin-top: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 {settings.SMTP_FROM_NAME} 초대장</h1>
                </div>
                <div class="content">
                    <p>안녕하세요!</p>
                    <p><strong>{settings.SMTP_FROM_NAME}</strong>에 초대되었습니다.</p>
                    <p>아래 버튼을 클릭하여 회원가입을 완료해주세요.</p>

                    <div style="text-align: center;">
                        <a href="{invitation_link}" class="button">회원가입 하기</a>
                    </div>

                    <p>또는 아래 초대 코드를 복사하여 회원가입 페이지에서 사용하실 수 있습니다:</p>
                    <div class="code-box">{invitation_code}</div>

                    <p><small>* 이 초대장은 7일간 유효합니다.</small></p>
                    <p><small>* 한 번만 사용 가능합니다.</small></p>
                </div>
                <div class="footer">
                    <p>이 이메일은 {settings.SMTP_FROM_NAME}에서 자동으로 발송되었습니다.</p>
                </div>
            </body>
            </html>
            """

            # Plain text alternative
            text_body = f"""
            {settings.SMTP_FROM_NAME} 초대장

            안녕하세요!

            {settings.SMTP_FROM_NAME}에 초대되었습니다.

            아래 링크를 클릭하여 회원가입을 완료해주세요:
            {invitation_link}

            또는 아래 초대 코드를 회원가입 페이지에서 입력하세요:
            {invitation_code}

            * 이 초대장은 7일간 유효합니다.
            * 한 번만 사용 가능합니다.

            ---
            이 이메일은 {settings.SMTP_FROM_NAME}에서 자동으로 발송되었습니다.
            """

            # Attach parts
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Invitation email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send invitation email to {to_email}: {str(e)}")
            return False


# Singleton instance
email_sender = EmailSender()

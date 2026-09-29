import os
import smtplib
import logging
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

logger = logging.getLogger("smartprep_email")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

def _send_email_smtp(to_email, subject, plain_text, html_text):
    """
    Internal helper to dispatch email via SMTP.
    Returns True if sent, False otherwise.
    Never throws an unhandled exception.
    """
    mail_server = getattr(Config, "MAIL_SERVER", os.getenv("MAIL_SERVER", "smtp.gmail.com"))
    mail_port = int(getattr(Config, "MAIL_PORT", os.getenv("MAIL_PORT", 587)))
    mail_use_tls = getattr(Config, "MAIL_USE_TLS", os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "yes"))
    mail_use_ssl = getattr(Config, "MAIL_USE_SSL", os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "yes"))
    mail_username = getattr(Config, "MAIL_USERNAME", os.getenv("MAIL_USERNAME", ""))
    mail_password = getattr(Config, "MAIL_PASSWORD", os.getenv("MAIL_PASSWORD", ""))
    sender = getattr(Config, "MAIL_DEFAULT_SENDER", os.getenv("MAIL_DEFAULT_SENDER", mail_username or "SmartPrep <noreply@smartprep.com>"))

    # Log to console for development/test visibility
    logger.info(f"[EMAIL SERVICE] Preparing email to: {to_email} | Subject: {subject}")

    if not mail_username or not mail_password:
        logger.warning(f"[EMAIL SERVICE NOTICE] MAIL_USERNAME or MAIL_PASSWORD not configured. "
                       f"Email to '{to_email}' logged to server console.")
        print(f"\n--- [SMARTPREP EMAIL SIMULATION] ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{plain_text}")
        print(f"------------------------------------\n")
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to_email

        part_plain = MIMEText(plain_text, "plain", "utf-8")
        part_html = MIMEText(html_text, "html", "utf-8")
        msg.attach(part_plain)
        msg.attach(part_html)

        if mail_use_ssl:
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=10)
        else:
            server = smtplib.SMTP(mail_server, mail_port, timeout=10)
            if mail_use_tls:
                server.starttls()

        server.login(mail_username, mail_password)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()
        logger.info(f"[EMAIL SERVICE SUCCESS] Email delivered to {to_email} with subject '{subject}'.")
        return True
    except Exception as e:
        logger.error(f"[EMAIL SERVICE ERROR] Failed to send email to {to_email}: {str(e)}")
        print(f"[EMAIL SERVICE ERROR] {str(e)}")
        return False


def _send_async(to_email, subject, plain_text, html_text):
    """Spawns a background thread to send email without blocking HTTP responses."""
    t = threading.Thread(target=_send_email_smtp, args=(to_email, subject, plain_text, html_text), daemon=True)
    t.start()


# =====================================================================
# 1. WELCOME EMAIL
# =====================================================================

def send_welcome_email(to_email, student_name, login_url="http://127.0.0.1:5000/login", async_send=True):
    """
    Sends a welcome email upon successful student registration.
    """
    subject = "Welcome to SmartPrep"
    
    plain_text = f"""Hello {student_name},

Welcome to SmartPrep!

Your SmartPrep account has been successfully created.

You can now login and start preparing for competitive exams through mock tests, practice quizzes and performance tracking.

Login to SmartPrep:
{login_url}

Regards,
SmartPrep Team
"""

    html_text = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0B1120; margin: 0; padding: 30px 10px; color: #E2E8F0; }}
  .container {{ max-width: 580px; margin: 0 auto; background: #0F172A; border: 1px solid #1E293B; border-radius: 16px; padding: 35px 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
  .header {{ text-align: center; border-bottom: 1px solid #1E293B; padding-bottom: 20px; margin-bottom: 25px; }}
  .logo {{ font-size: 26px; font-weight: 700; color: #38BDF8; letter-spacing: 0.5px; }}
  .greeting {{ font-size: 18px; font-weight: 600; color: #F8FAFC; margin-bottom: 15px; }}
  .content {{ font-size: 15px; line-height: 1.7; color: #CBD5E1; margin-bottom: 25px; }}
  .btn-box {{ text-align: center; margin: 30px 0; }}
  .btn {{ display: inline-block; background: linear-gradient(90deg, #2563EB, #0EA5E9); color: #FFFFFF !important; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
  .footer {{ border-top: 1px solid #1E293B; padding-top: 20px; font-size: 13px; color: #64748B; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">&#127891; SmartPrep</div>
  </div>
  <div class="greeting">Hello {student_name},</div>
  <div class="content">
    <p>Welcome to <strong>SmartPrep</strong>!</p>
    <p>Your SmartPrep account has been successfully created.</p>
    <p>You can now login and start preparing for competitive exams through structured mock tests, graded practice quizzes, AI performance analytics, and personalized study planning.</p>
  </div>
  <div class="btn-box">
    <a href="{login_url}" class="btn">Login to SmartPrep</a>
  </div>
  <div class="footer">
    <p>Regards,<br><strong>SmartPrep Team</strong></p>
    <p style="margin-top: 10px; font-size: 11px;">Competitive Exam Preparation & Progress Tracking System</p>
  </div>
</div>
</body>
</html>"""

    if async_send:
        _send_async(to_email, subject, plain_text, html_text)
    else:
        return _send_email_smtp(to_email, subject, plain_text, html_text)


# =====================================================================
# 2. PASSWORD RESET EMAIL
# =====================================================================

def send_password_reset_email(to_email, student_name, reset_url, async_send=True):
    """
    Sends a secure password reset link expiring in 30 minutes.
    """
    subject = "SmartPrep - Password Reset"

    plain_text = f"""Hello {student_name},

We received a request to reset your SmartPrep password.

Click the link below to create a new password:
{reset_url}

This link will expire in 30 minutes.

If you did not request this password reset, you can safely ignore this email.

Regards,
SmartPrep Team
"""

    html_text = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0B1120; margin: 0; padding: 30px 10px; color: #E2E8F0; }}
  .container {{ max-width: 580px; margin: 0 auto; background: #0F172A; border: 1px solid #1E293B; border-radius: 16px; padding: 35px 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
  .header {{ text-align: center; border-bottom: 1px solid #1E293B; padding-bottom: 20px; margin-bottom: 25px; }}
  .logo {{ font-size: 26px; font-weight: 700; color: #38BDF8; letter-spacing: 0.5px; }}
  .greeting {{ font-size: 18px; font-weight: 600; color: #F8FAFC; margin-bottom: 15px; }}
  .content {{ font-size: 15px; line-height: 1.7; color: #CBD5E1; margin-bottom: 25px; }}
  .btn-box {{ text-align: center; margin: 30px 0; }}
  .btn {{ display: inline-block; background: linear-gradient(90deg, #2563EB, #0EA5E9); color: #FFFFFF !important; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
  .warning-box {{ background: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 8px; font-size: 13px; color: #FCD34D; margin: 20px 0; }}
  .footer {{ border-top: 1px solid #1E293B; padding-top: 20px; font-size: 13px; color: #64748B; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">&#127891; SmartPrep</div>
  </div>
  <div class="greeting">Hello {student_name},</div>
  <div class="content">
    <p>We received a request to reset your SmartPrep password.</p>
    <p>Click the button below to create a new password.</p>
  </div>
  <div class="btn-box">
    <a href="{reset_url}" class="btn">Reset Password</a>
  </div>
  <div class="warning-box">
    &#9201; <strong>Note:</strong> This link will expire in <strong>30 minutes</strong> and can only be used once.
  </div>
  <div class="content">
    <p style="font-size: 13px; color: #94A3B8;">If you did not request this password reset, you can safely ignore this email. Your existing password will remain secure.</p>
  </div>
  <div class="footer">
    <p>Regards,<br><strong>SmartPrep Team</strong></p>
  </div>
</div>
</body>
</html>"""

    if async_send:
        _send_async(to_email, subject, plain_text, html_text)
    else:
        return _send_email_smtp(to_email, subject, plain_text, html_text)


# =====================================================================
# 3. TEST RESULT EMAIL
# =====================================================================

def send_result_email(to_email, student_name, exam_name, score, total_questions, percentage, correct, wrong, unanswered, test_date, results_url="http://127.0.0.1:5000/results", async_send=True):
    """
    Sends detailed test results after student submits an exam/quiz.
    """
    subject = "SmartPrep - Test Result"

    plain_text = f"""Hello {student_name},

Your SmartPrep test has been completed successfully.

Exam / Practice Quiz:
{exam_name}

Score:
{score} / {total_questions}

Percentage:
{percentage}%

Correct Answers:
{correct}

Wrong Answers:
{wrong}

Unanswered:
{unanswered}

Date:
{test_date}

Login to SmartPrep to view your detailed result and answer review:
{results_url}

Regards,
SmartPrep Team
"""

    html_text = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0B1120; margin: 0; padding: 30px 10px; color: #E2E8F0; }}
  .container {{ max-width: 580px; margin: 0 auto; background: #0F172A; border: 1px solid #1E293B; border-radius: 16px; padding: 35px 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
  .header {{ text-align: center; border-bottom: 1px solid #1E293B; padding-bottom: 20px; margin-bottom: 25px; }}
  .logo {{ font-size: 26px; font-weight: 700; color: #38BDF8; letter-spacing: 0.5px; }}
  .greeting {{ font-size: 18px; font-weight: 600; color: #F8FAFC; margin-bottom: 15px; }}
  .content {{ font-size: 15px; line-height: 1.6; color: #CBD5E1; margin-bottom: 20px; }}
  .result-card {{ background: #131E35; border: 1px solid #1E293B; border-radius: 12px; padding: 20px; margin: 20px 0; }}
  .result-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px; }}
  .result-item:last-child {{ border-bottom: none; }}
  .result-label {{ color: #94A3B8; font-weight: 500; }}
  .result-value {{ color: #F8FAFC; font-weight: 700; }}
  .btn-box {{ text-align: center; margin: 25px 0; }}
  .btn {{ display: inline-block; background: linear-gradient(90deg, #2563EB, #0EA5E9); color: #FFFFFF !important; text-decoration: none; padding: 14px 32px; border-radius: 10px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4); }}
  .footer {{ border-top: 1px solid #1E293B; padding-top: 20px; font-size: 13px; color: #64748B; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">&#127891; SmartPrep</div>
  </div>
  <div class="greeting">Hello {student_name},</div>
  <div class="content">
    <p>Your SmartPrep test has been completed successfully.</p>
  </div>
  <div class="result-card">
    <div class="result-item">
      <span class="result-label">Exam / Practice Quiz:</span>
      <span class="result-value" style="color:#38BDF8;">{exam_name}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Score:</span>
      <span class="result-value">{score} / {total_questions}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Percentage:</span>
      <span class="result-value" style="color:{'#22C55E' if float(percentage)>=70 else '#38BDF8' if float(percentage)>=50 else '#EF4444'};">{percentage}%</span>
    </div>
    <div class="result-item">
      <span class="result-label">Correct Answers:</span>
      <span class="result-value" style="color:#22C55E;">{correct}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Wrong Answers:</span>
      <span class="result-value" style="color:#EF4444;">{wrong}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Unanswered:</span>
      <span class="result-value" style="color:#F59E0B;">{unanswered}</span>
    </div>
    <div class="result-item">
      <span class="result-label">Date:</span>
      <span class="result-value">{test_date}</span>
    </div>
  </div>
  <div class="content" style="text-align:center;">
    <p>Login to SmartPrep to view your detailed result and answer review.</p>
  </div>
  <div class="btn-box">
    <a href="{results_url}" class="btn">View My Results</a>
  </div>
  <div class="footer">
    <p>Regards,<br><strong>SmartPrep Team</strong></p>
  </div>
</div>
</body>
</html>"""

    if async_send:
        _send_async(to_email, subject, plain_text, html_text)
    else:
        return _send_email_smtp(to_email, subject, plain_text, html_text)

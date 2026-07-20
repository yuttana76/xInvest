"""
Email utility functions for xInvest
ส่งอีเมล HTML template สำหรับ OTP และ Password Reset
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_otp_email(user_email: str, username: str, otp_code: str, otp_ref: str) -> bool:
    """
    ส่ง OTP email ด้วย HTML template แบบมืออาชีพ
    
    Returns:
        True ถ้าส่งสำเร็จ, False ถ้า error
    """
    subject = "Your xInvest Verification Code"

    context = {
        "otp_code": otp_code,
        "otp_ref": otp_ref,
    }

    html_message = render_to_string("users/emails/otp_email.html", context)
    plain_message = (
        f"Your xInvest verification code: {otp_code}\n"
        f"Reference: {otp_ref}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"xInvest Team"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send OTP email to {user_email}: {e}")
        return False


def send_password_reset_email(user_email: str, username: str, reset_link: str) -> bool:
    """
    ส่ง Password Reset email ด้วย HTML template แบบมืออาชีพ
    
    Returns:
        True ถ้าส่งสำเร็จ, False ถ้า error
    """
    subject = "Password Reset Request - xInvest"

    context = {
        "reset_link": reset_link,
    }

    html_message = render_to_string("users/emails/password_reset_email.html", context)
    plain_message = (
        f"We received a request to reset the password for your xInvest account.\n\n"
        f"Click the link below to set a new password:\n\n"
        f"{reset_link}\n\n"
        f"This link expires in 24 hours.\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"xInvest Team"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send password reset email to {user_email}: {e}")
        return False


def send_welcome_email(user_email: str, username: str) -> bool:
    """
    ส่งอีเมลต้อนรับเมื่อลงทะเบียนและยืนยันตัวตนสำเร็จ
    
    Returns:
        True ถ้าส่งสำเร็จ, False ถ้า error
    """
    subject = "Welcome to xInvest!"

    context = {
        "username": username,
    }

    html_message = render_to_string("users/emails/welcome_email.html", context)
    plain_message = (
        f"Welcome to xInvest, {username}!\n\n"
        f"Thank you for verifying your email. Your account is now fully active, and you are ready to start managing your investments on our platform.\n\n"
        f"If you have any questions or need support, contact us at support@xinvest.com\n\n"
        f"xInvest Team"
    )

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send welcome email to {user_email}: {e}")
        return False

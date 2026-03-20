"""
Celery Tasks — Email Queue สำหรับ xInvest
==========================================

แทนที่การส่งอีเมลแบบ synchronous (รอ SMTP ตอบกลับก่อน)
ด้วยการส่งผ่าน Celery Queue ทำให้:
  1. API ตอบกลับ user ทันที ไม่ต้องรอ SMTP
  2. มี retry อัตโนมัติ ถ้า Gmail/SMTP ล่มชั่วคราว
  3. ลด latency ของ Login API ลงอย่างเห็นได้ชัด

การทำงาน:
  views.py → .delay() → Redis Queue → Celery Worker → SMTP → Gmail → User
"""

import logging
from celery import shared_task
from .email_utils import send_otp_email, send_password_reset_email

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,          # ลองซ้ำสูงสุด 3 ครั้ง
    default_retry_delay=30, # รอ 30 วินาทีก่อนลองใหม่
    name="users.send_otp_email",
)
def task_send_otp_email(self, user_email: str, username: str, otp_code: str, otp_ref: str):
    """
    Celery Task: ส่ง OTP email ผ่าน queue

    Args:
        user_email: อีเมลผู้รับ
        username:   ชื่อผู้ใช้ (สำหรับ logging)
        otp_code:   รหัส OTP 6 หลัก
        otp_ref:    รหัสอ้างอิง

    Retry Policy:
        ถ้าส่งไม่สำเร็จ → รอ 30 วิ → ลองใหม่ (สูงสุด 3 ครั้ง)
    """
    logger.info(f"[EMAIL QUEUE] Sending OTP email to {user_email} (ref: {otp_ref})")
    try:
        success = send_otp_email(
            user_email=user_email,
            username=username,
            otp_code=otp_code,
            otp_ref=otp_ref,
        )
        if not success:
            raise Exception("send_otp_email returned False")
        logger.info(f"[EMAIL QUEUE] OTP email sent successfully to {user_email}")
    except Exception as exc:
        logger.warning(
            f"[EMAIL QUEUE] OTP email failed for {user_email} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    name="users.send_password_reset_email",
)
def task_send_password_reset_email(self, user_email: str, username: str, reset_link: str):
    """
    Celery Task: ส่ง Password Reset email ผ่าน queue

    Args:
        user_email:  อีเมลผู้รับ
        username:    ชื่อผู้ใช้ (สำหรับ logging)
        reset_link:  URL สำหรับรีเซ็ตรหัสผ่าน

    Retry Policy:
        ถ้าส่งไม่สำเร็จ → รอ 30 วิ → ลองใหม่ (สูงสุด 3 ครั้ง)
    """
    logger.info(f"[EMAIL QUEUE] Sending password reset email to {user_email}")
    try:
        success = send_password_reset_email(
            user_email=user_email,
            username=username,
            reset_link=reset_link,
        )
        if not success:
            raise Exception("send_password_reset_email returned False")
        logger.info(f"[EMAIL QUEUE] Password reset email sent successfully to {user_email}")
    except Exception as exc:
        logger.warning(
            f"[EMAIL QUEUE] Password reset email failed for {user_email} "
            f"(attempt {self.request.retries + 1}/{self.max_retries + 1}): {exc}"
        )
        raise self.retry(exc=exc)

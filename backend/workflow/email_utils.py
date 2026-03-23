import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User, Group
from .models import Request
from django.utils import timezone

logger = logging.getLogger(__name__)

def get_frontend_url(request_id):
    # ในสภาวะจริงควรดึงจาก settings
    base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    return f"{base_url}/workflow/requests/{request_id}"

def send_workflow_action_required_email(request_obj: Request, group: Group = None, specific_user_id: int = None) -> bool:
    """
    ส่งอีเมลแจ้งเตือนไปยังสมาชิกทุกคนในกลุ่มที่ต้องอนุมัติ หรือส่งหาบุคคลที่ระบุ
    """
    subject = f"Action Required: {request_obj.title} (Workflow)"
    
    recipient_list = []
    
    if specific_user_id:
        try:
            user = User.objects.get(id=specific_user_id, is_active=True)
            if user.email:
                recipient_list = [user.email]
                logger.info(f"Sending email to specific user: {user.username} ({user.email})")
            else:
                logger.warning(f"Specific user {user.username} has no email")
        except User.DoesNotExist:
            logger.error(f"Specific user ID {specific_user_id} not found")
            return False
    elif group:
        # ดึงอีเมลของสมาชิกในกลุ่ม
        users_in_group = group.user_set.filter(is_active=True)
        logger.info(f"Found {users_in_group.count()} active users in group {group.name}")
        
        recipient_list = list(users_in_group.values_list('email', flat=True))
        recipient_list = [email for email in recipient_list if email] # กรองอีเมลว่างออก
        
        if not recipient_list:
            logger.warning(f"No active users with valid email found in group {group.name} for request {request_obj.id}")
            return False
    else:
        logger.error("Neither group nor specific_user_id provided for notification")
        return False

    if not recipient_list:
        return False

    logger.info(f"Sending email to recipients: {recipient_list}")

    context = {
        "request_title": request_obj.title,
        "creator_name": request_obj.creator.get_full_name() or request_obj.creator.username,
        "workflow_name": request_obj.workflow.name,
        "current_step_name": request_obj.get_current_step_info().step_name if request_obj.get_current_step_info() else "N/A",
        "request_description": request_obj.description,
        "action_url": get_frontend_url(request_obj.id),
        "current_year": timezone.now().year,
    }

    html_content = render_to_string("workflow/emails/action_required_email.html", context)
    text_content = f"Action Required: {request_obj.title}\nA new workflow request is waiting for your review.\nLink: {context['action_url']}"

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send action required email for request {request_obj.id}: {e}")
        return False

def send_workflow_status_update_email(request_obj: Request, comment: str = "", action_by_name: str = "") -> bool:
    """
    ส่งอีเมลแจ้งเตือนถึงผู้สร้างคำขอ เมื่อสถานะเปลี่ยนไป (Completed, Returned, Rejected)
    """
    subject = f"Request Status Update: {request_obj.title} ({request_obj.status})"
    
    if not request_obj.creator.email:
        logger.warning(f"Creator {request_obj.creator.username} has no email for request {request_obj.id}")
        return False

    context = {
        "status": request_obj.status,
        "request_title": request_obj.title,
        "request_description": request_obj.description,
        "action_by": action_by_name,
        "comment": comment,
        "action_url": get_frontend_url(request_obj.id),
        "current_year": timezone.now().year,
    }

    html_content = render_to_string("workflow/emails/status_update_email.html", context)
    text_content = f"Status Update: {request_obj.title} is now {request_obj.status}.\nComment: {comment}\nLink: {context['action_url']}"

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request_obj.creator.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send status update email for request {request_obj.id}: {e}")
        return False

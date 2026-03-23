import logging
from celery import shared_task
from django.contrib.auth.models import Group
from .models import Request
from .email_utils import send_workflow_action_required_email, send_workflow_status_update_email

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def task_send_workflow_action_required_email(self, request_id: int, group_id: int = None, user_id: int = None):
    try:
        request_obj = Request.objects.get(id=request_id)
        group = None
        if group_id:
            group = Group.objects.get(id=group_id)
        
        success = send_workflow_action_required_email(request_obj, group, specific_user_id=user_id)
        if not success:
            logger.warning(f"Notification not sent for request {request_id}")
    except Request.DoesNotExist:
        logger.error(f"Request {request_id} does not exist for email task")
    except Group.DoesNotExist:
        logger.error(f"Group {group_id} does not exist for email task")
    except Request.DoesNotExist:
        logger.error(f"Request {request_id} does not exist for email task")
    except Group.DoesNotExist:
        logger.error(f"Group {group_id} does not exist for email task")
    except Exception as exc:
        logger.warning(f"Retrying email task for request {request_id}: {exc}")
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def task_send_workflow_status_update_email(self, request_id: int, comment: str, action_by_name: str):
    try:
        request_obj = Request.objects.get(id=request_id)
        
        success = send_workflow_status_update_email(request_obj, comment, action_by_name)
        if not success:
            raise Exception("send_workflow_status_update_email returned False")
    except Request.DoesNotExist:
        logger.error(f"Request {request_id} does not exist for email task")
    except Exception as exc:
        logger.warning(f"Retrying email task for request {request_id}: {exc}")
        raise self.retry(exc=exc)

import logging
from urllib.parse import urlencode
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import WorkflowConfig, WorkflowStep, Request, ApprovalLog, RequestFile, RequestSubject
from .serializers import (
    WorkflowConfigSerializer, WorkflowStepSerializer, RequestSerializer, ApprovalLogSerializer,
    RequestSubjectSerializer
)
from .tasks import (
    dispatch_workflow_action_required_email,
    dispatch_workflow_status_update_email,
)

# pyrefly: ignore [missing-import]
from django.db import models

logger = logging.getLogger(__name__)
User = get_user_model()

from rest_framework.pagination import PageNumberPagination

class OptionalPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)


class WorkflowConfigViewSet(viewsets.ModelViewSet):
    queryset = WorkflowConfig.objects.all()
    serializer_class = WorkflowConfigSerializer
    permission_classes = [permissions.IsAuthenticated]


class RequestSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only list of active request subjects.
    Filter by workflow: /api/v1/workflow/subjects/?workflow=<id>
    """
    serializer_class = RequestSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = RequestSubject.objects.filter(is_active=True)
        workflow_id = self.request.query_params.get('workflow')
        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        return queryset

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ('approve_via_email', 'decide_via_email'):
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # Determine the creator's department if available
        user_profile = getattr(self.request.user, 'profile', None)
        department_name = user_profile.department.name if user_profile and user_profile.department else None

        # Set the creator and initial status
        # Step 1 is the starting point
        request_obj = serializer.save(
            creator=self.request.user, 
            create_department=department_name,
            status='PENDING', 
            current_step_number=1
        )
        
        # Log the initial creation
        current_step = request_obj.get_current_step_info()
        ApprovalLog.objects.create(
            request=request_obj,
            approver=self.request.user,
            step_number=0,
            step_name="Creation",
            action="RESUBMIT", # Using RESUBMIT as starting action for now
            comment="Request created and submitted for approval."
        )

        # Notify first step approvers
        if current_step:
            if current_step.is_department_manager:
                manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
                if manager:
                    dispatch_workflow_action_required_email(request_obj.id, user_id=manager.id)
                else:
                    logger.warning(f"No department manager found for creator {request_obj.creator.username}")
            elif current_step.required_group:
                dispatch_workflow_action_required_email(request_obj.id, group_id=current_step.required_group.id)
        else:
            logger.warning(f"No current step found for request {request_obj.id} at step 1")

    def _build_email_redirect_url(self, request_obj, *, success=None, error=None):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        params = {}
        if success:
            params['email_action'] = success
        if error:
            params['email_error'] = error
        query_string = urlencode(params)
        path = f"/workflow/requests/{request_obj.id}"
        return f"{frontend_url}{path}" if not query_string else f"{frontend_url}{path}?{query_string}"

    def _resolve_email_action_token(self, request_obj, token, expected_action='approve'):
        """
        Validate a signed email-action token end to end.
        Returns (approver, current_step) on success, or (None, error_code) on failure.
        Re-checking authorization here (rather than trusting the token payload) means a
        forged/tampered token is rejected by the signature, and a stale-but-validly-signed
        token (e.g. request has since moved to another step, or the approver lost access)
        is rejected by the live checks below.
        """
        if not token:
            return None, 'missing_token'

        signer = TimestampSigner(salt='workflow-approval-email')
        try:
            payload = signer.unsign_object(token, max_age=60 * 60 * 24 * 7)
        except (BadSignature, SignatureExpired):
            return None, 'invalid_token'

        if payload.get('request_id') != request_obj.id or payload.get('action') != expected_action:
            return None, 'invalid_token'

        # The token is bound to the step it was issued for. If the request has since
        # advanced (or been sent back), the link is stale and must not be honored -
        # this also makes each token effectively single-use for its step.
        if payload.get('step_number') != request_obj.current_step_number:
            return None, 'stale_token'

        approver_id = payload.get('user_id')
        if not approver_id:
            return None, 'invalid_token'

        try:
            approver = User.objects.get(id=approver_id, is_active=True)
        except User.DoesNotExist:
            return None, 'invalid_token'

        current_step = request_obj.get_current_step_info()
        if not current_step:
            return None, 'no_current_step'

        is_authorized = False
        if current_step.is_department_manager:
            manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
            if manager and approver == manager:
                is_authorized = True

        if not is_authorized and current_step.required_group:
            if approver.groups.filter(id=current_step.required_group.id).exists():
                is_authorized = True

        if not is_authorized:
            return None, 'not_authorized'

        return approver, current_step

    @action(detail=True, methods=['get'])
    def approve_via_email(self, request, pk=None):
        """
        GET is intentionally side-effect free: it only validates the token and renders a
        decision page where the approver picks Approve / Reject / Return and can leave a
        comment. This protects against corporate email/link-scanners that prefetch links
        in emails, which would otherwise silently trigger a state change. The actual
        mutation happens in decide_via_email (POST) below.
        """
        request_obj = self.get_object()
        token = request.query_params.get('token', '')
        approver, result = self._resolve_email_action_token(request_obj, token, expected_action='review')

        if approver is None:
            return redirect(self._build_email_redirect_url(request_obj, error=result))

        current_step = result
        return render(request, 'workflow/email_decision.html', {
            'request_obj': request_obj,
            'approver': approver,
            'current_step': current_step,
            'token': token,
            'FRONTEND_URL': getattr(settings, 'FRONTEND_URL', 'http://localhost:3000'),
        })

    # Maps the decision chosen on the email decision page to the ApprovalLog action code
    # and the past-tense label used in the frontend redirect / success message.
    _EMAIL_DECISION_LOG_ACTIONS = {'approve': 'APPROVE', 'reject': 'REJECT', 'return': 'RETURN'}
    _EMAIL_DECISION_SUCCESS_LABELS = {'approve': 'approved', 'reject': 'rejected', 'return': 'returned'}

    @action(detail=True, methods=['post'])
    def decide_via_email(self, request, pk=None):
        token = request.data.get('token') or request.query_params.get('token', '')
        decision = request.data.get('decision', '')
        comment = (request.data.get('comment') or '').strip()

        log_action = self._EMAIL_DECISION_LOG_ACTIONS.get(decision)
        if not log_action:
            return Response({"error": "Invalid decision."}, status=status.HTTP_400_BAD_REQUEST)

        # select_for_update() locks the Request row for the duration of the transaction,
        # so a double-click / retried form submit that arrives while the first request is
        # still in flight blocks here instead of racing past the "already logged" check
        # below - without this, both requests could read "not yet actioned", both create
        # an ApprovalLog, and both dispatch a notification.
        with transaction.atomic():
            try:
                request_obj = Request.objects.select_for_update().get(pk=pk)
            except Request.DoesNotExist:
                return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

            if decision == 'return' and not comment:
                return redirect(self._build_email_redirect_url(request_obj, error='comment_required'))

            approver, result = self._resolve_email_action_token(request_obj, token, expected_action='review')

            if approver is None:
                return redirect(self._build_email_redirect_url(request_obj, error=result))

            current_step = result

            already_logged = ApprovalLog.objects.filter(
                request=request_obj,
                step_number=request_obj.current_step_number,
                approver=approver,
                action=log_action,
            ).exists()
            if already_logged:
                return redirect(self._build_email_redirect_url(request_obj, error='already_actioned'))

            ApprovalLog.objects.create(
                request=request_obj,
                approver=approver,
                step_number=request_obj.current_step_number,
                step_name=current_step.step_name,
                action=log_action,
                comment=comment or f'{decision.capitalize()}d via email link',
            )

            if decision == 'approve':
                next_step_number = request_obj.current_step_number + 1
                has_next_step = request_obj.workflow.steps.filter(step_number=next_step_number).exists()
                if has_next_step:
                    request_obj.current_step_number = next_step_number
                    request_obj.status = 'PENDING'
                else:
                    request_obj.status = 'APPROVED'
            elif decision == 'reject':
                request_obj.status = 'REJECTED'
            else:  # return
                request_obj.status = 'RETURNED'

            request_obj.save()

            # Notifications are dispatched only once the transaction actually commits,
            # so a rolled-back request never fires an email for a state change that didn't happen.
            transaction.on_commit(
                lambda: self._notify_after_email_decision(request_obj, approver, decision, comment)
            )

        return redirect(self._build_email_redirect_url(
            request_obj, success=self._EMAIL_DECISION_SUCCESS_LABELS[decision]
        ))

    def _notify_after_email_decision(self, request_obj, approver, decision, comment):
        approver_name = approver.get_full_name() or approver.username

        if decision == 'approve' and request_obj.status == 'PENDING':
            next_step = request_obj.get_current_step_info()
            if next_step:
                if next_step.is_department_manager:
                    manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
                    if manager:
                        dispatch_workflow_action_required_email(request_obj.id, user_id=manager.id)
                elif next_step.required_group:
                    dispatch_workflow_action_required_email(request_obj.id, group_id=next_step.required_group.id)
        else:
            # Final decision on the request (APPROVED at the last step, REJECTED, or
            # RETURNED) - notify the creator.
            dispatch_workflow_status_update_email(
                request_obj.id,
                comment or f'{decision.capitalize()}d via email link',
                approver_name,
            )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        request_obj = self.get_object()
        current_step = request_obj.get_current_step_info()

        if not current_step:
            return Response({"error": "No current step found."}, status=status.HTTP_400_BAD_REQUEST)

        # Check permission: User must be in the required group OR be the department manager if flag is set
        is_authorized = False
        if current_step.is_department_manager:
            manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
            if manager and request.user == manager:
                is_authorized = True
        
        if not is_authorized and current_step.required_group:
            if request.user.groups.filter(id=current_step.required_group.id).exists():
                is_authorized = True

        if not is_authorized:
            return Response({"error": "You do not have permission to approve this step."}, status=status.HTTP_403_FORBIDDEN)

        comment = request.data.get('comment', '')
        
        # Log the approval
        ApprovalLog.objects.create(
            request=request_obj,
            approver=request.user,
            step_number=request_obj.current_step_number,
            step_name=current_step.step_name,
            action='APPROVE',
            comment=comment
        )

        # Handle optional file upload during approval
        uploaded_files = request.FILES.getlist('uploaded_files')
        for file in uploaded_files:
            RequestFile.objects.create(request=request_obj, file=file)

        # Move to next step
        next_step_number = request_obj.current_step_number + 1
        has_next_step = request_obj.workflow.steps.filter(step_number=next_step_number).exists()

        if has_next_step:
            request_obj.current_step_number = next_step_number
            request_obj.status = 'PENDING'
        else:
            # Last step completed
            request_obj.status = 'APPROVED'
            # In some cases, we might set it to IN_PROGRESS if execution starts immediately
        
        request_obj.save()

        # Notify next step approvers if still pending
        if request_obj.status == 'PENDING':
            next_step = request_obj.get_current_step_info()
            if next_step:
                if next_step.is_department_manager:
                    manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
                    if manager:
                        dispatch_workflow_action_required_email(request_obj.id, user_id=manager.id)
                elif next_step.required_group:
                    dispatch_workflow_action_required_email(request_obj.id, group_id=next_step.required_group.id)
        elif request_obj.status == 'APPROVED':
            # Notify creator that it's fully approved
            dispatch_workflow_status_update_email(
                request_obj.id, 
                comment, 
                request.user.get_full_name() or request.user.username
            )

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def return_to_creator(self, request, pk=None):
        request_obj = self.get_object()
        current_step = request_obj.get_current_step_info()

        # Check permission: User must be in required group OR be department manager
        is_authorized = False
        if current_step.is_department_manager:
            manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
            if manager and request.user == manager:
                is_authorized = True
        
        if not is_authorized and current_step.required_group:
            if request.user.groups.filter(id=current_step.required_group.id).exists():
                is_authorized = True

        if not is_authorized:
            return Response({"error": "You do not have permission to return this request."}, status=status.HTTP_403_FORBIDDEN)

        comment = request.data.get('comment', '')
        if not comment:
            return Response({"error": "Comment is required when returning a request."}, status=status.HTTP_400_BAD_REQUEST)

        # Log the action
        ApprovalLog.objects.create(
            request=request_obj,
            approver=request.user,
            step_number=request_obj.current_step_number,
            step_name=current_step.step_name,
            action='RETURN',
            comment=comment
        )

        request_obj.status = 'RETURNED'
        request_obj.save()

        # Notify creator
        dispatch_workflow_status_update_email(
            request_obj.id, 
            comment, 
            request.user.get_full_name() or request.user.username
        )

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        request_obj = self.get_object()
        current_step = request_obj.get_current_step_info()

        # Check permission: User must be in required group OR be department manager
        is_authorized = False
        if current_step.is_department_manager:
            manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
            if manager and request.user == manager:
                is_authorized = True
        
        if not is_authorized and current_step.required_group:
            if request.user.groups.filter(id=current_step.required_group.id).exists():
                is_authorized = True

        if not is_authorized:
            return Response({"error": "You do not have permission to reject this request."}, status=status.HTTP_403_FORBIDDEN)

        comment = request.data.get('comment', '')
        
        # Log the action
        ApprovalLog.objects.create(
            request=request_obj,
            approver=request.user,
            step_number=request_obj.current_step_number,
            step_name=current_step.step_name,
            action='REJECT',
            comment=comment
        )

        request_obj.status = 'REJECTED'
        request_obj.save()

        # Notify creator
        dispatch_workflow_status_update_email(
            request_obj.id, 
            comment, 
            request.user.get_full_name() or request.user.username
        )

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        request_obj = self.get_object()
        
        # Only APPROVED or IN_PROGRESS can be completed
        if request_obj.status not in ['APPROVED', 'IN_PROGRESS']:
            return Response({"error": "Request must be Approved or In Progress to be completed."}, status=status.HTTP_400_BAD_REQUEST)

        comment = request.data.get('comment', '')
        
        # Log the completion
        ApprovalLog.objects.create(
            request=request_obj,
            approver=request.user,
            step_number=request_obj.current_step_number,
            step_name="Final Execution",
            action='COMPLETE',
            comment=comment
        )

        request_obj.status = 'COMPLETED'
        request_obj.completed_at = timezone.now()
        request_obj.assigned_to = request.user
        
        # Optionally handle rating if provided during completion
        rating = request.data.get('rating')
        if rating is not None:
            try:
                rating_val = int(rating)
                if 1 <= rating_val <= 5:
                    request_obj.rating = rating_val
                    request_obj.rating_comment = request.data.get('rating_comment', request.data.get('comment', ''))
                else:
                    logger.warning(f"Invalid rating value {rating} ignored during completion")
            except (ValueError, TypeError):
                logger.warning(f"Non-integer rating value {rating} ignored during completion")

        request_obj.save()

        # Notify creator
        dispatch_workflow_status_update_email(
            request_obj.id, 
            comment, 
            request.user.get_full_name() or request.user.username
        )

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def resubmit(self, request, pk=None):
        request_obj = self.get_object()

        # Only the creator can resubmit
        if request_obj.creator != request.user:
            return Response({"error": "Only the creator can resubmit the request."}, status=status.HTTP_403_FORBIDDEN)

        # Only RETURNED or DRAFT requests can be resubmitted
        if request_obj.status not in ['RETURNED', 'DRAFT']:
            return Response({"error": "Only Returned or Draft requests can be resubmitted."}, status=status.HTTP_400_BAD_REQUEST)

        # Allow updating data and files during resubmit
        # Since RequestSerializer handles file creation in its create() method, 
        # but we are doing update here, we should handle files in perform_update logic or in serializer update()
        # For simplicity, we use the serializer update logic
        serializer = self.get_serializer(request_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(status='PENDING')

        # Handle uploaded files manually if the serializer update doesn't handle it
        uploaded_files = request.FILES.getlist('uploaded_files')
        for file in uploaded_files:
            from .models import RequestFile
            RequestFile.objects.create(request=request_obj, file=file)

        comment = request.data.get('comment', 'Resubmitted after revision.')

        # Log the resubmission
        current_step = request_obj.get_current_step_info()
        ApprovalLog.objects.create(
            request=request_obj,
            approver=request.user,
            step_number=request_obj.current_step_number,
            step_name=current_step.step_name if current_step else "Resubmission",
            action='RESUBMIT',
            comment=comment
        )

        # Notify first step approvers again
        current_step = request_obj.get_current_step_info()
        if current_step:
            if current_step.is_department_manager:
                manager = getattr(request_obj.creator.profile.department, 'manager', None) if hasattr(request_obj.creator, 'profile') and request_obj.creator.profile.department else None
                if manager:
                    dispatch_workflow_action_required_email(request_obj.id, user_id=manager.id)
            elif current_step.required_group:
                dispatch_workflow_action_required_email(request_obj.id, group_id=current_step.required_group.id)

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        request_obj = self.get_object()

        # Only the creator can rate
        if request_obj.creator != request.user:
            return Response({"error": "Only the creator can rate this request."}, status=status.HTTP_403_FORBIDDEN)

        # Only COMPLETED requests can be rated
        if request_obj.status != 'COMPLETED':
            return Response({"error": "Only completed requests can be rated."}, status=status.HTTP_400_BAD_REQUEST)

        rating = request.data.get('rating')
        if rating is None or not (1 <= int(rating) <= 5):
            return Response({"error": "Rating must be an integer between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)

        request_obj.rating = int(rating)
        request_obj.rating_comment = request.data.get('rating_comment', '')
        request_obj.save()

        return Response(RequestSerializer(request_obj).data)

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        request_obj = self.get_object()

        if request_obj.workflow.category != 'IT':
            return Response(
                {"error": "PDF export is only available for IT Request workflows."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .pdf_service import generate_it_request_pdf
        buffer = generate_it_request_pdf(request_obj, exported_by=request.user)
        filename = f"{request_obj.req_code or request_obj.id}_IT_Request.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename)

    @action(detail=False, methods=['get'])
    def waiting_approval(self, request):
        user_groups = request.user.groups.all()
        
        # Find steps that require one of the user's groups
        relevant_steps = WorkflowStep.objects.filter(required_group__in=user_groups)
        valid_combinations = relevant_steps.values_list('workflow_id', 'step_number')
        # Build filter conditions using Q objects
        from django.db.models import Q
        query = Q()
        
        # 1. Groups-based approval
        if valid_combinations:
            for w_id, s_num in valid_combinations:
                query |= Q(workflow_id=w_id, current_step_number=s_num)

        # 2. Department Manager-based approval
        # Find requests where current step 'is_department_manager' is True 
        # AND the creator's department manager is the current user
        # This requires checking the WorkflowStep property and Request creator's department
        query_mgr = Q(
            workflow__steps__step_number=models.F('current_step_number'),
            workflow__steps__is_department_manager=True,
            creator__profile__department__manager=request.user
        )
        # Combine filters: if valid_combinations exists, use both; otherwise just manager query
        if valid_combinations:
            filter_query = query | query_mgr
        else:
            filter_query = query_mgr
                
        queryset = self.queryset.filter(filter_query, status='PENDING').distinct()
                
        # Apply pagination if needed (optional but good practice)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        
        queryset = self.queryset.filter(creator=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

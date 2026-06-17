import logging
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import WorkflowConfig, WorkflowStep, Request, ApprovalLog, RequestFile
from .serializers import (
    WorkflowConfigSerializer, WorkflowStepSerializer, RequestSerializer, ApprovalLogSerializer
)
from .tasks import task_send_workflow_action_required_email, task_send_workflow_status_update_email

# pyrefly: ignore [missing-import]
from django.db import models

logger = logging.getLogger(__name__)

class WorkflowConfigViewSet(viewsets.ModelViewSet):
    queryset = WorkflowConfig.objects.all()
    serializer_class = WorkflowConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

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
                    task_send_workflow_action_required_email.delay(request_obj.id, user_id=manager.id)
                else:
                    logger.warning(f"No department manager found for creator {request_obj.creator.username}")
            elif current_step.required_group:
                task_send_workflow_action_required_email.delay(request_obj.id, group_id=current_step.required_group.id)
        else:
            logger.warning(f"No current step found for request {request_obj.id} at step 1")

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
                        task_send_workflow_action_required_email.delay(request_obj.id, user_id=manager.id)
                elif next_step.required_group:
                    task_send_workflow_action_required_email.delay(request_obj.id, group_id=next_step.required_group.id)
        elif request_obj.status == 'APPROVED':
            # Notify creator that it's fully approved
            task_send_workflow_status_update_email.delay(
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
        task_send_workflow_status_update_email.delay(
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
        task_send_workflow_status_update_email.delay(
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
        task_send_workflow_status_update_email.delay(
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
                    task_send_workflow_action_required_email.delay(request_obj.id, user_id=manager.id)
            elif current_step.required_group:
                task_send_workflow_action_required_email.delay(request_obj.id, group_id=current_step.required_group.id)

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

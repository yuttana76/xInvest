from unittest.mock import patch
from urllib.parse import unquote

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase

from .admin import RequestAdmin
from .email_utils import build_workflow_action_url
from .models import Request, WorkflowConfig, WorkflowStep


class RequestAdminResendApprovalEmailTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='admin', email='admin@example.com', password='secret', is_staff=True, is_superuser=True)
        self.creator = get_user_model().objects.create_user(username='creator', email='creator@example.com', password='secret')
        self.group = Group.objects.create(name='Approvers')
        self.workflow = WorkflowConfig.objects.create(name='IT Change', category='IT')
        self.step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_number=1,
            step_name='Approver',
            required_group=self.group,
        )
        self.request_obj = Request.objects.create(
            title='New system access',
            workflow=self.workflow,
            creator=self.creator,
            status='PENDING',
            current_step_number=1,
        )

    def test_resend_approval_email_sends_to_current_step_group(self):
        admin_instance = RequestAdmin(Request, admin.site)
        request = RequestFactory().get('/admin/workflow/request/')
        request.user = self.user

        with patch('workflow.admin.dispatch_workflow_action_required_email') as mocked_dispatch:
            with patch.object(RequestAdmin, 'message_user'):
                admin_instance.resend_approval_email(request, Request.objects.filter(pk=self.request_obj.pk))

        mocked_dispatch.assert_called_once_with(self.request_obj.id, group_id=self.group.id)

    def _extract_token(self, token_url):
        return unquote(token_url.split('token=', 1)[1])

    def _decide_url(self, request_obj=None):
        return f'/api/v1/workflow/requests/{(request_obj or self.request_obj).id}/decide_via_email/'

    def test_get_review_link_renders_decision_page_without_mutating(self):
        """GET must be side-effect free so email link-scanners can't trigger a decision."""
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)

        response = self.client.get(token_url)

        self.assertEqual(response.status_code, 200)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'PENDING')
        self.assertFalse(self.request_obj.logs.exists())

    def test_decide_via_email_approve(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)

        response = self.client.post(self._decide_url(), {'token': token, 'decision': 'approve', 'comment': 'Looks good'})

        self.assertEqual(response.status_code, 302)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'APPROVED')
        log = self.request_obj.logs.get(action='APPROVE', approver=self.creator)
        self.assertEqual(log.comment, 'Looks good')

    def test_decide_via_email_reject(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)

        response = self.client.post(self._decide_url(), {'token': token, 'decision': 'reject', 'comment': 'Not needed'})

        self.assertEqual(response.status_code, 302)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'REJECTED')
        self.assertTrue(self.request_obj.logs.filter(action='REJECT', approver=self.creator, comment='Not needed').exists())

    def test_decide_via_email_return_requires_comment(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)

        response = self.client.post(self._decide_url(), {'token': token, 'decision': 'return', 'comment': ''})

        self.assertEqual(response.status_code, 302)
        self.assertIn('email_error=comment_required', response.url)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'PENDING')
        self.assertFalse(self.request_obj.logs.filter(action='RETURN').exists())

    def test_decide_via_email_return_with_comment(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)

        response = self.client.post(self._decide_url(), {'token': token, 'decision': 'return', 'comment': 'Please add more detail'})

        self.assertEqual(response.status_code, 302)
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'RETURNED')
        self.assertTrue(self.request_obj.logs.filter(action='RETURN', comment='Please add more detail').exists())

    def test_decide_via_email_rejects_duplicate_submit(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)
        decide_url = self._decide_url()

        self.client.post(decide_url, {'token': token, 'decision': 'approve'})
        self.client.post(decide_url, {'token': token, 'decision': 'approve'})

        self.assertEqual(
            self.request_obj.logs.filter(action='APPROVE', approver=self.creator).count(), 1
        )

    def test_decide_via_email_rejects_invalid_decision(self):
        self.group.user_set.add(self.creator)
        token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        token = self._extract_token(token_url)

        response = self.client.post(self._decide_url(), {'token': token, 'decision': 'delete-everything'})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.request_obj.logs.exists())

    def test_stale_token_rejected_after_step_advances(self):
        """A token issued for an earlier step must not action a later step it wasn't issued for."""
        self.group.user_set.add(self.creator)
        stale_token_url = build_workflow_action_url(self.request_obj, 'review', self.creator.id)
        stale_token = self._extract_token(stale_token_url)

        # Simulate the request having moved on to another step since the email was sent.
        self.request_obj.current_step_number = 2
        self.request_obj.save()
        WorkflowStep.objects.create(
            workflow=self.workflow,
            step_number=2,
            step_name='Second Approver',
            required_group=self.group,
        )

        response = self.client.post(self._decide_url(), {'token': stale_token, 'decision': 'approve'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('email_error=stale_token', response.url)
        self.assertFalse(self.request_obj.logs.filter(action='APPROVE').exists())

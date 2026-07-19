from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from payment.models import PaymentApprovalTier, Supplier, SupplierBankAccount
from payment.services import create_payment_voucher
from workflow.models import ApprovalLog, WorkflowConfig, WorkflowStep

User = get_user_model()


class CreatePaymentVoucherTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='secret')
        self.workflow = WorkflowConfig.objects.create(name='Payment Approval', category='PAYMENT')
        WorkflowStep.objects.create(workflow=self.workflow, step_number=1, step_name='Manager Approval')

        self.tier = PaymentApprovalTier.objects.create(
            name='Default Tier', min_amount=Decimal('0'), max_amount=None,
            workflow_config=self.workflow, order=1,
        )

        self.supplier = Supplier.objects.create(name='ACME Co', tax_id='1111111111111')
        self.bank_account = SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='SCB', account_no='123-456', account_name='ACME Co',
            is_current=True,
        )

    @patch('payment.services.dispatch_workflow_action_required_email')
    def test_creates_request_with_correct_workflow_and_step(self, mock_dispatch):
        lines_data = [
            {'description': 'Consulting fee', 'amount': 1000, 'vat_rate': 7, 'wht_rate': 3},
            {'description': 'Materials', 'amount': 500, 'vat_rate': 7, 'wht_rate': 0},
        ]

        voucher = create_payment_voucher(
            supplier=self.supplier,
            lines_data=lines_data,
            payee_bank_account=self.bank_account,
            created_by=self.user,
        )

        self.assertIsNotNone(voucher.request)
        self.assertEqual(voucher.request.workflow, self.workflow)
        self.assertEqual(voucher.request.current_step_number, 1)
        self.assertEqual(voucher.request.status, 'PENDING')
        self.assertEqual(voucher.request.creator, self.user)
        self.assertTrue(voucher.pv_code)
        self.assertEqual(voucher.status, 'PENDING_APPROVAL')

        self.assertTrue(
            ApprovalLog.objects.filter(request=voucher.request, action='RESUBMIT', step_number=0).exists()
        )

    @patch('payment.services.dispatch_workflow_action_required_email')
    def test_computed_totals_match_sum_of_lines(self, mock_dispatch):
        lines_data = [
            {'description': 'Item A', 'amount': 1000, 'vat_rate': 7, 'wht_rate': 3},
            {'description': 'Item B', 'amount': 500, 'vat_rate': 7, 'wht_rate': 0},
        ]

        voucher = create_payment_voucher(
            supplier=self.supplier,
            lines_data=lines_data,
            payee_bank_account=self.bank_account,
            created_by=self.user,
        )

        lines = list(voucher.lines.all())
        self.assertEqual(len(lines), 2)

        expected_subtotal = sum(line.amount for line in lines)
        expected_vat = sum(line.vat_amount for line in lines)
        expected_wht = sum(line.wht_amount for line in lines)
        expected_net = sum(line.net_amount for line in lines)

        self.assertEqual(voucher.subtotal, expected_subtotal)
        self.assertEqual(voucher.vat_amount, expected_vat)
        self.assertEqual(voucher.wht_amount, expected_wht)
        self.assertEqual(voucher.net_amount, expected_net)

    @patch('payment.services.dispatch_workflow_action_required_email')
    def test_picks_correct_tier_for_amount(self, mock_dispatch):
        high_workflow = WorkflowConfig.objects.create(name='High Value Approval', category='PAYMENT')
        WorkflowStep.objects.create(workflow=high_workflow, step_number=1, step_name='CFO Approval')
        PaymentApprovalTier.objects.create(
            name='High', min_amount=Decimal('100000'), max_amount=None,
            workflow_config=high_workflow, order=0,
        )

        lines_data = [{'description': 'Big purchase', 'amount': 200000, 'vat_rate': 0, 'wht_rate': 0}]

        voucher = create_payment_voucher(
            supplier=self.supplier,
            lines_data=lines_data,
            payee_bank_account=self.bank_account,
            created_by=self.user,
        )

        self.assertEqual(voucher.request.workflow, high_workflow)

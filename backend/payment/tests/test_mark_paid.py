from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from payment.models import PaymentVoucher, Supplier, SupplierBankAccount
from workflow.models import Request, WorkflowConfig, WorkflowStep

User = get_user_model()


class MarkPaidActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='secret')
        self.workflow = WorkflowConfig.objects.create(name='Payment Approval', category='PAYMENT')
        WorkflowStep.objects.create(workflow=self.workflow, step_number=1, step_name='Manager Approval')

        self.supplier = Supplier.objects.create(name='ACME Co', tax_id='4444444444444')
        self.bank_account = SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='SCB', account_no='123-456', account_name='ACME Co',
            is_current=True,
        )

    def _make_voucher(self, request_status, voucher_status):
        req = Request.objects.create(
            title='PV Test', workflow=self.workflow, creator=self.user,
            status=request_status, current_step_number=1,
        )
        return PaymentVoucher.objects.create(
            request=req, pv_code=f'PV-{req.id}', supplier=self.supplier,
            payee_bank_account=self.bank_account, net_amount=Decimal('1000'),
            status=voucher_status, created_by=self.user,
        )

    def _mark_paid_url(self, voucher):
        return f'/api/v1/payment/vouchers/{voucher.id}/mark-paid/'

    def _auth_header(self, user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}

    def test_requires_authentication(self):
        voucher = self._make_voucher('APPROVED', 'APPROVED')
        response = self.client.post(self._mark_paid_url(voucher), {})
        self.assertEqual(response.status_code, 401)

    def test_succeeds_when_approved(self):
        voucher = self._make_voucher('APPROVED', 'APPROVED')

        response = self.client.post(
            self._mark_paid_url(voucher), {'pay_bank': 'SCB', 'cheque_no': '00123'},
            **self._auth_header(self.user),
        )

        self.assertEqual(response.status_code, 200)
        voucher.refresh_from_db()
        self.assertEqual(voucher.status, 'PAID')
        self.assertIsNotNone(voucher.paid_at)
        self.assertEqual(voucher.pay_bank, 'SCB')

    def test_rejected_when_voucher_status_not_approved(self):
        voucher = self._make_voucher('APPROVED', 'PENDING_APPROVAL')

        response = self.client.post(self._mark_paid_url(voucher), {}, **self._auth_header(self.user))

        self.assertEqual(response.status_code, 400)
        voucher.refresh_from_db()
        self.assertEqual(voucher.status, 'PENDING_APPROVAL')

    def test_rejected_when_underlying_request_not_approved(self):
        voucher = self._make_voucher('PENDING', 'APPROVED')

        response = self.client.post(self._mark_paid_url(voucher), {}, **self._auth_header(self.user))

        self.assertEqual(response.status_code, 400)
        voucher.refresh_from_db()
        self.assertEqual(voucher.status, 'APPROVED')

    def test_rejected_when_already_paid(self):
        voucher = self._make_voucher('APPROVED', 'PAID')

        response = self.client.post(self._mark_paid_url(voucher), {}, **self._auth_header(self.user))

        self.assertEqual(response.status_code, 400)

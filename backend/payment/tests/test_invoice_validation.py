import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payment.models import PaymentVoucher, PaymentVoucherLine, Supplier, SupplierBankAccount
from payment.services import validate_voucher

User = get_user_model()


class ValidateVoucherTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='secret')
        self.supplier = Supplier.objects.create(name='ACME Co', tax_id='2222222222222')
        self.other_supplier = Supplier.objects.create(name='Other Co', tax_id='3333333333333')

        self.bank_account = SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='SCB', account_no='123-456', account_name='ACME Co',
            is_current=True,
        )
        self.stale_bank_account = SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='KBank', account_no='999-999', account_name='ACME Co Old',
            is_current=False,
        )
        self.other_supplier_bank_account = SupplierBankAccount.objects.create(
            supplier=self.other_supplier, bank_name='BBL', account_no='777-777', account_name='Other Co',
            is_current=True,
        )

    _pv_counter = 0

    def _make_voucher(self, **overrides):
        ValidateVoucherTests._pv_counter += 1
        defaults = dict(
            supplier=self.supplier,
            payee_bank_account=self.bank_account,
            invoice_no_ref='INV-001',
            net_amount=Decimal('1000'),
            vat_amount=Decimal('70'),
            created_by=self.user,
            pv_code=f'PV-TEST-{ValidateVoucherTests._pv_counter}',
        )
        defaults.update(overrides)
        return PaymentVoucher.objects.create(**defaults)

    def test_duplicate_invoice_is_flagged(self):
        self._make_voucher()
        voucher2 = self._make_voucher()

        flags = validate_voucher(voucher2)

        codes = [f['code'] for f in flags]
        self.assertIn('DUPLICATE_INVOICE', codes)

    def test_bank_account_not_current_is_flagged(self):
        voucher = self._make_voucher(payee_bank_account=self.stale_bank_account, invoice_no_ref='')

        flags = validate_voucher(voucher)

        codes = [f['code'] for f in flags]
        self.assertIn('BANK_ACCOUNT_NOT_CURRENT', codes)

    def test_bank_account_belonging_to_different_supplier_is_flagged(self):
        voucher = self._make_voucher(payee_bank_account=self.other_supplier_bank_account, invoice_no_ref='')

        flags = validate_voucher(voucher)

        codes = [f['code'] for f in flags]
        self.assertIn('BANK_ACCOUNT_SUPPLIER_MISMATCH', codes)

    def test_vat_mismatch_is_flagged(self):
        voucher = self._make_voucher(invoice_no_ref='', vat_amount=Decimal('999'))
        PaymentVoucherLine.objects.create(
            voucher=voucher, description='Item', amount=Decimal('1000'),
            vat_rate=Decimal('7'), vat_amount=Decimal('70'), net_amount=Decimal('1070'),
        )

        flags = validate_voucher(voucher)

        codes = [f['code'] for f in flags]
        self.assertIn('VAT_MISMATCH', codes)

    def test_due_date_passed_is_flagged(self):
        voucher = self._make_voucher(
            invoice_no_ref='', due_date=datetime.date.today() - datetime.timedelta(days=5),
        )

        flags = validate_voucher(voucher)

        codes = [f['code'] for f in flags]
        self.assertIn('DUE_DATE_PASSED', codes)

    def test_valid_voucher_has_no_flags(self):
        voucher = self._make_voucher(invoice_no_ref='', vat_amount=Decimal('0'))

        flags = validate_voucher(voucher)

        self.assertEqual(flags, [])

from django.db import IntegrityError, transaction
from django.test import TestCase

from payment.models import Supplier, SupplierBankAccount


class SupplierTests(TestCase):
    def test_tax_id_must_be_unique(self):
        Supplier.objects.create(name='Supplier A', tax_id='1234567890123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Supplier.objects.create(name='Supplier B', tax_id='1234567890123')


class SupplierBankAccountTests(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(name='Supplier A', tax_id='1234567890123')

    def test_only_one_current_bank_account_per_supplier(self):
        SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='Bank 1', account_no='001', account_name='Acc1', is_current=True,
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SupplierBankAccount.objects.create(
                    supplier=self.supplier, bank_name='Bank 2', account_no='002', account_name='Acc2',
                    is_current=True,
                )

    def test_multiple_non_current_accounts_allowed(self):
        SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='Bank 1', account_no='001', account_name='Acc1', is_current=False,
        )
        SupplierBankAccount.objects.create(
            supplier=self.supplier, bank_name='Bank 2', account_no='002', account_name='Acc2', is_current=False,
        )
        self.assertEqual(self.supplier.bank_accounts.count(), 2)

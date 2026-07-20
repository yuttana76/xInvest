import csv
import datetime
import os
import tempfile

from django.core.management import call_command
from django.test import TestCase

from payment.models import DepreciationEntry, FixedAsset, Supplier, SupplierBankAccount


class ImportSuppliersCommandTests(TestCase):
    def _write_csv(self, rows):
        fd, path = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'tax_id', 'branch_type', 'address', 'phone', 'email',
                'bank_name', 'branch', 'account_no', 'account_name',
            ])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path

    def test_import_is_idempotent_on_rerun(self):
        rows = [{
            'name': 'ACME Co', 'tax_id': '5555555555555', 'branch_type': 'HQ',
            'address': '123 Road', 'phone': '02-000-0000', 'email': 'acme@example.com',
            'bank_name': 'SCB', 'branch': 'Silom', 'account_no': '111-222-333',
            'account_name': 'ACME Co Ltd',
        }]
        path = self._write_csv(rows)

        call_command('import_suppliers', file=path)
        call_command('import_suppliers', file=path)

        self.assertEqual(Supplier.objects.filter(tax_id='5555555555555').count(), 1)
        supplier = Supplier.objects.get(tax_id='5555555555555')
        self.assertEqual(supplier.bank_accounts.count(), 1)
        self.assertEqual(supplier.bank_accounts.filter(is_current=True).count(), 1)

    def test_import_updates_existing_supplier_fields(self):
        path = self._write_csv([{
            'name': 'ACME Co', 'tax_id': '6666666666666', 'branch_type': 'HQ',
            'address': 'Old Address', 'phone': '', 'email': '',
            'bank_name': 'SCB', 'branch': '', 'account_no': '999',
            'account_name': 'ACME Co Ltd',
        }])
        call_command('import_suppliers', file=path)

        path2 = self._write_csv([{
            'name': 'ACME Co', 'tax_id': '6666666666666', 'branch_type': 'HQ',
            'address': 'New Address', 'phone': '', 'email': '',
            'bank_name': 'SCB', 'branch': '', 'account_no': '999',
            'account_name': 'ACME Co Ltd',
        }])
        call_command('import_suppliers', file=path2)

        supplier = Supplier.objects.get(tax_id='6666666666666')
        self.assertEqual(supplier.address, 'New Address')
        self.assertEqual(Supplier.objects.filter(tax_id='6666666666666').count(), 1)


class ImportDepreciationExcelCommandTests(TestCase):
    def _build_fixture_xlsx(self):
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '2569'

        # Row 1: title row (mostly irrelevant to the parser)
        ws.append(['Test Company', None, None, None, None, None, None, None, None, None])
        # Row 2/3: header rows (informational only, parser doesn't rely on labels)
        ws.append(['ลำดับ', 'เลขที่', 'เลขที่', 'จ่าย', 'เริ่มคำนวณ', 'รายการทรัพย์สิน', 'Supplier',
                    'ประเภท', 'ราคา', 'ยกมา'])
        ws.append([None, 'ทรัพย์สิน', 'ใบสำคัญจ่าย', None, None, None, None, 'ประเภท', 'ที่ซื้อมา', 'ยกมา'])

        # Category header row: item_no None, asset_code(col B)=1(int), name(col F)='ยานพาหนะ'
        ws.append([None, 1, '100-504-00', None, None, 'ยานพาหนะ'])

        # Data row for a vehicle asset
        row = [
            1, 'TEST-CAR-001', 'PV0001', datetime.date(2026, 1, 1), datetime.date(2026, 1, 1),
            'Test Vehicle', 'Test Supplier', 'รถตู้', 450000, 0, 0.2, 90000, 365,
        ]
        row += [7500] * 12  # JAN..DEC monthly depreciation
        row += [90000, 90000, 360000, 'TAXINV-001', 'Main Office']
        ws.append(row)

        # Category header row for computer category
        ws.append([None, 3, '100-503-00', None, None, 'เครื่องคอมพิวเตอร์'])
        row2 = [
            1, 'TEST-PC-001', 'PV0002', datetime.date(2026, 2, 1), datetime.date(2026, 2, 1),
            'Test Computer', 'Test Supplier 2', 'คอมพิวเตอร์', 30000, 0, 0.333, 10000, 365,
        ]
        row2 += [0, 833, 833, 833, 833, 833, 833, 833, 833, 833, 833, 833]
        row2 += [10000, 10000, 20000, 'TAXINV-002', 'IT Room']
        ws.append(row2)

        fd, path = tempfile.mkstemp(suffix='.xlsx')
        os.close(fd)
        wb.save(path)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))
        return path

    def test_import_creates_expected_assets_and_entries(self):
        path = self._build_fixture_xlsx()

        call_command('import_depreciation_excel', file=path, sheet='2569')

        self.assertEqual(FixedAsset.objects.count(), 2)

        car = FixedAsset.objects.get(asset_code='TEST-CAR-001')
        self.assertEqual(car.category, 'VEHICLE')
        self.assertEqual(car.legacy_pv_ref, 'PV0001')
        self.assertEqual(car.tax_invoice_no, 'TAXINV-001')
        self.assertEqual(int(car.purchase_price), 450000)
        self.assertEqual(car.depreciation_entries.count(), 12)

        pc = FixedAsset.objects.get(asset_code='TEST-PC-001')
        self.assertEqual(pc.category, 'COMPUTER')
        # Only 11 non-zero months (JAN was 0)
        self.assertEqual(pc.depreciation_entries.count(), 11)

    def test_import_is_idempotent_on_rerun(self):
        path = self._build_fixture_xlsx()

        call_command('import_depreciation_excel', file=path, sheet='2569')
        call_command('import_depreciation_excel', file=path, sheet='2569')

        self.assertEqual(FixedAsset.objects.count(), 2)
        car = FixedAsset.objects.get(asset_code='TEST-CAR-001')
        self.assertEqual(car.depreciation_entries.count(), 12)

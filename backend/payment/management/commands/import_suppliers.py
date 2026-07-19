import csv
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from payment.models import Supplier, SupplierBankAccount

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    'name', 'tax_id', 'branch_type', 'address', 'phone', 'email',
    'bank_name', 'branch', 'account_no', 'account_name',
]


class Command(BaseCommand):
    help = "Import suppliers (and their current bank account) from a CSV or XLSX file. Idempotent by tax_id."

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Path to the CSV or XLSX file to import.')

    def handle(self, *args, **options):
        file_path = options['file']
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            rows = self._read_csv(file_path)
        elif ext in ('.xlsx', '.xlsm'):
            rows = self._read_xlsx(file_path)
        else:
            raise CommandError(f"Unsupported file extension: {ext}")

        created_count = 0
        updated_count = 0

        for row in rows:
            tax_id = str(row.get('tax_id') or '').strip()
            if not tax_id:
                continue

            with transaction.atomic():
                supplier, created = Supplier.objects.update_or_create(
                    tax_id=tax_id,
                    defaults={
                        'name': (row.get('name') or '').strip(),
                        'branch_type': (row.get('branch_type') or 'HQ').strip().upper() or 'HQ',
                        'address': (row.get('address') or '').strip(),
                        'phone': (row.get('phone') or '').strip(),
                        'email': (row.get('email') or '').strip(),
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                account_no = (row.get('account_no') or '').strip()
                if account_no:
                    SupplierBankAccount.objects.update_or_create(
                        supplier=supplier,
                        account_no=account_no,
                        defaults={
                            'bank_name': (row.get('bank_name') or '').strip(),
                            'branch': (row.get('branch') or '').strip(),
                            'account_name': (row.get('account_name') or '').strip(),
                            'is_current': True,
                        },
                    )
                    # Ensure only this account is current for the supplier
                    supplier.bank_accounts.exclude(account_no=account_no).update(is_current=False)

        self.stdout.write(self.style.SUCCESS(
            f"Import complete. Created {created_count} suppliers, updated {updated_count} suppliers."
        ))

    def _read_csv(self, file_path):
        with open(file_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _read_xlsx(self, file_path):
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        header = [str(h).strip() if h else '' for h in next(rows_iter)]
        rows = []
        for values in rows_iter:
            if all(v is None for v in values):
                continue
            rows.append(dict(zip(header, values)))
        return rows

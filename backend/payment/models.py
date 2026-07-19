from django.conf import settings
from django.db import models, transaction
from django.db.models import Q

User = settings.AUTH_USER_MODEL


class Supplier(models.Model):
    BRANCH_TYPE_CHOICES = [
        ('HQ', 'สำนักงานใหญ่'),
        ('BRANCH', 'สาขา'),
    ]

    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=13, unique=True, db_index=True)
    branch_type = models.CharField(max_length=10, choices=BRANCH_TYPE_CHOICES, default='HQ')
    branch_no = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    default_wht_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.tax_id})"


class SupplierBankAccount(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='bank_accounts', on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True)
    account_no = models.CharField(max_length=30)
    account_name = models.CharField(max_length=255)
    is_current = models.BooleanField(default=True)
    verified_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['supplier'],
                condition=Q(is_current=True),
                name='one_current_bank_account_per_supplier',
            )
        ]

    def __str__(self):
        return f"{self.supplier.name} - {self.bank_name} {self.account_no}"


class SourceDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('QUOTATION', 'ใบเสนอราคา'),
        ('INVOICE', 'ใบแจ้งหนี้/บิล'),
    ]
    EXTRACTION_STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('PROCESSING', 'PROCESSING'),
        ('SUCCESS', 'SUCCESS'),
        ('FAILED', 'FAILED'),
        ('NEEDS_REVIEW', 'NEEDS_REVIEW'),
    ]

    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    file = models.FileField(upload_to='payment/documents/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    supplier_guess = models.ForeignKey(Supplier, null=True, blank=True, on_delete=models.SET_NULL)
    extraction_status = models.CharField(max_length=20, choices=EXTRACTION_STATUS_CHOICES, default='PENDING')
    extracted_data = models.JSONField(null=True, blank=True)
    ai_error_message = models.TextField(blank=True)
    linked_quotation = models.ForeignKey(
        'self', null=True, blank=True, related_name='matched_invoices', on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} #{self.pk}"


class PVNumberingConfig(models.Model):
    RESET_PERIOD_CHOICES = [
        ('NEVER', 'NEVER'),
        ('YEARLY', 'YEARLY'),
        ('MONTHLY', 'MONTHLY'),
    ]

    prefix = models.CharField(max_length=10, default="PV")
    pattern = models.CharField(max_length=100, default="{prefix}{seq:02d}/{running:03d}")
    reset_period = models.CharField(max_length=10, choices=RESET_PERIOD_CHOICES, default='YEARLY')
    current_seq = models.PositiveIntegerField(default=1)
    current_running = models.PositiveIntegerField(default=0)
    last_reset_period_key = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.prefix} ({self.reset_period})"

    def _current_period_key(self):
        from django.utils import timezone
        now = timezone.localtime()
        if self.reset_period == 'YEARLY':
            return str(now.year)
        elif self.reset_period == 'MONTHLY':
            return f"{now.year}-{now.month:02d}"
        return ''

    def generate_next(self):
        """Generate the next PV code. Safe under concurrent calls via select_for_update()."""
        with transaction.atomic():
            config = PVNumberingConfig.objects.select_for_update().get(pk=self.pk)
            period_key = config._current_period_key()

            if config.reset_period != 'NEVER' and period_key != config.last_reset_period_key:
                config.current_seq += 1 if config.last_reset_period_key else 0
                config.current_running = 0
                config.last_reset_period_key = period_key

            config.current_running += 1
            config.save()

            code = config.pattern.format(
                prefix=config.prefix,
                seq=config.current_seq,
                running=config.current_running,
            )

            # Keep in-memory instance in sync
            self.current_seq = config.current_seq
            self.current_running = config.current_running
            self.last_reset_period_key = config.last_reset_period_key

            return code

    @classmethod
    def get_active_config(cls):
        config = cls.objects.first()
        if not config:
            config = cls.objects.create()
        return config


class PaymentApprovalTier(models.Model):
    name = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    workflow_config = models.ForeignKey('workflow.WorkflowConfig', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.min_amount} - {self.max_amount or 'unbounded'})"

    @classmethod
    def resolve_for_amount(cls, amount):
        qs = cls.objects.filter(is_active=True, min_amount__lte=amount).order_by('order')
        for tier in qs:
            if tier.max_amount is None or amount <= tier.max_amount:
                return tier
        raise ValueError(f"No active PaymentApprovalTier configured for amount {amount}")


class PaymentBatch(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'DRAFT'),
        ('EXPORTED', 'EXPORTED'),
        ('CONFIRMED', 'CONFIRMED'),
    ]

    batch_code = models.CharField(max_length=50, unique=True)
    bank = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    exported_file = models.FileField(upload_to='payment/batches/%Y/%m/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.batch_code


class PaymentVoucher(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'DRAFT'),
        ('PENDING_APPROVAL', 'PENDING_APPROVAL'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
        ('RETURNED', 'RETURNED'),
        ('PAID', 'PAID'),
    ]

    request = models.OneToOneField(
        'workflow.Request', on_delete=models.PROTECT, related_name='payment_voucher', null=True, blank=True
    )
    pv_code = models.CharField(max_length=50, unique=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    source_document = models.ForeignKey(SourceDocument, null=True, blank=True, on_delete=models.SET_NULL)
    payee_bank_account = models.ForeignKey(SupplierBankAccount, on_delete=models.PROTECT)
    invoice_no_ref = models.CharField(max_length=100, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    wht_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_fixed_asset = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    pay_bank = models.CharField(max_length=100, blank=True)
    cheque_no = models.CharField(max_length=50, blank=True)
    cheque_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    validation_flags = models.JSONField(default=list, blank=True)
    batch = models.ForeignKey(
        PaymentBatch, null=True, blank=True, on_delete=models.SET_NULL, related_name='vouchers'
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payment_vouchers_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pv_code or f"Voucher #{self.pk}"


class PaymentVoucherLine(models.Model):
    voucher = models.ForeignKey(PaymentVoucher, related_name='lines', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    department = models.ForeignKey('users.Department', null=True, blank=True, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    wht_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    wht_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.description} ({self.amount})"


class FixedAsset(models.Model):
    CATEGORY_CHOICES = [
        ('VEHICLE', 'ยานพาหนะ'),
        ('COMPUTER', 'คอมพิวเตอร์'),
        ('FURNITURE', 'เครื่องตกแต่ง/เครื่องมือเครื่องใช้'),
        ('OFFICE_DECOR', 'ค่าตกแต่งสำนักงาน'),
        ('SOFTWARE', 'ซอฟต์แวร์คอมพิวเตอร์'),
        ('OTHER', 'อื่นๆ'),
    ]

    asset_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    purchase_voucher = models.ForeignKey(PaymentVoucher, null=True, blank=True, on_delete=models.SET_NULL)
    legacy_pv_ref = models.CharField(max_length=50, blank=True)
    tax_invoice_no = models.CharField(max_length=100, blank=True)
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2)
    purchase_date = models.DateField()
    depreciation_rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    useful_life_days = models.PositiveIntegerField(null=True, blank=True)
    disposed_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.asset_code} - {self.name}"


class DepreciationEntry(models.Model):
    asset = models.ForeignKey(FixedAsset, related_name='depreciation_entries', on_delete=models.CASCADE)
    period = models.CharField(max_length=7)  # "2026-06"
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    accumulated_amount = models.DecimalField(max_digits=14, decimal_places=2)
    is_disallowed_expense = models.BooleanField(default=False)

    class Meta:
        unique_together = [('asset', 'period')]

    def __str__(self):
        return f"{self.asset.asset_code} - {self.period}"

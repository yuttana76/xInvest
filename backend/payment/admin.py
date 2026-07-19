from django.contrib import admin
from .models import (
    Supplier, SupplierBankAccount, SourceDocument, PVNumberingConfig,
    PaymentApprovalTier, PaymentVoucher, PaymentVoucherLine, FixedAsset,
    DepreciationEntry, PaymentBatch,
)


class SupplierBankAccountInline(admin.TabularInline):
    model = SupplierBankAccount
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'branch_type', 'is_active')
    search_fields = ('name', 'tax_id')
    list_filter = ('branch_type', 'is_active')
    inlines = [SupplierBankAccountInline]


@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc_type', 'extraction_status', 'supplier_guess', 'created_at')
    list_filter = ('doc_type', 'extraction_status')


@admin.register(PVNumberingConfig)
class PVNumberingConfigAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'pattern', 'reset_period', 'current_seq', 'current_running')


@admin.register(PaymentApprovalTier)
class PaymentApprovalTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_amount', 'max_amount', 'workflow_config', 'order', 'is_active')
    list_editable = ('order', 'is_active')


class PaymentVoucherLineInline(admin.TabularInline):
    model = PaymentVoucherLine
    extra = 0


@admin.register(PaymentVoucher)
class PaymentVoucherAdmin(admin.ModelAdmin):
    list_display = ('pv_code', 'supplier', 'net_amount', 'status', 'is_fixed_asset', 'created_at')
    list_filter = ('status', 'is_fixed_asset')
    search_fields = ('pv_code', 'invoice_no_ref', 'supplier__name')
    inlines = [PaymentVoucherLineInline]


class DepreciationEntryInline(admin.TabularInline):
    model = DepreciationEntry
    extra = 0


@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ('asset_code', 'name', 'category', 'purchase_price', 'purchase_date')
    list_filter = ('category',)
    search_fields = ('asset_code', 'name', 'legacy_pv_ref')
    inlines = [DepreciationEntryInline]


@admin.register(PaymentBatch)
class PaymentBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_code', 'bank', 'status', 'created_at')

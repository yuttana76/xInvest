from rest_framework import serializers

from .models import (
    Supplier, SupplierBankAccount, SourceDocument, PaymentApprovalTier,
    PaymentVoucher, PaymentVoucherLine, FixedAsset, DepreciationEntry, PaymentBatch,
)


class SupplierBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierBankAccount
        fields = [
            'id', 'supplier', 'bank_name', 'branch', 'account_no', 'account_name',
            'is_current', 'verified_by', 'verified_at', 'created_at',
        ]
        read_only_fields = ['verified_by', 'verified_at', 'created_at']


class SupplierSerializer(serializers.ModelSerializer):
    bank_accounts = SupplierBankAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'tax_id', 'branch_type', 'branch_no', 'address', 'phone', 'email',
            'default_wht_rate', 'is_active', 'bank_accounts', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class SourceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceDocument
        fields = [
            'id', 'doc_type', 'file', 'uploaded_by', 'supplier_guess', 'extraction_status',
            'extracted_data', 'ai_error_message', 'linked_quotation', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'uploaded_by', 'extraction_status', 'extracted_data', 'ai_error_message',
            'created_at', 'updated_at',
        ]


class PaymentVoucherLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentVoucherLine
        fields = [
            'id', 'description', 'department', 'amount', 'vat_rate', 'vat_amount',
            'wht_rate', 'wht_amount', 'net_amount',
        ]


class PaymentApprovalTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentApprovalTier
        fields = [
            'id', 'name', 'min_amount', 'max_amount', 'workflow_config', 'is_active', 'order',
        ]


class PaymentVoucherSerializer(serializers.ModelSerializer):
    lines = PaymentVoucherLineSerializer(many=True, read_only=True)
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    request_status = serializers.ReadOnlyField(source='request.status')

    class Meta:
        model = PaymentVoucher
        fields = [
            'id', 'request', 'request_status', 'pv_code', 'supplier', 'supplier_name',
            'source_document', 'payee_bank_account', 'invoice_no_ref', 'invoice_date', 'due_date',
            'subtotal', 'vat_amount', 'wht_amount', 'net_amount', 'is_fixed_asset', 'status',
            'pay_bank', 'cheque_no', 'cheque_date', 'paid_at', 'validation_flags', 'batch',
            'created_by', 'created_at', 'updated_at', 'lines',
        ]
        read_only_fields = [
            'request', 'pv_code', 'subtotal', 'vat_amount', 'wht_amount', 'net_amount', 'status',
            'validation_flags', 'created_by', 'created_at', 'updated_at',
        ]


class PaymentVoucherCreateSerializer(serializers.Serializer):
    """Input serializer for the voucher-creation endpoint (delegates to services.create_payment_voucher)."""
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())
    payee_bank_account = serializers.PrimaryKeyRelatedField(queryset=SupplierBankAccount.objects.all())
    source_document = serializers.PrimaryKeyRelatedField(
        queryset=SourceDocument.objects.all(), required=False, allow_null=True
    )
    is_fixed_asset = serializers.BooleanField(required=False, default=False)
    invoice_no_ref = serializers.CharField(required=False, allow_blank=True, default='')
    invoice_date = serializers.DateField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    lines = serializers.ListField(child=serializers.DictField(), allow_empty=False)


class DepreciationEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DepreciationEntry
        fields = ['id', 'asset', 'period', 'amount', 'accumulated_amount', 'is_disallowed_expense']


class FixedAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedAsset
        fields = [
            'id', 'asset_code', 'name', 'category', 'purchase_voucher', 'legacy_pv_ref',
            'tax_invoice_no', 'purchase_price', 'purchase_date', 'depreciation_rate_percent',
            'useful_life_days', 'disposed_at',
        ]


class PaymentBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentBatch
        fields = ['id', 'batch_code', 'bank', 'status', 'exported_file', 'created_at']

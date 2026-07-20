import io
import logging

from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import (
    Supplier, SupplierBankAccount, SourceDocument, PaymentApprovalTier,
    PaymentVoucher, FixedAsset, DepreciationEntry,
)
from .serializers import (
    SupplierSerializer, SupplierBankAccountSerializer, SourceDocumentSerializer,
    PaymentApprovalTierSerializer, PaymentVoucherSerializer, PaymentVoucherCreateSerializer,
    FixedAssetSerializer, DepreciationEntrySerializer,
)
from .services import create_payment_voucher
from .tasks import extract_invoice_task

logger = logging.getLogger(__name__)


class OptionalPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('name')
    serializer_class = SupplierSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q')
        tax_id = self.request.query_params.get('tax_id')
        if q:
            queryset = queryset.filter(name__icontains=q)
        if tax_id:
            queryset = queryset.filter(tax_id=tax_id)
        return queryset

    @action(detail=True, methods=['get', 'post'], url_path='bank-accounts')
    def bank_accounts(self, request, pk=None):
        supplier = self.get_object()
        if request.method == 'GET':
            accounts = supplier.bank_accounts.all()
            serializer = SupplierBankAccountSerializer(accounts, many=True)
            return Response(serializer.data)

        serializer = SupplierBankAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(supplier=supplier)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'bank-accounts/(?P<bank_id>[^/.]+)/set-current')
    def set_current_bank_account(self, request, pk=None, bank_id=None):
        supplier = self.get_object()
        try:
            account = supplier.bank_accounts.get(pk=bank_id)
        except SupplierBankAccount.DoesNotExist:
            return Response({"error": "Bank account not found."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            supplier.bank_accounts.exclude(pk=account.pk).update(is_current=False)
            account.is_current = True
            account.verified_by = request.user
            account.verified_at = timezone.now()
            account.save()

        return Response(SupplierBankAccountSerializer(account).data)


class SourceDocumentViewSet(viewsets.ModelViewSet):
    queryset = SourceDocument.objects.all().order_by('-created_at')
    serializer_class = SourceDocumentSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        queryset = super().get_queryset()
        doc_type = self.request.query_params.get('doc_type')
        extraction_status = self.request.query_params.get('extraction_status')
        if doc_type:
            queryset = queryset.filter(doc_type=doc_type)
        if extraction_status:
            queryset = queryset.filter(extraction_status=extraction_status)
        return queryset

    def perform_create(self, serializer):
        doc = serializer.save(uploaded_by=self.request.user)
        try:
            extract_invoice_task.delay(doc.id)
        except Exception as exc:
            logger.warning(f"Celery unavailable for invoice extraction, running synchronously: {exc}")
            extract_invoice_task(doc.id)

    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        doc = self.get_object()
        doc.extraction_status = 'PENDING'
        doc.ai_error_message = ''
        doc.save(update_fields=['extraction_status', 'ai_error_message'])
        try:
            extract_invoice_task.delay(doc.id)
        except Exception as exc:
            logger.warning(f"Celery unavailable for invoice extraction, running synchronously: {exc}")
            extract_invoice_task(doc.id)
        return Response(SourceDocumentSerializer(doc).data)


class PaymentVoucherViewSet(viewsets.ModelViewSet):
    queryset = PaymentVoucher.objects.all().order_by('-created_at')
    serializer_class = PaymentVoucherSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        supplier_id = self.request.query_params.get('supplier')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        return queryset

    def create(self, request, *args, **kwargs):
        input_serializer = PaymentVoucherCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        voucher = create_payment_voucher(
            supplier=data['supplier'],
            lines_data=data['lines'],
            payee_bank_account=data['payee_bank_account'],
            source_document=data.get('source_document'),
            is_fixed_asset=data.get('is_fixed_asset', False),
            created_by=request.user,
            invoice_no_ref=data.get('invoice_no_ref', ''),
            invoice_date=data.get('invoice_date'),
            due_date=data.get('due_date'),
        )

        return Response(PaymentVoucherSerializer(voucher).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        voucher = self.get_object()

        underlying_approved = voucher.request is not None and voucher.request.status == 'APPROVED'
        if voucher.status != 'APPROVED' or not underlying_approved:
            return Response(
                {"error": "Voucher must be Approved (and its underlying request Approved) before marking as paid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        voucher.pay_bank = request.data.get('pay_bank', voucher.pay_bank)
        voucher.cheque_no = request.data.get('cheque_no', voucher.cheque_no)
        cheque_date = request.data.get('cheque_date')
        if cheque_date:
            voucher.cheque_date = cheque_date
        voucher.paid_at = timezone.now()
        voucher.status = 'PAID'
        voucher.save()

        return Response(PaymentVoucherSerializer(voucher).data)

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        voucher = self.get_object()

        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"Payment Voucher / ใบสำคัญจ่าย - {voucher.pv_code}", styles['Title']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Supplier: {voucher.supplier.name}", styles['Normal']))
        elements.append(Paragraph(f"Invoice Ref: {voucher.invoice_no_ref}", styles['Normal']))
        elements.append(Paragraph(f"Status: {voucher.status}", styles['Normal']))
        elements.append(Spacer(1, 12))

        table_data = [["Description", "Amount", "VAT", "WHT", "Net"]]
        for line in voucher.lines.all():
            table_data.append([
                line.description, str(line.amount), str(line.vat_amount),
                str(line.wht_amount), str(line.net_amount),
            ])
        table_data.append(["TOTAL", str(voucher.subtotal), str(voucher.vat_amount),
                            str(voucher.wht_amount), str(voucher.net_amount)])

        table = Table(table_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"{voucher.pv_code or voucher.pk}.pdf")


class PaymentApprovalTierViewSet(viewsets.ModelViewSet):
    queryset = PaymentApprovalTier.objects.all().order_by('order')
    serializer_class = PaymentApprovalTierSerializer
    permission_classes = [permissions.IsAuthenticated]


class FixedAssetViewSet(viewsets.ModelViewSet):
    queryset = FixedAsset.objects.all().order_by('asset_code')
    serializer_class = FixedAssetSerializer
    pagination_class = OptionalPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='depreciation-entries')
    def depreciation_entries(self, request, pk=None):
        asset = self.get_object()
        entries = asset.depreciation_entries.all().order_by('period')
        serializer = DepreciationEntrySerializer(entries, many=True)
        return Response(serializer.data)

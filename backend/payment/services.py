import logging
from decimal import Decimal

from django.db import transaction

from workflow.models import Request, ApprovalLog
from workflow.tasks import dispatch_workflow_action_required_email

from .models import (
    PaymentApprovalTier, PaymentVoucher, PaymentVoucherLine, PVNumberingConfig,
    SourceDocument,
)

logger = logging.getLogger(__name__)


def _notify_first_step(request_obj):
    """Mirror RequestViewSet.perform_create's first-step notification logic exactly."""
    current_step = request_obj.get_current_step_info()
    if current_step:
        if current_step.is_department_manager:
            manager = None
            creator = request_obj.creator
            if hasattr(creator, 'profile') and creator.profile.department:
                manager = getattr(creator.profile.department, 'manager', None)
            if manager:
                dispatch_workflow_action_required_email(request_obj.id, user_id=manager.id)
            else:
                logger.warning(f"No department manager found for creator {request_obj.creator.username}")
        elif current_step.required_group:
            dispatch_workflow_action_required_email(request_obj.id, group_id=current_step.required_group.id)
    else:
        logger.warning(f"No current step found for request {request_obj.id} at step 1")


@transaction.atomic
def create_payment_voucher(
    supplier, lines_data, payee_bank_account, source_document=None, is_fixed_asset=False,
    created_by=None, invoice_no_ref='', invoice_date=None, due_date=None,
):
    """
    Create a PaymentVoucher (and its lines) with the correct totals, route it through
    the workflow app for approval based on the resolved PaymentApprovalTier, and
    replicate RequestViewSet.perform_create's initial notification behavior.
    """
    subtotal = Decimal('0')
    vat_amount = Decimal('0')
    wht_amount = Decimal('0')
    net_amount = Decimal('0')

    computed_lines = []
    for line in lines_data:
        amount = Decimal(str(line['amount']))
        vat_rate = Decimal(str(line.get('vat_rate', 0)))
        wht_rate = Decimal(str(line.get('wht_rate', 0)))
        line_vat = (amount * vat_rate / Decimal('100')).quantize(Decimal('0.01'))
        line_wht = (amount * wht_rate / Decimal('100')).quantize(Decimal('0.01'))
        line_net = amount + line_vat - line_wht

        subtotal += amount
        vat_amount += line_vat
        wht_amount += line_wht
        net_amount += line_net

        computed_lines.append({
            'description': line['description'],
            'department': line.get('department'),
            'amount': amount,
            'vat_rate': vat_rate,
            'vat_amount': line_vat,
            'wht_rate': wht_rate,
            'wht_amount': line_wht,
            'net_amount': line_net,
        })

    tier = PaymentApprovalTier.resolve_for_amount(net_amount)

    user_profile = getattr(created_by, 'profile', None)
    department_name = user_profile.department.name if user_profile and user_profile.department else None

    request_obj = Request.objects.create(
        title=f"Payment Voucher - {supplier.name}",
        workflow=tier.workflow_config,
        creator=created_by,
        create_department=department_name,
        status='PENDING',
        current_step_number=1,
    )

    ApprovalLog.objects.create(
        request=request_obj,
        approver=created_by,
        step_number=0,
        step_name="Creation",
        action="RESUBMIT",
        comment="Payment voucher created and submitted for approval.",
    )

    _notify_first_step(request_obj)

    config = PVNumberingConfig.get_active_config()
    pv_code = config.generate_next()

    voucher = PaymentVoucher.objects.create(
        request=request_obj,
        pv_code=pv_code,
        supplier=supplier,
        source_document=source_document,
        payee_bank_account=payee_bank_account,
        invoice_no_ref=invoice_no_ref,
        invoice_date=invoice_date,
        due_date=due_date,
        subtotal=subtotal,
        vat_amount=vat_amount,
        wht_amount=wht_amount,
        net_amount=net_amount,
        is_fixed_asset=is_fixed_asset,
        status='PENDING_APPROVAL',
        created_by=created_by,
    )

    for line in computed_lines:
        PaymentVoucherLine.objects.create(voucher=voucher, **line)

    validate_voucher(voucher)

    return voucher


def validate_voucher(voucher):
    """
    Populate voucher.validation_flags with a list of {code, message, severity} dicts.
    Purely advisory - never blocks creation/approval.
    """
    flags = []

    # 1. Duplicate invoice check (same supplier + invoice_no_ref + net_amount)
    if voucher.invoice_no_ref:
        dup_qs = PaymentVoucher.objects.filter(
            supplier=voucher.supplier,
            invoice_no_ref=voucher.invoice_no_ref,
            net_amount=voucher.net_amount,
        ).exclude(pk=voucher.pk)
        if dup_qs.exists():
            flags.append({
                'code': 'DUPLICATE_INVOICE',
                'message': f"Another voucher already exists with invoice ref '{voucher.invoice_no_ref}' "
                           f"and the same net amount for this supplier.",
                'severity': 'WARNING',
            })

        dup_doc_qs = SourceDocument.objects.filter(
            supplier_guess=voucher.supplier,
            extracted_data__invoice_no=voucher.invoice_no_ref,
        )
        if voucher.source_document_id:
            dup_doc_qs = dup_doc_qs.exclude(pk=voucher.source_document_id)
        if dup_doc_qs.exists():
            flags.append({
                'code': 'DUPLICATE_SOURCE_DOCUMENT',
                'message': f"Another source document with invoice ref '{voucher.invoice_no_ref}' "
                           f"already exists for this supplier.",
                'severity': 'WARNING',
            })

    # 2. Bank account mismatch
    bank_account = voucher.payee_bank_account
    if bank_account:
        if bank_account.supplier_id != voucher.supplier_id:
            flags.append({
                'code': 'BANK_ACCOUNT_SUPPLIER_MISMATCH',
                'message': "The payee bank account does not belong to the voucher's supplier.",
                'severity': 'ERROR',
            })
        if not bank_account.is_current:
            flags.append({
                'code': 'BANK_ACCOUNT_NOT_CURRENT',
                'message': "The payee bank account is not marked as the supplier's current account.",
                'severity': 'WARNING',
            })

    # 3. VAT recompute mismatch
    lines_vat_total = sum((line.vat_amount for line in voucher.lines.all()), Decimal('0'))
    tolerance = Decimal('0.05')
    if abs(lines_vat_total - voucher.vat_amount) > tolerance:
        flags.append({
            'code': 'VAT_MISMATCH',
            'message': f"Sum of line VAT ({lines_vat_total}) does not match voucher VAT ({voucher.vat_amount}).",
            'severity': 'WARNING',
        })

    # 4. Due date already passed
    if voucher.due_date:
        from django.utils import timezone
        if voucher.due_date < timezone.localdate():
            flags.append({
                'code': 'DUE_DATE_PASSED',
                'message': f"Due date {voucher.due_date} has already passed.",
                'severity': 'WARNING',
            })

    voucher.validation_flags = flags
    voucher.save(update_fields=['validation_flags'])
    return flags

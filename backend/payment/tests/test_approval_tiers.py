from decimal import Decimal

from django.test import TestCase

from payment.models import PaymentApprovalTier
from workflow.models import WorkflowConfig


class PaymentApprovalTierTests(TestCase):
    def setUp(self):
        self.wf_low = WorkflowConfig.objects.create(name='Low Value Approval', category='PAYMENT')
        self.wf_mid = WorkflowConfig.objects.create(name='Mid Value Approval', category='PAYMENT')
        self.wf_high = WorkflowConfig.objects.create(name='High Value Approval', category='PAYMENT')

        self.tier_low = PaymentApprovalTier.objects.create(
            name='Low', min_amount=Decimal('0'), max_amount=Decimal('10000'),
            workflow_config=self.wf_low, order=1,
        )
        self.tier_mid = PaymentApprovalTier.objects.create(
            name='Mid', min_amount=Decimal('10000.01'), max_amount=Decimal('100000'),
            workflow_config=self.wf_mid, order=2,
        )
        self.tier_high = PaymentApprovalTier.objects.create(
            name='High', min_amount=Decimal('100000.01'), max_amount=None,
            workflow_config=self.wf_high, order=3,
        )

    def test_lower_bound_of_tier(self):
        tier = PaymentApprovalTier.resolve_for_amount(Decimal('0'))
        self.assertEqual(tier, self.tier_low)

    def test_upper_bound_of_tier(self):
        tier = PaymentApprovalTier.resolve_for_amount(Decimal('10000'))
        self.assertEqual(tier, self.tier_low)

    def test_mid_range_amount(self):
        tier = PaymentApprovalTier.resolve_for_amount(Decimal('50000'))
        self.assertEqual(tier, self.tier_mid)

    def test_unbounded_top_tier(self):
        tier = PaymentApprovalTier.resolve_for_amount(Decimal('999999999'))
        self.assertEqual(tier, self.tier_high)

    def test_no_matching_tier_raises_value_error(self):
        self.tier_low.delete()
        self.tier_mid.delete()
        self.tier_high.delete()
        with self.assertRaises(ValueError):
            PaymentApprovalTier.resolve_for_amount(Decimal('5000'))

    def test_inactive_tier_is_ignored(self):
        self.tier_low.is_active = False
        self.tier_low.save()
        with self.assertRaises(ValueError):
            PaymentApprovalTier.resolve_for_amount(Decimal('5000'))

    def test_overlapping_tiers_use_order_precedence(self):
        """
        When tiers overlap in range, resolve_for_amount() picks the first match by
        ascending `order` (lowest order wins) - not by range specificity.
        """
        overlapping_tier = PaymentApprovalTier.objects.create(
            name='Overlap-Low-Order', min_amount=Decimal('0'), max_amount=Decimal('1000000'),
            workflow_config=self.wf_high, order=0,
        )
        tier = PaymentApprovalTier.resolve_for_amount(Decimal('5000'))
        self.assertEqual(tier, overlapping_tier)

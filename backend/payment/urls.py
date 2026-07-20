from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SupplierViewSet, SourceDocumentViewSet, PaymentVoucherViewSet,
    PaymentApprovalTierViewSet, FixedAssetViewSet,
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'documents', SourceDocumentViewSet, basename='sourcedocument')
router.register(r'vouchers', PaymentVoucherViewSet, basename='paymentvoucher')
router.register(r'approval-tiers', PaymentApprovalTierViewSet, basename='paymentapprovaltier')
router.register(r'assets', FixedAssetViewSet, basename='fixedasset')

urlpatterns = [
    path('', include(router.urls)),
]

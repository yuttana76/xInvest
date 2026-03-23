from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowConfigViewSet, RequestViewSet

router = DefaultRouter()
router.register(r'configs', WorkflowConfigViewSet)
router.register(r'requests', RequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

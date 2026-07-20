from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkflowConfigViewSet, RequestViewSet, RequestSubjectViewSet

router = DefaultRouter()
router.register(r'configs', WorkflowConfigViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'subjects', RequestSubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]

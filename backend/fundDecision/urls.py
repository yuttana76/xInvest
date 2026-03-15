from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FundViewSet, NewsArticleViewSet

router = DefaultRouter()
router.register(r'funds', FundViewSet, basename='fund')
router.register(r'news', NewsArticleViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]

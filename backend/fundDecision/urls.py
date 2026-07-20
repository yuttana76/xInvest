from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsArticleViewSet
# from .views import SmartFundChatView  # disabled, see ai_service.py

router = DefaultRouter()
router.register(r'news', NewsArticleViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
    # path('chat/', SmartFundChatView.as_view(), name='fund-chat'),  # disabled
]

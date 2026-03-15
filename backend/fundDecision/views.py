from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Fund, NewsArticle
from .serializers import FundDetailSerializer, NewsArticleSerializer

class FundViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Fund.objects.all().prefetch_related('ai_insights')
    serializer_class = FundDetailSerializer

    # เพิ่มระบบ Search/Filter เบื้องต้น
    def get_queryset(self):
        queryset = Fund.objects.all().prefetch_related('ai_insights')
        category = self.request.query_params.get('category')
        ticker = self.request.query_params.get('ticker')
        
        if category:
            queryset = queryset.filter(fund_category=category)
        if ticker:
            queryset = queryset.filter(fundCode=ticker)
            
        return queryset

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.all().prefetch_related('related_funds')
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = NewsArticle.objects.all().prefetch_related('related_funds')
        ticker = self.request.query_params.get('ticker')
        if ticker:
            queryset = queryset.filter(related_funds__fundCode=ticker)
        return queryset
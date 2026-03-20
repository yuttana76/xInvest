from django.shortcuts import render
from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import FundInfo, NewsArticle
from .serializers import FundDetailSerializer, FundListSerializer, NewsArticleSerializer

class FundInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for FundInfo with separate serializers for list and detail views.
    List returns basic info + sentiment analysis.
    Detail returns all info + holdings + analysis + all insights.
    """
    lookup_field = 'fundCode'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FundListSerializer
        return FundDetailSerializer

    def get_queryset(self):
        queryset = FundInfo.objects.all().prefetch_related(
            'ai_insights', 'holdings', 'related_news','fund_analysis'
        )

        category = self.request.query_params.get('category')
        ticker = self.request.query_params.get('')


        if category:
            queryset = queryset.filter(fund_category=category)
        if ticker:
            queryset = queryset.filter(fundCode=ticker)

        return queryset

    # แคชหน้า List เป็นเวลา 2 ชั่วโมง (7200 วินาที)
    @method_decorator(cache_page(60 * 60 * 2, key_prefix="fund_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # แคชหน้า Detail เป็นเวลา 2 ชั่วโมง (7200 วินาที)
    # 1 minute
    # @method_decorator(cache_page(60, key_prefix="fund_detail"))
    # 1 hour
    # @method_decorator(cache_page(60 * 60, key_prefix="fund_detail"))
    # 1 day
    # @method_decorator(cache_page(60 * 60 * 24, key_prefix="fund_detail"))
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.all().prefetch_related('related_funds')
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = NewsArticle.objects.all().prefetch_related('related_funds')
        ticker = self.request.query_params.get('ticker')
        if ticker:
            queryset = queryset.filter(related_funds__fundCode=ticker)
        return queryset
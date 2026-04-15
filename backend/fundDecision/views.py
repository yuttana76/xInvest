from django.shortcuts import render
from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import NewsArticle
from .serializers import NewsArticleSerializer

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.all().prefetch_related('related_funds')
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = NewsArticle.objects.filter(published_status=True).order_by('-published_at').prefetch_related('related_funds')
        ticker = self.request.query_params.get('ticker')
        relate_product = self.request.query_params.get('relate_product')

        

        if ticker:
            queryset = queryset.filter(related_funds__fundCode=ticker)
        if relate_product:
            from django.db.models import Q
            products = relate_product.split(',')
            query = Q()
            for product in products:
                query |= Q(relate_product__icontains=product.strip())
            queryset = queryset.filter(query)
            
        return queryset
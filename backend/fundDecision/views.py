from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import NewsArticle
from .ai_service import SmartFundAIService
from .serializers import NewsArticleSerializer

class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer

    def get_queryset(self):
        queryset = NewsArticle.objects.filter(published_status=True).order_by('-published_at')
        ticker = self.request.query_params.get('ticker')
        relate_product = self.request.query_params.get('relate_product')

        if ticker:
            queryset = queryset.filter(related_funds__icontains=ticker)
        if relate_product:
            from django.db.models import Q
            products = relate_product.split(',')
            query = Q()
            for product in products:
                query |= Q(relate_product__icontains=product.strip())
            queryset = queryset.filter(query)
            
        return queryset
class SmartFundChatView(APIView):
    """
    API สำหรับถาม-ตอบข้อมูลกองทุนอัจฉริยะ (RAG)
    """
    def post(self, request):
        fund_code = request.data.get('fund_code')
        query = request.data.get('query')
        
        import logging
        logger = logging.getLogger(__name__)

        if not query:
            return Response(
                {"error": "Missing query"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            logger.info(f"SmartFundChatView: querying fund_code={fund_code} with '{query}'")
            smart_ai = SmartFundAIService()
            answer = smart_ai.query_fund(query=query, fund_code=fund_code)
            
            return Response({
                "fund_code": fund_code,
                "query": query,
                "answer": answer
            })
        except Exception as e:
            logger.error(f"Error in SmartFundChatView: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

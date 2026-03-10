from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Fund, FundAnalysis
from .serializers import FundSerializer
from .services import FundAggregatorService, AISentimentService

class FundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows funds to be viewed or searched.
    """
    queryset = Fund.objects.all().select_related('analysis')
    serializer_class = FundSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['fund_code', 'fund_name_th', 'fund_name_en', 'fund_policy']

    @action(detail=True, methods=['post'])
    def refresh_analysis(self, request, pk=None):
        """
        Triggers a refresh of fund data and AI analysis for a specific fund.
        """
        fund = self.get_object()
        
        # 1. Fetch latest data
        raw_data = FundAggregatorService.fetch_fund_data(fund.fund_code)
        if not raw_data:
            return Response({"error": "Failed to fetch fund data"}, status=400)

        # 2. Analyze with AI (Mocking news for now)
        ai_service = AISentimentService()
        mock_news = f"Market is reacting to recent economic data affecting {fund.fund_code}."
        ai_result = ai_service.analyze_news(mock_news)

        # 3. Update or create analysis record
        analysis, created = FundAnalysis.objects.update_or_create(
            fund=fund,
            defaults={
                'analysis_data': {
                    'raw_holdings': raw_data.get('holdings', []),
                    'sector_allocation': raw_data.get('sector_allocation', {}),
                    'expert_note': ai_result.get('note', '')
                },
                'sentiment_score': ai_result.get('sentiment', 0.0)
            }
        )

        return Response({"status": "Analysis refreshed", "sentiment": analysis.sentiment_score})

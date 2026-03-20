from rest_framework import serializers
from .models import FundInfo, AIInsight, NewsArticle, FundAnalysis, FundHoldingAsset

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'

class FundAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundAnalysis
        fields = [
            'id',
            'standard_deviation',
            'treynor_ratio',
            'sortino_ratio',
            'information_ratio',
            'capture_ratio_up',
            'capture_ratio_down',
            'sentiment_score',
            'sentiment_summary',
            'sentiment_impact_level',
            'last_calculated',
            'created_at',
            'updated_at',
            'createBy',
            'updateBy',
        ]

class AIInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsight
        fields = '__all__'

class FundHoldingAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundHoldingAsset
        fields = '__all__'

class FundListSerializer(serializers.ModelSerializer):
    """Serializer for fund listing with sentiment from FundAnalysis"""
    sentiment_score = serializers.FloatField(source='fund_analysis.sentiment_score', read_only=True)
    sentiment_summary = serializers.CharField(source='fund_analysis.sentiment_summary', read_only=True)
    sentiment_impact_level = serializers.CharField(source='fund_analysis.sentiment_impact_level', read_only=True)

    class Meta:
        model = FundInfo
        fields = [
            'id', 'fundCode', 'name_th', 'name_en', 'fund_category', 
            'risk_level', 'is_dividend', 'sentiment_score', 
            'sentiment_summary', 'sentiment_impact_level',
            'created_at', 'updated_at'
        ]

class FundDetailSerializer(serializers.ModelSerializer):
    """Serializer for fund details including holdings, analysis, insights and approved news."""
    holdings = FundHoldingAssetSerializer(many=True, read_only=True)
    # fund_analysis = FundAnalysisSerializer(read_only=True)
    fund_analysis = FundAnalysisSerializer(many=True,read_only=True)
    ai_insights = AIInsightSerializer(many=True, read_only=True)
    approved_news = serializers.SerializerMethodField()

    # Keeping extra metrics for functionality
    latest_insight = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = FundInfo
        fields = '__all__'

    def get_approved_news(self, obj):
        """Published news where this fund is in related_funds and published_status=True"""
        news_qs = obj.related_news.filter(published_status=True).order_by('-published_at')
        return NewsArticleSerializer(news_qs, many=True).data

    def get_latest_insight(self, obj):
        insight = obj.ai_insights.order_by('-created_at').first()
        if insight:
            return {
                "content": insight.content, 
                "sentiment": insight.sentiment_score,
                "confidence": insight.confidence_score,
                "type": insight.insight_type
            }
        return None

    def get_metrics(self, obj):
        from .utils import calculate_fund_metrics
        return calculate_fund_metrics(obj.id)
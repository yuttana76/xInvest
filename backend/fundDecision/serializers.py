from rest_framework import serializers
from .models import Fund, AIInsight, NewsArticle

class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticle
        fields = '__all__'

class FundDetailSerializer(serializers.ModelSerializer):
    latest_insight = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Fund
        fields = '__all__'

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
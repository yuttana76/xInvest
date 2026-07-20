from rest_framework import serializers
from .models import AIInsight, NewsArticle, FundAnalysis

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

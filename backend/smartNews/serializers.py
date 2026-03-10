from rest_framework import serializers
from .models import Fund, FundAnalysis

class FundAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundAnalysis
        fields = ['analysis_data', 'sentiment_score', 'last_analyzed']

class FundSerializer(serializers.ModelSerializer):
    analysis = FundAnalysisSerializer(read_only=True)

    class Meta:
        model = Fund
        fields = [
            'id', 'fund_code', 'amc_code', 'fund_name_th', 'fund_name_en',
            'fund_policy', 'tax_type', 'fif_flag', 'dividend_flag',
            'registration_date', 'fund_risk_level', 'analysis'
        ]

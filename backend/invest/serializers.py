from rest_framework import serializers
from .models import (
    Investor, InvestorAccount, AccountBalance, Marketing, 
    BondAccount, PrivateFundAccount, PrivateFundBalance,
    MarketingGroup, ExternalAgent
)

class MarketingGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingGroup
        fields = '__all__'

class ExternalAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalAgent
        fields = '__all__'

class MarketingSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.groupName', read_only=True)
    supervisor_name = serializers.CharField(source='supervisor.fullName', read_only=True)
    class Meta:
        model = Marketing
        fields = '__all__'

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

class MarketingInvestorSerializer(serializers.ModelSerializer):
    mf_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    bond_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    pf_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_profit = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    mf_profit = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    pf_profit = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Investor
        fields = [
            'id', 'custCode', 'fullNameEn', 'fullNameTh', 'status', 
            'mf_amount', 'bond_amount', 'pf_amount', 'total_amount', 
            'total_profit', 'mf_profit', 'pf_profit',
            'suitDate', 'cardExpireDate', 'nextKycDate',
            'created_at', 'updated_at'
        ]

class AccountBalanceSerializer(serializers.ModelSerializer):
    AccountID = serializers.CharField(source='accountID.accountID', read_only=True)
    accountID = serializers.CharField(source='accountID.accountID', read_only=True)
    class Meta:
        model = AccountBalance
        fields = '__all__'

class InvestorAccountSerializer(serializers.ModelSerializer):
    balances = AccountBalanceSerializer(many=True, read_only=True)
    marketing_name = serializers.CharField(source='marketing.fullName', read_only=True)
    agent_name = serializers.CharField(source='referred_by_agent.fullName', read_only=True)
    class Meta:
        model = InvestorAccount
        fields = '__all__'

class BondAccountSerializer(serializers.ModelSerializer):
    marketing_name = serializers.CharField(source='marketing.fullName', read_only=True)
    agent_name = serializers.CharField(source='referred_by_agent.fullName', read_only=True)
    class Meta:
        model = BondAccount
        fields = '__all__'

class PrivateFundBalanceSerializer(serializers.ModelSerializer):
    AccountID = serializers.CharField(source='accountID.accountID', read_only=True)
    accountID = serializers.CharField(source='accountID.accountID', read_only=True)
    class Meta:
        model = PrivateFundBalance
        fields = '__all__'

class PrivateFundAccountSerializer(serializers.ModelSerializer):
    privateFundBalances = PrivateFundBalanceSerializer(many=True, read_only=True, source='private_fund_balances')
    marketing_name = serializers.CharField(source='marketing.fullName', read_only=True)
    agent_name = serializers.CharField(source='referred_by_agent.fullName', read_only=True)
    class Meta:
        model = PrivateFundAccount
        fields = '__all__'

class PerformanceChartSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_market_value = serializers.FloatField()
    total_gain = serializers.FloatField()
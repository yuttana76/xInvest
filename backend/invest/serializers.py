from rest_framework import serializers
from .models import Investor, InvestorAccount, AccountBalance, ICLicense, BondAccount, PrivateFundAccount, PrivateFundBalance

class ICLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICLicense
        fields = '__all__'

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

class AccountBalanceSerializer(serializers.ModelSerializer):
    AccountID = serializers.CharField(source='accountID.accountID', read_only=True)
    accountID = serializers.CharField(source='accountID.accountID', read_only=True)
    class Meta:
        model = AccountBalance
        fields = '__all__'

class InvestorAccountSerializer(serializers.ModelSerializer):
    balances = AccountBalanceSerializer(many=True, read_only=True)
    class Meta:
        model = InvestorAccount
        fields = '__all__'

class BondAccountSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = PrivateFundAccount
        fields = '__all__'

from rest_framework import serializers
from .models import Investor, InvestorAccount, AccountBalance, ICLicense

class ICLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICLicense
        fields = '__all__'

class InvestorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        fields = '__all__'

class InvestorAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorAccount
        fields = '__all__'

class AccountBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountBalance
        fields = '__all__'

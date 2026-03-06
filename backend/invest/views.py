from rest_framework import generics, permissions
from .models import Investor, InvestorAccount, AccountBalance, ICLicense
from .serializers import InvestorSerializer, InvestorAccountSerializer, AccountBalanceSerializer, ICLicenseSerializer

class InvestorDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()
    lookup_field = 'custCode'

class InvestorAccountListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvestorAccountSerializer

    def get_queryset(self):
        cust_code = self.kwargs['custCode']
        return InvestorAccount.objects.filter(custCode__custCode=cust_code)

class AccountBalanceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        cust_code = self.kwargs['custCode']
        return AccountBalance.objects.filter(accountID__custCode__custCode=cust_code)

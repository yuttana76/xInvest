from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
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

class InvestorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()

class InvestorInquiryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        comp_code = request.data.get('compCode')
        cust_code = request.data.get('custCode')

        if not comp_code or not cust_code:
            return Response({"error": "compCode and custCode are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            investor = Investor.objects.get(compCode=comp_code, custCode=cust_code)
            accounts = investor.accounts.all()
            balances = AccountBalance.objects.filter(accountID__in=accounts)

            return Response({
                "profile": InvestorSerializer(investor).data,
                "accounts": InvestorAccountSerializer(accounts, many=True).data,
                "balances": AccountBalanceSerializer(balances, many=True).data
            }, status=status.HTTP_200_OK)
        except Investor.DoesNotExist:
            return Response({"error": "Investor not found"}, status=status.HTTP_404_NOT_FOUND)

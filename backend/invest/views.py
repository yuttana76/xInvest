from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Investor, InvestorAccount, AccountBalance, ICLicense
from .serializers import InvestorSerializer, InvestorAccountSerializer, AccountBalanceSerializer, ICLicenseSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class InvestorDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()
    lookup_field = 'custCode'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Investor.objects.all()
        return Investor.objects.filter(user=user)

class InvestorAccountListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    serializer_class = InvestorAccountSerializer

    def get_queryset(self):
        user = self.request.user
        cust_code = self.kwargs['custCode']
        
        # Security check: Does this cust_code belong to the user?
        if not (user.is_staff or user.is_superuser):
            if not hasattr(user, 'investor_profile') or user.investor_profile.custCode != cust_code:
                return InvestorAccount.objects.none()
                
        return InvestorAccount.objects.filter(custCode__custCode=cust_code)

class AccountBalanceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    serializer_class = AccountBalanceSerializer

    def get_queryset(self):
        user = self.request.user
        cust_code = self.kwargs['custCode']
        
        # Security check
        if not (user.is_staff or user.is_superuser):
            if not hasattr(user, 'investor_profile') or user.investor_profile.custCode != cust_code:
                return AccountBalance.objects.none()

        return AccountBalance.objects.filter(accountID__custCode__custCode=cust_code)

class InvestorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser,permissions.IsAuthenticated]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()

class InvestorInquiryView(APIView):
    permission_classes = [permissions.IsAdminUser,permissions.IsAuthenticated]

    @extend_schema(
        summary="Inquiry Investor Data",
        description="Get full investor profile, accounts, and balances using compCode and custCode.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "compCode": {"type": "string", "example": "COMP001"},
                    "custCode": {"type": "string", "example": "CUST001"}
                },
                "required": ["compCode", "custCode"]
            }
        },
        responses={200: InvestorSerializer}, # You can improve this with a custom response serializer
        tags=["Investments"]
    )
    def post(self, request):
        comp_code = request.data.get('compCode')
        cust_code = request.data.get('custCode')

        if not comp_code or not cust_code:
            return Response({"error": "compCode and custCode are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Security check: Does this cust_code belong to the user?
        if not (request.user.is_staff or request.user.is_superuser):
            if not hasattr(request.user, 'investor_profile') or request.user.investor_profile.custCode != cust_code:
                return Response({"error": "You do not have permission to access this investor's data"}, status=status.HTTP_403_FORBIDDEN)

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

class InvestorMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'investor_profile'):
            return Response({"error": "No investor profile associated with this user"}, status=status.HTTP_404_NOT_FOUND)
            
        investor = request.user.investor_profile
        accounts = investor.accounts.all()
        balances = AccountBalance.objects.filter(accountID__in=accounts)

        return Response({
            "profile": InvestorSerializer(investor).data,
            "accounts": InvestorAccountSerializer(accounts, many=True).data,
            "balances": AccountBalanceSerializer(balances, many=True).data
        }, status=status.HTTP_200_OK)

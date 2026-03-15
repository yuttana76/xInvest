from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import pandas as pd
import io
from django.http import HttpResponse
from .models import (
    Investor, InvestorAccount, AccountBalance, Marketing, 
    BondAccount, PrivateFundAccount, PrivateFundBalance, 
    PerformanceMFAccountBalance, PerformancePrivateFundBalance,
    MarketingGroup, ExternalAgent
)
from .serializers import (
    InvestorSerializer, InvestorAccountSerializer, AccountBalanceSerializer, 
    MarketingSerializer, BondAccountSerializer, PrivateFundAccountSerializer, 
    PrivateFundBalanceSerializer, PerformanceChartSerializer,
    MarketingGroupSerializer, ExternalAgentSerializer,
    MarketingInvestorSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .tasks import run_daily_fundconnext_etl_trans, run_daily_fundconnext_etl_performance_mf_balance,run_daily_fundconnext_etl_current_mf_balance
from datetime import datetime, timedelta
from django.db.models import Sum, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.core.cache import cache
import logging
from .permissions import IsOperator, IsMarketing, IsAgent
from django.db import models
from .models import MFTransaction
from django.db.models import Sum, Value, DecimalField

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class InvestorListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser,IsAuthenticated]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()
    pagination_class = StandardResultsSetPagination

class OperatorInvestorListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOperator]
    serializer_class = MarketingInvestorSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Investor.objects.all().order_by('-created_at', '-updated_at')
        
        # Annotate with global aggregate amounts for Active accounts
        queryset = queryset.annotate(
            mf_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active')), Value(0, output_field=DecimalField())),
            bond_amount=Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active')), Value(0, output_field=DecimalField())),
            pf_amount=Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active')), Value(0, output_field=DecimalField()))
        ).annotate(
            total_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active')), Value(0, output_field=DecimalField())) + 
                         Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active')), Value(0, output_field=DecimalField())) + 
                         Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active')), Value(0, output_field=DecimalField())),
            mf_profit=Coalesce(Sum(models.F('accounts__balances__amount') - (models.F('accounts__balances__unitBalance') * models.F('accounts__balances__averageCost')), filter=Q(accounts__status='Active')), Value(0, output_field=DecimalField())),
            pf_profit=Coalesce(Sum(models.F('private_fund_accounts__private_fund_balances__amount') - (models.F('private_fund_accounts__private_fund_balances__unitBalance') * models.F('private_fund_accounts__private_fund_balances__averageCost')), filter=Q(private_fund_accounts__status='Active')), Value(0, output_field=DecimalField()))
        ).annotate(
            total_profit=models.F('mf_profit') + models.F('pf_profit')
        )

        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(fullNameTh__icontains=search) | 
                Q(fullNameEn__icontains=search) |
                Q(custCode__icontains=search)
            )
        return queryset

class OperatorInvestorDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOperator]
    serializer_class = InvestorSerializer
    queryset = Investor.objects.all()
    lookup_field = 'pk'

class OperatorDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOperator]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Block 1
        total_customers = Investor.objects.count()
        new_today = Investor.objects.filter(created_at__gte=today_start).count()
        modified_today = Investor.objects.filter(updated_at__gte=today_start).count()
        
        # Block 2 (Current Month Expirations)
        # Django __month and __year lookup
        suit_expired_this_month = Investor.objects.filter(suitDate__month=now.month, suitDate__year=now.year).count()
        card_expired_this_month = Investor.objects.filter(cardExpireDate__month=now.month, cardExpireDate__year=now.year).count()
        kyc_expired_this_month = Investor.objects.filter(nextKycDate__month=now.month, nextKycDate__year=now.year).count()
        
        # Today's lists
        # Show top 10 new and modified today
        new_customers_list = InvestorSerializer(Investor.objects.filter(created_at__gte=today_start).order_by('-created_at')[:10], many=True).data
        modified_today_qs = Investor.objects.filter(updated_at__gte=today_start).exclude(created_at__gte=today_start).order_by('-updated_at')
        modified_customers_list = InvestorSerializer(modified_today_qs[:10], many=True).data
        
        return Response({
            "stats": {
                "totalCustomers": total_customers,
                "newToday": new_today,
                "modifiedToday": modified_today,
                "suitExpiredMonth": suit_expired_this_month,
                "cardExpiredMonth": card_expired_this_month,
                "kycExpiredMonth": kyc_expired_this_month,
            },
            "newCustomers": new_customers_list,
            "modifiedCustomers": modified_customers_list
        })

class MarketingDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsMarketing]

    def get(self, request):
        try:
            profile = Marketing.objects.get(user=request.user)
            # Filter investors who have at least one account assigned to this marketing profile
            investors = Investor.objects.filter(
                Q(accounts__marketing=profile) | 
                Q(bond_accounts__marketing=profile) | 
                Q(private_fund_accounts__marketing=profile)
            ).distinct()
            
            total_investors = investors.count()
            
            # AUM Totals
            mf_aum = AccountBalance.objects.filter(accountID__marketing=profile, accountID__status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            bond_aum = BondAccount.objects.filter(marketing=profile, status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            pf_aum = PrivateFundBalance.objects.filter(accountID__marketing=profile, accountID__status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_aum = mf_aum + bond_aum + pf_aum
            
            # AUM this month (based on account creation or investor joining? 
            # I'll stick to investors who joined this month and have accounts with this marketing)
            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            mf_aum_month = AccountBalance.objects.filter(accountID__marketing=profile, accountID__status='Active', accountID__custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            bond_aum_month = BondAccount.objects.filter(marketing=profile, status='Active', custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            pf_aum_month = PrivateFundBalance.objects.filter(accountID__marketing=profile, accountID__status='Active', accountID__custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_aum_month = mf_aum_month + bond_aum_month + pf_aum_month

            # Transactions (SUB) this month by Product
            mf_sub_this_month = MFTransaction.objects.filter(
                accountID__marketing=profile,
                transactionCode='SUB',
                transactionDateTime__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            bond_sub_this_month = BondAccount.objects.filter(
                marketing=profile,
                status='Active',
                fromDate__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            pf_sub_this_month = PrivateFundBalance.objects.filter(
                accountID__marketing=profile,
                accountID__status='Active',
                accountID__openDate__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            total_sub_this_month = mf_sub_this_month + bond_sub_this_month + pf_sub_this_month

            # Compliance alerts (Current Month Expirations for MY investors)
            alerts = {
                "suitability": investors.filter(suitDate__month=now.month, suitDate__year=now.year).count(),
                "card": investors.filter(cardExpireDate__month=now.month, cardExpireDate__year=now.year).count(),
                "kyc": investors.filter(nextKycDate__month=now.month, nextKycDate__year=now.year).count(),
            }

            # Onboarding status
            status_counts = investors.values('status').annotate(count=Sum(Value(1))).order_by('status')
            
            return Response({
                "profile": MarketingSerializer(profile).data,
                "stats": {
                    "totalInvestors": total_investors,
                    "totalAUM": total_aum,
                    "aumThisMonth": total_aum_month,
                    "mfAUM": mf_aum,
                    "bondAUM": bond_aum,
                    "pfAUM": pf_aum,
                    "subThisMonth": total_sub_this_month,
                    "mfSubThisMonth": mf_sub_this_month,
                    "bondSubThisMonth": bond_sub_this_month,
                    "pfSubThisMonth": pf_sub_this_month,
                },
                "alerts": alerts,
                "statusDistribution": {item['status']: item['count'] for item in status_counts}
            })
        except Marketing.DoesNotExist:
            return Response({"error": "Marketing profile not found"}, status=status.HTTP_404_NOT_FOUND)

class AgentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]

    def get(self, request):
        try:
            profile = ExternalAgent.objects.get(user=request.user)
            # Filter investors who have at least one account referred by this agent
            investors = Investor.objects.filter(
                Q(accounts__referred_by_agent=profile) | 
                Q(bond_accounts__referred_by_agent=profile) | 
                Q(private_fund_accounts__referred_by_agent=profile)
            ).distinct()
            
            total_investors = investors.count()
            
            # AUM Totals for this Agent's referrals
            mf_aum = AccountBalance.objects.filter(accountID__referred_by_agent=profile, accountID__status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            bond_aum = BondAccount.objects.filter(referred_by_agent=profile, status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            pf_aum = PrivateFundBalance.objects.filter(accountID__referred_by_agent=profile, accountID__status='Active').aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_aum = mf_aum + bond_aum + pf_aum
            
            # AUM this month
            now = timezone.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            mf_aum_month = AccountBalance.objects.filter(accountID__referred_by_agent=profile, accountID__status='Active', accountID__custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            bond_aum_month = BondAccount.objects.filter(referred_by_agent=profile, status='Active', custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            pf_aum_month = PrivateFundBalance.objects.filter(accountID__referred_by_agent=profile, accountID__status='Active', accountID__custCode__created_at__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
            
            total_aum_month = mf_aum_month + bond_aum_month + pf_aum_month

            # Transactions (SUB) this month by Product
            mf_sub_this_month = MFTransaction.objects.filter(
                accountID__referred_by_agent=profile,
                transactionCode='SUB',
                transactionDateTime__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            bond_sub_this_month = BondAccount.objects.filter(
                referred_by_agent=profile,
                status='Active',
                fromDate__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            pf_sub_this_month = PrivateFundBalance.objects.filter(
                accountID__referred_by_agent=profile,
                accountID__status='Active',
                accountID__openDate__gte=month_start
            ).aggregate(Sum('amount'))['amount__sum'] or 0

            total_sub_this_month = mf_sub_this_month + bond_sub_this_month + pf_sub_this_month

            # Compliance alerts (Current Month Expirations for referral investors)
            alerts = {
                "suitability": investors.filter(suitDate__month=now.month, suitDate__year=now.year).count(),
                "card": investors.filter(cardExpireDate__month=now.month, cardExpireDate__year=now.year).count(),
                "kyc": investors.filter(nextKycDate__month=now.month, nextKycDate__year=now.year).count(),
            }

            # Onboarding status
            status_counts = investors.values('status').annotate(count=Sum(Value(1))).order_by('status')
            
            return Response({
                "profile": ExternalAgentSerializer(profile).data,
                "stats": {
                    "totalInvestors": total_investors,
                    "totalAUM": total_aum,
                    "aumThisMonth": total_aum_month,
                    "mfAUM": mf_aum,
                    "bondAUM": bond_aum,
                    "pfAUM": pf_aum,
                    "subThisMonth": total_sub_this_month,
                    "mfSubThisMonth": mf_sub_this_month,
                    "bondSubThisMonth": bond_sub_this_month,
                    "pfSubThisMonth": pf_sub_this_month,
                },
                "alerts": alerts,
                "statusDistribution": {item['status']: item['count'] for item in status_counts}
            })
        except ExternalAgent.DoesNotExist:
            return Response({"error": "Agent profile not found"}, status=status.HTTP_404_NOT_FOUND)

class OperatorInvestorExportView(APIView):
    permission_classes = [IsAuthenticated, IsOperator]

    @extend_schema(
        summary="Export investors to Excel",
        description="Admin/Operator only endpoint to export all investors to an Excel file."
    )
    def get(self, request):
        investors = Investor.objects.all().prefetch_related('accounts__marketing', 'bond_accounts__marketing', 'private_fund_accounts__marketing').order_by('-created_at')
        data = []
        for inv in investors:
            # Get marketing from any account
            mkt = inv.accounts.filter(marketing__isnull=False).first() or \
                  inv.bond_accounts.filter(marketing__isnull=False).first() or \
                  inv.private_fund_accounts.filter(marketing__isnull=False).first()
            
            agent = inv.accounts.filter(referred_by_agent__isnull=False).first() or \
                    inv.bond_accounts.filter(referred_by_agent__isnull=False).first() or \
                    inv.private_fund_accounts.filter(referred_by_agent__isnull=False).first()

            data.append({
                "Investor Name": inv.fullNameTh,
                "Mobile": inv.mobile,
                "Email": inv.email,
                "Status": inv.status,
                "Marketing": mkt.marketing.fullName if mkt and mkt.marketing else "",
                "Agent": agent.referred_by_agent.fullName if agent and agent.referred_by_agent else ""
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        # Use pandas ExcelWriter with openpyxl
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Investors')
        
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="investors.xlsx"'
        return response

class MarketingInvestorListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsMarketing]
    serializer_class = MarketingInvestorSerializer
    
    def get_queryset(self):
        try:
            marketing_profile = Marketing.objects.get(user=self.request.user)
            # Filter investors who have at least one account assigned to this marketing profile
            queryset = Investor.objects.filter(
                Q(accounts__marketing=marketing_profile) | 
                Q(bond_accounts__marketing=marketing_profile) | 
                Q(private_fund_accounts__marketing=marketing_profile)
            ).distinct().order_by('-created_at', '-updated_at')
            
            # Annnotate with aggregate amounts for Active accounts belonging to this marketing
            queryset = queryset.annotate(
                mf_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active', accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())),
                bond_amount=Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active', bond_accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())),
                pf_amount=Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active', private_fund_accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField()))
            ).annotate(
                total_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active', accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())) + 
                             Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active', bond_accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())) + 
                             Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active', private_fund_accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())),
                mf_profit=Coalesce(Sum(models.F('accounts__balances__amount') - (models.F('accounts__balances__unitBalance') * models.F('accounts__balances__averageCost')), filter=Q(accounts__status='Active', accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField())),
                pf_profit=Coalesce(Sum(models.F('private_fund_accounts__private_fund_balances__amount') - (models.F('private_fund_accounts__private_fund_balances__unitBalance') * models.F('private_fund_accounts__private_fund_balances__averageCost')), filter=Q(private_fund_accounts__status='Active', private_fund_accounts__marketing=marketing_profile)), Value(0, output_field=DecimalField()))
            ).annotate(
                total_profit=models.F('mf_profit') + models.F('pf_profit')
            )
            
            status_filter = self.request.query_params.get('status')
            search = self.request.query_params.get('search')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if search:
                queryset = queryset.filter(
                    Q(fullNameTh__icontains=search) | 
                    Q(fullNameEn__icontains=search) |
                    Q(custCode__icontains=search)
                )
            
            return queryset
        except Marketing.DoesNotExist:
            return Investor.objects.none()

class AgentInvestorListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAgent]
    serializer_class = MarketingInvestorSerializer
    
    def get_queryset(self):
        try:
            agent_profile = ExternalAgent.objects.get(user=self.request.user)
            # Filter investors who have at least one account referred by this agent
            queryset = Investor.objects.filter(
                Q(accounts__referred_by_agent=agent_profile) | 
                Q(bond_accounts__referred_by_agent=agent_profile) | 
                Q(private_fund_accounts__referred_by_agent=agent_profile)
            ).distinct().order_by('-created_at', '-updated_at')
            
            queryset = queryset.annotate(
                mf_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active', accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())),
                bond_amount=Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active', bond_accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())),
                pf_amount=Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active', private_fund_accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField()))
            ).annotate(
                total_amount=Coalesce(Sum('accounts__balances__amount', filter=Q(accounts__status='Active', accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())) + 
                             Coalesce(Sum('bond_accounts__amount', filter=Q(bond_accounts__status='Active', bond_accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())) + 
                             Coalesce(Sum('private_fund_accounts__private_fund_balances__amount', filter=Q(private_fund_accounts__status='Active', private_fund_accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())),
                mf_profit=Coalesce(Sum(models.F('accounts__balances__amount') - (models.F('accounts__balances__unitBalance') * models.F('accounts__balances__averageCost')), filter=Q(accounts__status='Active', accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField())),
                pf_profit=Coalesce(Sum(models.F('private_fund_accounts__private_fund_balances__amount') - (models.F('private_fund_accounts__private_fund_balances__unitBalance') * models.F('private_fund_accounts__private_fund_balances__averageCost')), filter=Q(private_fund_accounts__status='Active', private_fund_accounts__referred_by_agent=agent_profile)), Value(0, output_field=DecimalField()))
            ).annotate(
                total_profit=models.F('mf_profit') + models.F('pf_profit')
            )
            
            status_filter = self.request.query_params.get('status')
            search = self.request.query_params.get('search')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            if search:
                queryset = queryset.filter(
                    Q(fullNameTh__icontains=search) | 
                    Q(fullNameEn__icontains=search) |
                    Q(custCode__icontains=search)
                )
            
            return queryset
        except ExternalAgent.DoesNotExist:
            return Investor.objects.none()

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
            mf_accounts = investor.accounts.prefetch_related('balances').all()
            pf_accounts = investor.private_fund_accounts.prefetch_related('private_fund_balances').all()
            bond_accounts = investor.bond_accounts.all()

            return Response({
                "profile": InvestorSerializer(investor).data,
                "mfAccounts": InvestorAccountSerializer(mf_accounts, many=True).data,
                "privateFundAccounts": PrivateFundAccountSerializer(pf_accounts, many=True).data,
                "bondAccounts": BondAccountSerializer(bond_accounts, many=True).data
            }, status=status.HTTP_200_OK)
        except Investor.DoesNotExist:
            return Response({"error": "Investor not found"}, status=status.HTTP_404_NOT_FOUND)

class InvestorMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'investor_profile'):
            return Response({"error": "No investor profile associated with this user"}, status=status.HTTP_404_NOT_FOUND)
            
        investor = request.user.investor_profile
        mf_accounts = investor.accounts.prefetch_related('balances').all()
        pf_accounts = investor.private_fund_accounts.prefetch_related('private_fund_balances').all()
        bond_accounts = investor.bond_accounts.all()

        return Response({
            "profile": InvestorSerializer(investor).data,
            "mfAccounts": InvestorAccountSerializer(mf_accounts, many=True).data,
            "privateFundAccounts": PrivateFundAccountSerializer(pf_accounts, many=True).data,
            "bondAccounts": BondAccountSerializer(bond_accounts, many=True).data
        }, status=status.HTTP_200_OK)

class ETLManualTriggerViewTrans(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    @extend_schema(
        summary="Trigger FundConnext ETL manually",
        description="Admin only endpoint to trigger transaction ETL for FundConnext data.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "business_date": {"type": "string", "example": "20240101", "description": "Optional: YYYYMMDD format. Defaults to yesterday."},
                }
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        tags=["Admin ETL"]
    )
    def post(self, request):

        business_date_str = request.data.get('business_date')

        #Validate business_date_str format
        try:
            datetime.strptime(business_date_str, '%Y%m%d')
        except ValueError:
            return Response({"error": "Invalid business_date format. Must be YYYYMMDD."}, status=status.HTTP_400_BAD_REQUEST)   

        target_date = business_date_str if business_date_str else (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        logger.info(f"Manual trigger for FundConnext ETL for date: {target_date}")
        
        result = run_daily_fundconnext_etl_trans.delay(business_date_str)

        celery_task_id = []
        if result:
            celery_task_id.append(result.id)
        else:
            logger.error("Failed to trigger transaction ETL")

        if celery_task_id.__len__() > 0:
            return Response({
                "message": f"ETL task triggered for transaction successfully for business date {target_date}.",
                "status": "Task Queued",
                "celery_task_id": celery_task_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": f"ETL task failed to trigger for transaction for business date {target_date}.",
                "status": "Task Failed",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ETLManualTriggerViewCurrentBalance(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    @extend_schema(
        summary="Trigger FundConnext ETL manually",
        description="Admin only endpoint to trigger current MF balance ETL for FundConnext data.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "business_date": {"type": "string", "example": "20240101", "description": "Optional: YYYYMMDD format. Defaults to yesterday."},
                }
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        tags=["Admin ETL"]
    )
    def post(self, request):

        business_date_str = request.data.get('business_date')

        #Validate business_date_str format
        try:
            datetime.strptime(business_date_str, '%Y%m%d')
        except ValueError:
            return Response({"error": "Invalid business_date format. Must be YYYYMMDD."}, status=status.HTTP_400_BAD_REQUEST)   

        target_date = business_date_str if business_date_str else (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        logger.info(f"Manual trigger for FundConnext ETL for date: {target_date}")
        
        result1 =''
        result2 =''
        # result1 = run_daily_fundconnext_etl_trans.delay(business_date_str)
        # result2 = run_daily_fundconnext_etl_performance_mf_balance.delay(business_date_str)
        result3 = run_daily_fundconnext_etl_current_mf_balance.delay(business_date_str)

        celery_task_id = []
        if result1:
            celery_task_id.append(result1.id)
        else:
            logger.error("Failed to trigger transaction ETL")


        if result2:
            celery_task_id.append(result2.id)
        else:
            logger.error("Failed to trigger performance MF balance ETL")

        if result3:
            celery_task_id.append(result3.id)
        else:
            logger.error("Failed to trigger current MF balance ETL")

        if celery_task_id.__len__() > 0:
            return Response({
                "message": f"ETL task triggered for current MF balance successfully for business date {target_date}.",
                "status": "Task Queued",
                "celery_task_id": celery_task_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": f"ETL task failed to trigger for current MF balance for business date {target_date}.",
                "status": "Task Failed",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ETLManualTriggerViewPerformanceBalance(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]

    @extend_schema(
        summary="Trigger FundConnext ETL manually",
        description="Admin only endpoint to trigger performance MF balance ETL for FundConnext data.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "business_date": {"type": "string", "example": "20240101", "description": "Optional: YYYYMMDD format. Defaults to yesterday."},
                }
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        tags=["Admin ETL"]
    )
    def post(self, request):

        business_date_str = request.data.get('business_date')

        #Validate business_date_str format
        try:
            datetime.strptime(business_date_str, '%Y%m%d')
        except ValueError:
            return Response({"error": "Invalid business_date format. Must be YYYYMMDD."}, status=status.HTTP_400_BAD_REQUEST)   

        target_date = business_date_str if business_date_str else (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        logger.info(f"Manual trigger for FundConnext ETL for date: {target_date}")
        
        result = run_daily_fundconnext_etl_performance_mf_balance.delay(business_date_str)

        celery_task_id = []
        if result:
            celery_task_id.append(result.id)
        else:
            logger.error("Failed to trigger performance MF balance ETL")

        if celery_task_id.__len__() > 0:
            return Response({
                "message": f"ETL task triggered for performance MF balance successfully for business date {target_date}.",
                "status": "Task Queued",
                "celery_task_id": celery_task_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": f"ETL task failed to trigger for performance MF balance for business date {target_date}.",
                "status": "Task Failed",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MFPortfolioPerformanceAPIView(APIView):
    """
    API สำหรับดึงข้อมูล Performance ย้อนหลังเพื่อทำ Chart
    URL: /api/portfolio-performance/
    Method: POST
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get Portfolio Performance Chart Data",
        description="Daily aggregated market value and gain for a specific account over a period.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "example": "M1234567"},
                    "days": {"type": "integer", "example": 30}
                },
                "required": ["account_id"]
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        tags=["Investments"]
    )
    def post(self, request):
        if not hasattr(request.user, 'investor_profile'):
            return Response({"error": "No investor profile associated with this user"}, status=status.HTTP_404_NOT_FOUND)
            
        investor = request.user.investor_profile
        account_id = request.data.get('account_id')
        days_param = request.data.get('days', 30)

        if not account_id:
            return Response(
                {"error": "account_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            days = int(days_param)
            
            # Cache Key: performance_mf_{user_id}_{account_id}_{days}
            cache_key = f"performance_mf_{request.user.id}_{account_id}_{days}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for MF performance: {cache_key}")
                return Response(cached_data, status=status.HTTP_200_OK)

            start_date = timezone.now().date() - timedelta(days=days)
            
            # Filter logic: Specific account or all accounts for this investor
            filters = {'date__gte': start_date}
            
            if account_id and account_id != 'all':
                # Security: Verify account belongs to this investor (or is admin)
                if not request.user.is_staff:
                    if not InvestorAccount.objects.filter(accountID=account_id, custCode=investor).exists():
                        return Response({"error": "You do not have permission to access this account's performance data"}, status=status.HTTP_403_FORBIDDEN)
                filters['accountID__accountID'] = account_id
            else:
                # Aggregate for all accounts of this investor
                filters['accountID__custCode'] = investor
            
            # Query ข้อมูลและรวมยอด (Aggregate) รายวัน
            history = PerformanceMFAccountBalance.objects.filter(
                **filters
            ).values('date').annotate(
                total_market_value=Sum('marketValue'),
                total_gain=Sum('unrealizedGain')
            ).order_by('date')

            serializer = PerformanceChartSerializer(history, many=True)
            
            # คำนวณภาพรวมสั้นๆ
            summary = self._get_summary(history)

            response_data = {
                "account_id": account_id,
                "period_days": days,
                "summary": summary,
                "chart_data": serializer.data
            }
            
            # Cache the result for 1 hour (3600 seconds)
            cache.set(cache_key, response_data, 3600)
            logger.info(f"Cache miss for MF performance: {cache_key}. Data cached.")

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid days parameter"}, status=status.HTTP_400_BAD_REQUEST)

    def _get_summary(self, history):
        if not history:
            return None
        
        # history is a QuerySet of dicts
        first_val = history[0]['total_market_value']
        last_val = history[len(history)-1]['total_market_value']
        
        # Protection against None
        first = float(first_val) if first_val else 0.0
        last = float(last_val) if last_val else 0.0
        
        diff = last - first
        pct = (diff / first * 100) if first > 0 else 0
        
        return {
            "start_value": first,
            "current_value": last,
            "change_amount": diff,
            "change_percent": round(pct, 2)
        }

class PFPortfolioPerformanceAPIView(APIView):
    """
    API สำหรับดึงข้อมูล Performance ย้อนหลังเพื่อทำ Chart
    URL: /api/portfolio-performance/
    Method: POST
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Get Portfolio Performance Chart Data",
        description="Daily aggregated market value and gain for a specific account over a period.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "example": "M1234567"},
                    "days": {"type": "integer", "example": 30}
                },
                "required": ["account_id"]
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        tags=["Investments"]
    )
    def post(self, request):
        if not hasattr(request.user, 'investor_profile'):
            return Response({"error": "No investor profile associated with this user"}, status=status.HTTP_404_NOT_FOUND)
            
        investor = request.user.investor_profile
        account_id = request.data.get('account_id')
        days_param = request.data.get('days', 30)

        if not account_id:
            return Response(
                {"error": "account_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            days = int(days_param)
            
            # Cache Key: performance_pf_{user_id}_{account_id}_{days}
            cache_key = f"performance_pf_{request.user.id}_{account_id}_{days}"
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for PF performance: {cache_key}")
                return Response(cached_data, status=status.HTTP_200_OK)

            start_date = timezone.now().date() - timedelta(days=days)
            
            # Filter logic: Specific account or all accounts for this investor
            filters = {'date__gte': start_date}
            
            if account_id and account_id != 'all':
                # Security: Verify account belongs to this investor (or is admin)
                if not request.user.is_staff:
                    if not InvestorAccount.objects.filter(accountID=account_id, custCode=investor).exists():
                        return Response({"error": "You do not have permission to access this account's performance data"}, status=status.HTTP_403_FORBIDDEN)
                filters['accountID__accountID'] = account_id
            else:
                # Aggregate for all accounts of this investor
                filters['accountID__custCode'] = investor
            
            # Query ข้อมูลและรวมยอด (Aggregate) รายวัน
            history = PerformancePrivateFundBalance.objects.filter(
                **filters
            ).values('date').annotate(
                total_market_value=Sum('marketValue'),
                total_gain=Sum('unrealizedGain')
            ).order_by('date')

            serializer = PerformanceChartSerializer(history, many=True)
            
            # คำนวณภาพรวมสั้นๆ
            summary = self._get_summary(history)

            response_data = {
                "account_id": account_id,
                "period_days": days,
                "summary": summary,
                "chart_data": serializer.data
            }

            # Cache the result for 1 hour (3600 seconds)
            cache.set(cache_key, response_data, 3600)
            logger.info(f"Cache miss for PF performance: {cache_key}. Data cached.")

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid days parameter"}, status=status.HTTP_400_BAD_REQUEST)

    def _get_summary(self, history):
        if not history:
            return None
        
        # history is a QuerySet of dicts
        first_val = history[0]['total_market_value']
        last_val = history[len(history)-1]['total_market_value']
        
        # Protection against None
        first = float(first_val) if first_val else 0.0
        last = float(last_val) if last_val else 0.0
        
        diff = last - first
        pct = (diff / first * 100) if first > 0 else 0
        
        return {
            "start_value": first,
            "current_value": last,
            "change_amount": diff,
            "change_percent": round(pct, 2)
        }
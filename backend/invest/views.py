from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Investor, InvestorAccount, AccountBalance, ICLicense, BondAccount, PrivateFundAccount, PrivateFundBalance, PerformanceMFAccountBalance,PerformancePrivateFundBalance
from .serializers import (
    InvestorSerializer, InvestorAccountSerializer, AccountBalanceSerializer, 
    ICLicenseSerializer, BondAccountSerializer, PrivateFundAccountSerializer, 
    PrivateFundBalanceSerializer, PerformanceChartSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .tasks import run_daily_fundconnext_etl_trans, run_daily_fundconnext_etl_performance_mf_balance,run_daily_fundconnext_etl_current_mf_balance
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


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
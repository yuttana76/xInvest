from django.urls import path
from .views import (
    InvestorListView, InvestorInquiryView, InvestorMeView, 
    ETLManualTriggerViewTrans, ETLManualTriggerViewCurrentBalance, 
    ETLManualTriggerViewPerformanceBalance, MFPortfolioPerformanceAPIView, PFPortfolioPerformanceAPIView
)

urlpatterns = [
    # Investor
    path('me/', InvestorMeView.as_view(), name='investor_me'),

    # Admin
    path('investors/', InvestorListView.as_view(), name='investor_list'),
    path('inquiry/', InvestorInquiryView.as_view(), name='investor_inquiry'),

    #AllottedTransactions
    #Current-UnitholderBalance
    #Performance-UnitholderBalance

    path('etl/trigger-fconnext-transaction/', ETLManualTriggerViewTrans.as_view(), name='etl_trigger_transaction'),
    path('etl/trigger-fconnext-current-balance/', ETLManualTriggerViewCurrentBalance.as_view(), name='etl_trigger_current_balance'),
    path('etl/trigger-fconnext-performance-balance/', ETLManualTriggerViewPerformanceBalance.as_view(), name='etl_trigger_performance_balance'),

    #Performance api
    path('mf/portfolio-performance/', MFPortfolioPerformanceAPIView.as_view(), name='portfolio_performance'),
    path('pf/portfolio-performance/', PFPortfolioPerformanceAPIView.as_view(), name='portfolio_performance'),

]

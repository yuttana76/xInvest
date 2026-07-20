from django.urls import path
from .views import (
    InvestorListView, InvestorInquiryView, InvestorMeView, 
    MFPortfolioPerformanceAPIView, PFPortfolioPerformanceAPIView,
    OperatorInvestorListView, OperatorInvestorDetailView, MarketingInvestorListView, AgentInvestorListView,
    OperatorDashboardView, OperatorInvestorExportView,
    MarketingDashboardView, AgentDashboardView,
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

    # path('etl/trigger-fconnext-transaction/', ETLManualTriggerViewTrans.as_view(), name='etl_trigger_transaction'),
    # path('etl/trigger-fconnext-current-balance/', ETLManualTriggerViewCurrentBalance.as_view(), name='etl_trigger_current_balance'),
    # path('etl/trigger-fconnext-performance-balance/', ETLManualTriggerViewPerformanceBalance.as_view(), name='etl_trigger_performance_balance'),

    #Performance api
    path('mf/portfolio-performance/', MFPortfolioPerformanceAPIView.as_view(), name='portfolio_performance'),
    path('pf/portfolio-performance/', PFPortfolioPerformanceAPIView.as_view(), name='portfolio_performance'),

    #Admin & Staff & Marketing
    path('operator/investors/', OperatorInvestorListView.as_view(), name='operator_investor_list'),
    path('operator/investors/<int:pk>/', OperatorInvestorDetailView.as_view(), name='operator_investor_detail'),
    path('operator/dashboard/', OperatorDashboardView.as_view(), name='operator_dashboard'),
    path('operator/investors/export/', OperatorInvestorExportView.as_view(), name='operator_investor_export'),
    
    path('marketing/dashboard/', MarketingDashboardView.as_view(), name='marketing_dashboard'),
    path('marketing/investors/', MarketingInvestorListView.as_view(), name='marketing_investor_list'),
    
    path('agent/dashboard/', AgentDashboardView.as_view(), name='agent_dashboard'),
    path('agent/investors/', AgentInvestorListView.as_view(), name='agent_investor_list'),
]

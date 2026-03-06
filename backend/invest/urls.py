from django.urls import path
from .views import InvestorDetailView, InvestorAccountListView, AccountBalanceListView, InvestorListView, InvestorInquiryView

urlpatterns = [
    path('inquiry/', InvestorInquiryView.as_view(), name='investor_inquiry'),
    path('investors/', InvestorListView.as_view(), name='investor_list'),
    path('investor/<str:custCode>/', InvestorDetailView.as_view(), name='investor_detail'),
    path('accounts/<str:custCode>/', InvestorAccountListView.as_view(), name='investor_accounts'),
    path('balances/<str:custCode>/', AccountBalanceListView.as_view(), name='account_balances'),
]

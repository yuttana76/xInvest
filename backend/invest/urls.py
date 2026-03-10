from django.urls import path
from .views import InvestorDetailView, InvestorAccountListView, AccountBalanceListView, InvestorListView, InvestorInquiryView, InvestorMeView

urlpatterns = [
    # Investor
    path('me/', InvestorMeView.as_view(), name='investor_me'),

    # Admin
    path('investors/', InvestorListView.as_view(), name='investor_list'),
    path('inquiry/', InvestorInquiryView.as_view(), name='investor_inquiry'),

#     path('investor/<str:custCode>/', InvestorDetailView.as_view(), name='investor_detail'),
#     path('investor/accounts/<str:custCode>/', InvestorAccountListView.as_view(), name='investor_accounts'),
#     path('investor/balances/<str:custCode>/', AccountBalanceListView.as_view(), name='account_balances'),
 
]

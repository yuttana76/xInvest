from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import APILoginView, APIVerifyOTPView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('login/', APILoginView.as_view(), name='api_login'),
    path('verify-otp/', APIVerifyOTPView.as_view(), name='api_verify_otp'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

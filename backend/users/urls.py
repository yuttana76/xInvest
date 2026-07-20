# pyrefly: ignore [missing-import]
from django.urls import path
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    APILoginView, APIVerifyOTPView, PasswordResetRequestView, PasswordResetConfirmView,
    APIRegisterView, APIRegisterVerifyView, APIResendRegisterOTPView
)

urlpatterns = [
    path('login/', APILoginView.as_view(), name='api_login'),
    path('verify-otp/', APIVerifyOTPView.as_view(), name='api_verify_otp'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Registor api.
    path('register/', APIRegisterView.as_view(), name='api_register'),
    path('register/verify/', APIRegisterVerifyView.as_view(), name='api_register_verify'),
    path('register/resend-otp/', APIResendRegisterOTPView.as_view(), name='api_register_resend_otp'),
]

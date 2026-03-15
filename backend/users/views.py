from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, UserActivityLog
from .serializers import LoginSerializer, VerifyOTPSerializer, TokenRefreshSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.models import User
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_os_from_ua(user_agent):
    if not user_agent:
        return "Unknown"
    ua = user_agent.lower()
    if "windows" in ua:
        return "Windows"
    elif "macintosh" in ua or "mac os x" in ua:
        return "Mac OS"
    elif "linux" in ua:
        return "Linux"
    elif "android" in ua:
        return "Android"
    elif "iphone" in ua or "ipad" in ua:
        return "iOS"
    return "Other"

def log_activity(user, request, activity_type):
    ip = get_client_ip(request)
    ua = request.META.get('HTTP_USER_AGENT')
    os = get_os_from_ua(ua)
    UserActivityLog.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=ip,
        user_agent=ua,
        os=os
    )

class APILoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Login (Phase 1)",
        description="Authenticates user and sends OTP to email. Returns otp_ref for phase 2. ",
        request=LoginSerializer,
        responses={200: OpenApiTypes.OBJECT},
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

        
            user = authenticate(username=username, password=password)
            
            if user:
                otp, created = OTP.objects.get_or_create(user=user)
                otp_ref, otp_code = otp.generate_code()
                
                # Send OTP via email (Console for now)
                send_mail(
                    "Your xInvest Verification Code",
                    f"Your otp code is: {otp_code} for {otp_ref}. It will expire in 10 minutes.",
                    "noreply@xinvest.com",
                    [user.email],
                    fail_silently=False,
                )
                
                print("OTP sent to your email.OTP Code: %s Ref: %s", otp_code, otp_ref)


                return Response({
                    "message": "OTP sent to your email.",
                    "username": username,   
                    "otp_ref": otp_ref
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class APIVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            # otp_ref = serializer.validated_data['otp_ref']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                user = User.objects.get(username=username)
                otp = user.otp
                
                if otp.otp_code == otp_code and otp.is_valid():
                    # Generate JWT
                    refresh = RefreshToken.for_user(user)
                    
                    # Clear OTP after successful verify
                    otp.max_otp_try = 3
                    otp.otp_code = ""
                    otp.otpSuccess_DT = timezone.now()
                    otp.save()
                    
                    # Determine role
                    if user.is_staff or user.is_superuser:
                        role = "admin"
                    elif user.groups.filter(name="operator").exists():
                        role = "operator"
                    elif user.groups.filter(name="marketing").exists():
                        role = "marketing"
                    elif user.groups.filter(name="agent").exists():
                        role = "agent"
                    elif hasattr(user, 'investor_profile'):
                        role = "investor"
                    else:
                        role = "guest" # Or some other default

                    # Add custom claims to the token payload
                    refresh['username'] = user.username
                    refresh['email'] = user.email
                    refresh['role'] = role
                    
                    # Log the login
                    log_activity(user, request, 'LOGIN')
                    
                    return Response({
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "username": user.username,
                        "email": user.email,
                        "role": role
                    }, status=status.HTTP_200_OK)
                
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_401_UNAUTHORIZED)
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({"error": "User or OTP not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            serializer = TokenRefreshSerializer(data=request.data)
            if serializer.is_valid():
                refresh_token = serializer.validated_data['refresh']
                # In a real scenario, you'd use rest_framework_simplejwt.views.TokenRefreshView
                # but for simplicity in this custom view:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken(refresh_token)
                return Response({
                    "access": str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(username=username, email=email)
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                
                from django.conf import settings
                reset_link = f"{settings.FRONTEND_URL}/reset-password?uidb64={uidb64}&token={token}"
                
                print("Password reset link sent to your email. Link: %s", reset_link)
                print("User email: %s", user.email)
                
                # Log the forgot password request
                log_activity(user, request, 'PASSWORD_RESET_REQUEST')
                
                # Send email (Console for now)
                send_mail(
                    "Password Reset Request for xInvest",
                    f"Hi {user.username},\n\nYou requested a password reset. Click the link below to set a new password:\n\n{reset_link}\n\nIf you didn't request this, please ignore this email.",
                    "noreply@xinvest.com",
                    [user.email],
                    fail_silently=False,
                )
                
                return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                # Don't leak if user exists or not
                return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            uidb64 = serializer.validated_data['uidb64']
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                
                print("User found: %s", user)

                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
            except (UnicodeDecodeError, User.DoesNotExist, ValueError):
                return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
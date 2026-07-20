import os

from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.cache.backends.locmem import LocMemCache
from .tasks import task_send_otp_email, task_send_password_reset_email, task_send_welcome_email
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, UserActivityLog, determine_user_role
from .serializers import (
    LoginSerializer, VerifyOTPSerializer, TokenRefreshSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, RegisterSerializer
)
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", "3"))
OTP_COOLDOWN_SECONDS = int(os.environ.get("OTP_COOLDOWN_SECONDS", "60"))
PASSWORD_MAX_ATTEMPTS = int(os.environ.get("PASSWORD_MAX_ATTEMPTS", "3"))
PASSWORD_COOLDOWN_SECONDS = int(os.environ.get("PASSWORD_COOLDOWN_SECONDS", "60"))

_FALLBACK_CACHE = LocMemCache("otp-lockout-fallback", {})


def _active_cache():
    try:
        cache.get("otp-lockout-probe")
        return cache
    except Exception:
        return _FALLBACK_CACHE


def _lock_state_key(username, scope):
    return f"{scope}_lock:{username.lower()}"


def _get_lock_state(username, scope, otp=None):
    state = _active_cache().get(_lock_state_key(username, scope)) or {"attempts": 0, "locked_until": None}
    if state.get("locked_until") and timezone.now() >= state["locked_until"]:
        state = {"attempts": 0, "locked_until": None}
        _active_cache().set(_lock_state_key(username, scope), state, timeout=OTP_COOLDOWN_SECONDS)

    if not state.get("locked_until") and otp is not None and scope == "otp":
        if otp.otpSuccess_DT and otp.otpSuccess_DT > timezone.now():
            state = {"attempts": OTP_MAX_ATTEMPTS, "locked_until": otp.otpSuccess_DT}
        elif otp.max_otp_try is not None and otp.max_otp_try <= 0:
            state = {"attempts": OTP_MAX_ATTEMPTS, "locked_until": timezone.now() + timezone.timedelta(seconds=OTP_COOLDOWN_SECONDS)}

    return state


def _set_lock_state(username, scope, attempts, locked_until, otp=None):
    timeout = OTP_COOLDOWN_SECONDS if scope == "otp" else PASSWORD_COOLDOWN_SECONDS
    _active_cache().set(_lock_state_key(username, scope), {"attempts": attempts, "locked_until": locked_until}, timeout=timeout)
    if otp is not None and scope == "otp":
        if locked_until and locked_until > timezone.now():
            otp.max_otp_try = 0
            otp.otpSuccess_DT = locked_until
        else:
            otp.max_otp_try = OTP_MAX_ATTEMPTS
            otp.otpSuccess_DT = None
        otp.save(update_fields=['max_otp_try', 'otpSuccess_DT'])


def _is_otp_locked(username, otp=None):
    state = _get_lock_state(username, "otp", otp=otp)
    return bool(state.get("locked_until") and state["locked_until"] > timezone.now())


def _unlock_if_expired(username, otp=None):
    state = _get_lock_state(username, "otp", otp=otp)
    if state.get("locked_until") and state["locked_until"] <= timezone.now():
        _set_lock_state(username, "otp", 0, None, otp=otp)


def _mark_failed_attempt(username, otp=None):
    state = _get_lock_state(username, "otp", otp=otp)
    attempts = state.get("attempts", 0) + 1
    if attempts >= OTP_MAX_ATTEMPTS:
        locked_until = timezone.now() + timezone.timedelta(seconds=OTP_COOLDOWN_SECONDS)
        _set_lock_state(username, "otp", attempts, locked_until, otp=otp)
        return True
    _set_lock_state(username, "otp", attempts, None, otp=otp)
    return False


def _reset_attempt_state(username, otp=None):
    _set_lock_state(username, "otp", 0, None, otp=otp)


def _is_password_locked(username):
    state = _get_lock_state(username, "password")
    return bool(state.get("locked_until") and state["locked_until"] > timezone.now())


def _get_retry_at_message(username, scope):
    state = _get_lock_state(username, scope)
    locked_until = state.get("locked_until")
    if locked_until:
        aware_locked_until = timezone.localtime(locked_until)
        return aware_locked_until.strftime("Please try again at %H:%M:%S")
    return f"Please try again in {OTP_COOLDOWN_SECONDS if scope == 'otp' else PASSWORD_COOLDOWN_SECONDS} seconds."


def _unlock_password_if_expired(username):
    state = _get_lock_state(username, "password")
    if state.get("locked_until") and state["locked_until"] <= timezone.now():
        _set_lock_state(username, "password", 0, None)


def _mark_password_failed_attempt(username):
    state = _get_lock_state(username, "password")
    attempts = state.get("attempts", 0) + 1
    if attempts >= PASSWORD_MAX_ATTEMPTS:
        locked_until = timezone.now() + timezone.timedelta(seconds=PASSWORD_COOLDOWN_SECONDS)
        _set_lock_state(username, "password", attempts, locked_until)
        return True
    _set_lock_state(username, "password", attempts, None)
    return False


def _reset_password_attempt_state(username):
    _set_lock_state(username, "password", 0, None)


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
        
        print("*Login request data:", request.data)
        serializer = LoginSerializer(data=request.data)


        if serializer.is_valid():

            print("*Login serializer validated data:", serializer.validated_data)
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            if _is_password_locked(username):
                return Response({"error": f"Login locked. {_get_retry_at_message(username, 'password')}"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            user = authenticate(username=username, password=password)

            print("*Authenticated user:", user)
            if user:
                otp, created = OTP.objects.get_or_create(user=user)
                _reset_attempt_state(username, otp=otp)
                _reset_password_attempt_state(username)
                otp_ref, otp_code = otp.generate_code()

                task_send_otp_email.delay(
                    user_email=user.email,
                    username=user.username,
                    otp_code=otp_code,
                    otp_ref=otp_ref,
                )

                print("OTP sent to your email.OTP Code: %s Ref: %s", otp_code, otp_ref)

                return Response({
                    "message": "OTP sent to your email.",
                    "username": username,
                    "otp_ref": otp_ref
                }, status=status.HTTP_200_OK)

            existing_user = User.objects.filter(username=username).first()
            print("*Existing user:", existing_user)
            if existing_user:
                otp, _ = OTP.objects.get_or_create(user=existing_user)
                if _is_password_locked(username):
                    return Response({"error": f"Login locked. {_get_retry_at_message(username, 'password')}"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
                _unlock_password_if_expired(username)
                if _mark_password_failed_attempt(username):
                    return Response({"error": f"Login locked(failed attempt). {_get_retry_at_message(username, 'password')}"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class APIVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                user = User.objects.get(username=username)
                otp = user.otp

                if _is_otp_locked(username, otp=otp):
                    return Response({"error": f"OTP locked. {_get_retry_at_message(username, 'otp')}"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

                _unlock_if_expired(username, otp=otp)

                if otp.otp_code == otp_code and otp.is_valid():
                    refresh = RefreshToken.for_user(user)
                    _reset_attempt_state(username, otp=otp)
                    otp.otp_code = ""
                    otp.save()
                    
                    role = determine_user_role(user)
                    refresh['username'] = user.username
                    refresh['email'] = user.email
                    refresh['role'] = role
                    
                    log_activity(user, request, 'LOGIN')
                    
                    return Response({
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "username": user.username,
                        "email": user.email,
                        "role": role
                    }, status=status.HTTP_200_OK)

                if _mark_failed_attempt(username, otp=otp):
                    return Response({"error": f"OTP locked. {_get_retry_at_message(username, 'otp')}"}, status=status.HTTP_429_TOO_MANY_REQUESTS)

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
            email = serializer.validated_data.get('email')

            try:
                if email:
                    user = User.objects.get(username=username, email=email)
                else:
                    user = User.objects.get(username=username)

                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                
                from django.conf import settings
                reset_link = f"{settings.FRONTEND_URL}/reset-password?uidb64={uidb64}&token={token}"
                
                print("Password reset link sent to your email. Link: %s", reset_link)
                print("User email: %s", user.email)
                
                # Log the forgot password request
                log_activity(user, request, 'PASSWORD_RESET_REQUEST')
                
                # ส่ง Password Reset email ผ่าน Celery Queue (async)
                # → API ตอบกลับทันที ไม่รอ SMTP
                task_send_password_reset_email.delay(
                    user_email=user.email,
                    username=user.username,
                    reset_link=reset_link,
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


class APIRegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Registration (Phase 1)",
        description="Creates a new unverified user and sends OTP to email.",
        request=RegisterSerializer,
        responses={201: OpenApiTypes.OBJECT},
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate OTP & OTP Reference
            otp, created = OTP.objects.get_or_create(user=user)
            otp_ref, otp_code = otp.generate_code()
            
            # Send OTP email via Celery async
            task_send_otp_email.delay(
                user_email=user.email,
                username=user.username,
                otp_code=otp_code,
                otp_ref=otp_ref,
            )
            
            print(f"Registration OTP sent to email. OTP Code: {otp_code} Ref: {otp_ref}")

            return Response({
                "message": "Registration successful. Please verify your email with the OTP sent.",
                "username": user.username,
                "email": user.email,
                "otp_ref": otp_ref,
                "register_date": user.date_joined
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify Registration OTP (Phase 2)",
        description="Verifies the OTP code to activate the user account.",
        request=VerifyOTPSerializer,
        responses={200: OpenApiTypes.OBJECT},
        tags=["Authentication"]
    )
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                user = User.objects.get(username=username)
                
                # Check if user is already active
                if user.is_active and hasattr(user, 'profile') and user.profile.is_email_verified:
                    return Response({"message": "User is already active and verified."}, status=status.HTTP_200_OK)
                
                otp = user.otp
                if otp.otp_code == otp_code and otp.is_valid():
                    # Activate user
                    user.is_active = True
                    user.save()
                    
                    # Mark email as verified
                    profile = user.profile
                    profile.is_email_verified = True
                    profile.save()
                    
                    # Clear OTP
                    otp.max_otp_try = 3
                    otp.otp_code = ""
                    otp.otpSuccess_DT = timezone.now()
                    otp.save()
                    
                    # Log activity
                    log_activity(user, request, 'LOGIN')
                    
                    # ส่งอีเมลต้อนรับผ่าน Celery async
                    task_send_welcome_email.delay(
                        user_email=user.email,
                        username=user.username,
                    )
                    
                    return Response({
                        "message": "Email verified successfully. Your account is now active.",
                        "username": user.username,
                        "is_active": True
                    }, status=status.HTTP_200_OK)
                
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_401_UNAUTHORIZED)
            except (User.DoesNotExist, OTP.DoesNotExist):
                return Response({"error": "User or OTP not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIResendRegisterOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Resend Registration OTP",
        description="Resends the verification OTP code to the user's registered email if not verified yet.",
        responses={200: OpenApiTypes.OBJECT},
        tags=["Authentication"]
    )
    def post(self, request):
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(username=username)
            if user.is_active and hasattr(user, 'profile') and user.profile.is_email_verified:
                return Response({"error": "User is already active and verified."}, status=status.HTTP_400_BAD_REQUEST)
                
            otp, created = OTP.objects.get_or_create(user=user)
            otp_ref, otp_code = otp.generate_code()
            
            task_send_otp_email.delay(
                user_email=user.email,
                username=user.username,
                otp_code=otp_code,
                otp_ref=otp_ref,
            )
            
            return Response({
                "message": "Registration OTP resent successfully.",
                "otp_ref": otp_ref
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
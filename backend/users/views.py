from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTP, LoginLog
from .serializers import LoginSerializer, VerifyOTPSerializer
from django.contrib.auth.models import User
from django.utils import timezone

class APILoginView(APIView):
    permission_classes = [AllowAny]

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
                    elif hasattr(user, 'investor_profile'):
                        role = "investor"
                    else:
                        role = "guest" # Or some other default
                    
                    # Log the login
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')
                    
                    user_agent = request.META.get('HTTP_USER_AGENT')
                    
                    LoginLog.objects.create(
                        user=user,
                        ip_address=ip,
                        user_agent=user_agent
                    )
                    
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
                print("***",refresh_token)

                request.data['refresh'] = refresh_token
                response = super().post(request, *args, **kwargs)
                tokens = response.data
                access_token = tokens['access']
                res = Response()


                return Response({
                    "access": str(access_token),
                }, status=status.HTTP_200_OK)

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # print("***",request.data)
            # refresh_token = request.COOKIES.get('refresh_token')

            # request.data['refresh'] = refresh_token
            # response = super().post(request, *args, **kwargs)
            # tokens = response.data
            # access_token = tokens['access']
            # res = Response()

            # res.data = {'refreshed': True}

            # res.set_cookie(
            #     key='access_token',
            #     value=access_token,
            #     httponly=True,
            #     secure=True,
            #     samesite='None',
            #     path='/'
            # )
            # return res

        except Exception as e:
            print(e)
            return Response({'refreshed': False})
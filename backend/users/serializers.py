from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class VerifyOTPSerializer(serializers.Serializer):
    username = serializers.CharField()
    otp_code = serializers.CharField(max_length=6)

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_blank=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)


import re
from django.contrib.auth.models import User
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    mobile_number = serializers.CharField(max_length=15, write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'mobile_number']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_mobile_number(self, value):
        # Allow numbers only and check length (9-10 digits for TH phone numbers)
        if not re.match(r'^\d{9,10}$', value):
            raise serializers.ValidationError("Mobile number must be a valid 9 to 10 digit number.")
        if Profile.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError("This mobile number is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
            
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter."})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter."})
        if not re.search(r'[0-9]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one number."})
        if not re.search(r'[_@$!%*?&#]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one special character (_@$!%*?&#)."})
            
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        mobile_number = validated_data.pop('mobile_number')
        
        # Create user with is_active = False (unverified)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=False
        )
        
        # Create Profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.mobile_number = mobile_number
        profile.save()
        
        return user


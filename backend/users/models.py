from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import datetime
import pyotp
import base64
import random
from random import choice
import string

class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp")
    otp_ref = models.CharField(max_length=6)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    max_otp_try = models.IntegerField(default=3,null=True, blank=True)  # Max OTP tries
    otpSuccess_DT = models.DateTimeField(blank=True, null=True)
    
    def is_valid(self):
        # OTP is valid for 10 minutes
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() <= expiry_time

    def generate_code(self):

        # # New Generate OTP & OTP Reference
        OTP_LIFE_MIN=10  # OTP life in 10 minutes
        MAX_OTP_TRY=3

        keygen = generateKey()
        OTP_Ref = keygen.generate_ref()
        
        key = base64.b32encode(OTP_Ref.encode())  # Key is generated
        OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
        OTP_Code = OTP.at(6)  # OTP Code length 6 digit
        OTP_expiry = timezone.now() + timezone.timedelta(minutes=OTP_LIFE_MIN)
        max_otp_try = int(self.max_otp_try) - 1

        # client.otp = OTP_Code
        # client.otp_ref = OTP_Ref
        # client.otp_expiry = OTP_expiry
        # client.max_otp_try = max_otp_try

        #Generate OTP reference
        # self.code = ''.join(random.choices(string.digits, k=6))
        self.otp_code = OTP_Code
        self.otp_ref = OTP_Ref
        self.otp_expiry = OTP_expiry
        self.max_otp_try = max_otp_try
        self.created_at = timezone.now()
        self.save()
        # Return otp_ref and otp_code

        return self.otp_ref, self.otp_code

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"

class generateKey:
    @staticmethod
    def generateOTP(phone, refCode):
        return str(phone) + refCode

    def generate_ref(self):
        # Generate 6 Digit verification code , Prevent cracking
        # :return:
        seeds = "1234567890abcdefghijklmnopqrstuvwxyz"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)
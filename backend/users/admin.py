from django.contrib import admin

from .models import *
# from import_export.admin import ImportExportModelAdmin

# admin.site.register(OTP)

@admin.register(OTP)
class otpAdmin(admin.ModelAdmin):
    list_display = ('user','created_at', 'otp_expiry','max_otp_try','otpSuccess_DT')
    ordering = ['created_at']
    search_fields = ['user']

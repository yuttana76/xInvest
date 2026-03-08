from django.contrib import admin

from .models import *
# from import_export.admin import ImportExportModelAdmin

# admin.site.register(OTP)

@admin.register(OTP)
class otpAdmin(admin.ModelAdmin):
    list_display = ('user','created_at', 'otp_expiry','max_otp_try','otpSuccess_DT')
    ordering = ['created_at']
    search_fields = ['user']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'os', 'created_at')
    list_filter = ('activity_type', 'created_at', 'os')
    search_fields = ('user__username', 'ip_address', 'user_agent', 'os')
    readonly_fields = ('user', 'activity_type', 'ip_address', 'user_agent', 'os', 'created_at')

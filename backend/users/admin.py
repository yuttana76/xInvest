from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(OTP)
class otpAdmin(admin.ModelAdmin):
    list_display = ('user','created_at', 'otp_expiry','max_otp_try','otpSuccess_DT')
    ordering = ['created_at']
    search_fields = ['user__username']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'ip_address', 'os', 'created_at')
    list_filter = ('activity_type', 'created_at', 'os')
    search_fields = ('user__username', 'ip_address', 'user_agent', 'os')
    readonly_fields = ('user', 'activity_type', 'ip_address', 'user_agent', 'os', 'created_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user__username', 'department__name')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')
    search_fields = ('name', 'manager__username')

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
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
    list_display = ('user', 'department', 'is_email_verified', 'resend_otp_button')
    search_fields = ('user__username', 'department__name')
    list_filter = ('is_email_verified', 'department')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:profile_id>/resend-otp/', self.admin_site.admin_view(self.resend_otp_view), name='profile-resend-otp'),
        ]
        return custom_urls + urls

    def resend_otp_view(self, request, profile_id):
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib import messages
        from .models import OTP
        from .tasks import task_send_otp_email

        profile = get_object_or_404(Profile, pk=profile_id)
        user = profile.user

        if user.is_active and profile.is_email_verified:
            self.message_user(request, f"User {user.username} is already active and verified.", level=messages.WARNING)
        else:
            otp, created = OTP.objects.get_or_create(user=user)
            otp_ref, otp_code = otp.generate_code()
            
            task_send_otp_email.delay(
                user_email=user.email,
                username=user.username,
                otp_code=otp_code,
                otp_ref=otp_ref,
            )
            self.message_user(request, f"Registration OTP resent successfully for {user.username}. Ref: {otp_ref}", level=messages.SUCCESS)

        return redirect(request.META.get('HTTP_REFERER', 'admin:users_profile_changelist'))



    def resend_otp_button(self, obj):
        if obj.user.is_active and obj.is_email_verified:
            return format_html('<span style="color: green; font-weight: bold;">Verified</span>')
        url = reverse('admin:profile-resend-otp', args=[obj.pk])
        return format_html('<a class="button" href="{}" style="padding: 3px 8px; background: #79aec8; color: white; border-radius: 4px; text-decoration: none; font-size: 11px;">Resend OTP</a>', url)
    
    resend_otp_button.short_description = 'Actions'
    resend_otp_button.allow_tags = True

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager')
    search_fields = ('name', 'manager__username')

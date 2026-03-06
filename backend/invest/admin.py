from django.contrib import admin
from .models import Investor, InvestorAccount, AccountBalance

@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ('compCode', 'custCode', 'fullNameEn', 'projects', 'status')
    list_filter = ('projects', 'status')
    search_fields = ('compCode', 'custCode', 'fullNameEn')

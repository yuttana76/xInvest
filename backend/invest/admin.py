from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Investor, InvestorAccount, AccountBalance

@admin.register(Investor)
class InvestorAdmin(ImportExportModelAdmin):
    list_display = ('compCode', 'custCode', 'fullNameEn', 'projects', 'status')
    list_filter = ('projects', 'status')
    search_fields = ('compCode', 'custCode', 'fullNameEn')

@admin.register(InvestorAccount)
class InvestorAccountAdmin(ImportExportModelAdmin):
    list_display = ('compCode', 'custCode', 'accountID', 'IC_license', 'openDate')
    list_filter = ('compCode', 'IC_license')
    search_fields = ('compCode', 'accountID', 'custCode__custCode')

@admin.register(AccountBalance)
class AccountBalanceAdmin(ImportExportModelAdmin):
    list_display = ('compCode', 'accountID', 'fundCode', 'unitBalance', 'amount', 'NAV', 'NAVdate')
    list_filter = ('compCode', 'fundCode', 'NAVdate')
    search_fields = ('compCode', 'accountID__accountID', 'fundCode')

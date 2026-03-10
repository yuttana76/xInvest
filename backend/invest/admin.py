from django.contrib import admin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Investor, InvestorAccount, AccountBalance, ICLicense

class BaseResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        if 'id' not in row or not row['id']:
            row['id'] = None

class InvestorResource(BaseResource):
    class Meta:
        model = Investor

class InvestorAccountResource(BaseResource):
    custCode = fields.Field(
        column_name='custCode',
        attribute='custCode',
        widget=ForeignKeyWidget(Investor, field='custCode')
    )
    
    class Meta:
        model = InvestorAccount

class AccountBalanceResource(BaseResource):
    accountID = fields.Field(
        column_name='accountID',
        attribute='accountID',
        widget=ForeignKeyWidget(InvestorAccount, field='accountID')
    )

    class Meta:
        model = AccountBalance

class ICLicenseResource(BaseResource):
    class Meta:
        model = ICLicense

@admin.register(Investor)
class InvestorAdmin(ImportExportModelAdmin):
    resource_class = InvestorResource
    list_display = ('compCode', 'custCode', 'fullNameEn', 'projects', 'status')
    list_filter = ('projects', 'status')
    search_fields = ('compCode', 'custCode', 'fullNameEn')

@admin.register(InvestorAccount)
class InvestorAccountAdmin(ImportExportModelAdmin):
    resource_class = InvestorAccountResource
    list_display = ('compCode', 'custCode', 'accountID', 'IC_license', 'openDate')
    list_filter = ('compCode', 'IC_license')
    search_fields = ('compCode', 'accountID', 'custCode__custCode')

@admin.register(AccountBalance)
class AccountBalanceAdmin(ImportExportModelAdmin):
    resource_class = AccountBalanceResource
    list_display = ('compCode', 'accountID', 'fundCode', 'unitBalance', 'amount', 'NAV', 'NAVdate')
    list_filter = ('compCode', 'fundCode', 'NAVdate')
    search_fields = ('compCode', 'accountID__accountID', 'fundCode')

@admin.register(ICLicense)
class ICLicenseAdmin(ImportExportModelAdmin):
    resource_class = ICLicenseResource
    list_display = ('compCode', 'IC_license', 'fullName')
    list_filter = ('compCode',)
    search_fields = ('compCode', 'IC_license', 'fullName')

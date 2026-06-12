from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from .models import Investor, InvestorAccount, AccountBalance, Marketing, BondAccount, PrivateFundAccount, PrivateFundBalance, MFTransaction, MarketingGroup, ExternalAgent

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

class MarketingResource(BaseResource):
    class Meta:
        model = Marketing

class MarketingGroupResource(BaseResource):
    class Meta:
        model = MarketingGroup

class ExternalAgentResource(BaseResource):
    class Meta:
        model = ExternalAgent

@admin.register(Investor)
class InvestorAdmin(ImportExportModelAdmin):
    resource_class = InvestorResource
    list_display = ('compCode', 'user','custCode', 'fullNameEn', 'projects', 'status')
    list_filter = ('projects', 'status')
    search_fields = ('compCode', 'custCode', 'fullNameEn')
    actions = ['send_statement_report']

    def send_statement_report(self, request, queryset):
        from .tasks import send_investor_statement_report
        for investor in queryset:
            send_investor_statement_report.delay(investor.id)
        self.message_user(request, f"Statement report task triggered for {queryset.count()} investors.")
    
    send_statement_report.short_description = "Send Statement Report (via Email)"

@admin.register(InvestorAccount)
class InvestorAccountAdmin(ImportExportModelAdmin):
    resource_class = InvestorAccountResource
    list_display = ('compCode', 'custCode', 'accountID', 'marketing', 'referred_by_agent', 'openDate')
    list_filter = ('compCode', 'marketing')
    search_fields = ('compCode', 'accountID', 'custCode__custCode')

@admin.register(Marketing)
class MarketingAdmin(ImportExportModelAdmin):
    resource_class = MarketingResource
    list_display = ('fullName','user' ,'role', 'group', 'supervisor', 'license_code', 'compCode')
    list_filter = ('compCode', 'role', 'group')
    search_fields = ('fullName', 'license_code', 'compCode')

@admin.register(MarketingGroup)
class MarketingGroupAdmin(ImportExportModelAdmin):
    resource_class = MarketingGroupResource
    list_display = ('groupName', 'leader')
    search_fields = ('groupName',)

@admin.register(ExternalAgent)
class ExternalAgentAdmin(ImportExportModelAdmin):
    resource_class = ExternalAgentResource
    list_display = ('agentCode', 'fullName', 'contactNumber', 'isActive')
    list_filter = ('isActive',)
    search_fields = ('agentCode', 'fullName')

@admin.register(AccountBalance)
class AccountBalanceAdmin(ImportExportModelAdmin):
    resource_class = AccountBalanceResource
    list_display = ('compCode', 'accountID', 'fundCode', 'unitBalance', 'amount', 'NAV', 'NAVdate', 'redis_monitor_shortcut')
    list_filter = ('compCode', 'fundCode', 'NAVdate','accountID')
    search_fields = ('compCode', 'accountID__accountID', 'fundCode')
    change_list_template = "admin/invest/accountbalance/change_list.html"

    def redis_monitor_shortcut(self, obj):
        return format_html('<a href="redis-status/">Monitor</a>')
    redis_monitor_shortcut.short_description = 'Redis'

    class Media:
        js = ('invest/js/redis_monitor.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('redis-status/', self.admin_site.admin_view(self.redis_status_view), name='redis_status'),
            path('redis-status/clear-performance/', self.admin_site.admin_view(self.clear_performance_cache), name='clear_performance_cache'),
            path('run-etl-current-balance/', self.admin_site.admin_view(self.run_etl_current_balance_view), name='run_etl_current_balance'),
        ]
        return custom_urls + urls

    def redis_status_view(self, request):
        from django_redis import get_redis_connection
        from django.template.response import TemplateResponse
        
        con = get_redis_connection("default")
        info = con.info()
        
        # Performance Keys (Django)
        performance_keys = []
        for pattern in ["*performance_mf_*", "*performance_pf_*"]:
            for key in con.scan_iter(pattern):
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                ttl = con.ttl(key)
                performance_keys.append({
                    'name': key_str,
                    'ttl': ttl,
                    'ttl_human': f"{ttl // 3600}h {(ttl % 3600) // 60}m" if ttl > 0 else "Expired/No TTL"
                })
        
        # Portfolio Keys (Go Trading)
        portfolio_keys = []
        for key in con.scan_iter("portfolio:*"):
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            ttl = con.ttl(key)
            portfolio_keys.append({
                'name': key_str,
                'ttl': ttl,
                'ttl_human': f"{ttl // 3600}h {(ttl % 3600) // 60}m" if ttl > 0 else "Expired/No TTL"
            })
            
        context = {
            **self.admin_site.each_context(request),
            'title': 'Redis Real-time Monitor',
            'redis_info': {
                'Version': info.get('redis_version'),
                'Uptime (Days)': info.get('uptime_in_days'),
                'Used Memory': info.get('used_memory_human'),
                'Peak Memory': info.get('used_memory_peak_human'),
                'Connected Clients': info.get('connected_clients'),
                'Total Keys': con.dbsize(),
                'Hits': info.get('keyspace_hits'),
                'Misses': info.get('keyspace_misses'),
            },
            'performance_keys': sorted(performance_keys, key=lambda x: x['name']),
            'portfolio_keys': sorted(portfolio_keys, key=lambda x: x['name']),
        }
        return TemplateResponse(request, "admin/redis_status.html", context)

    def clear_performance_cache(self, request):
        from django_redis import get_redis_connection
        from django.contrib import messages
        from django.shortcuts import redirect
        
        con = get_redis_connection("default")
        
        selected_keys = request.POST.getlist('selected_keys')
        clear_all_perf = request.POST.get('clear_all_perf') == '1'
        clear_all_portfolio = request.POST.get('clear_all_portfolio') == '1'
        
        keys_to_delete = []
        if clear_all_perf:
            mf_keys = list(con.scan_iter("*performance_mf_*"))
            pf_keys = list(con.scan_iter("*performance_pf_*"))
            keys_to_delete = mf_keys + pf_keys
            msg = "Successfully cleared ALL performance cache keys."
        elif clear_all_portfolio:
            portfolio_keys = list(con.scan_iter("portfolio:*"))
            keys_to_delete = portfolio_keys
            msg = "Successfully cleared ALL portfolio cache keys (Go Trading)."
        elif selected_keys:
            keys_to_delete = selected_keys
            msg = f"Successfully cleared {len(keys_to_delete)} selected cache keys."
        else:
            messages.info(request, "No keys selected or found to clear.")
            return redirect('admin:redis_status')

        if keys_to_delete:
            con.delete(*keys_to_delete)
            messages.success(request, msg)
            
        return redirect('admin:redis_status')

    def run_etl_current_balance_view(self, request):
        from .tasks import run_daily_fundconnext_etl_current_mf_balance
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.template.response import TemplateResponse
        
        if request.method == 'POST':
            business_date = request.POST.get('business_date')
            if business_date:
                # Trigger the task asynchronously with the specified date
                run_daily_fundconnext_etl_current_mf_balance.delay(business_date)
                self.message_user(request, f"Task 'run_daily_fundconnext_etl_current_mf_balance' triggered for date: {business_date}")
                return redirect("..")
        
        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Run ETL Current Balance',
            'default_date': yesterday,
        }
        return TemplateResponse(request, "admin/invest/run_etl_form.html", context)


class BondAccountResource(BaseResource):
    custCode = fields.Field(
        column_name='custCode',
        attribute='custCode',
        widget=ForeignKeyWidget(Investor, field='custCode')
    )
    class Meta:
        model = BondAccount

class PrivateFundAccountResource(BaseResource):
    custCode = fields.Field(
        column_name='custCode',
        attribute='custCode',
        widget=ForeignKeyWidget(Investor, field='custCode')
    )
    class Meta:
        model = PrivateFundAccount

class PrivateFundBalanceResource(BaseResource):
    accountID = fields.Field(
        column_name='accountID',
        attribute='accountID',
        widget=ForeignKeyWidget(PrivateFundAccount, field='accountID')
    )
    class Meta:
        model = PrivateFundBalance

@admin.register(BondAccount)
class BondAccountAdmin(ImportExportModelAdmin):
    resource_class = BondAccountResource
    list_display = ('compCode', 'custCode', 'bondCode', 'marketing', 'referred_by_agent', 'amount', 'fromDate', 'toDate', 'status')
    list_filter = ('compCode', 'status')
    search_fields = ('compCode', 'custCode__custCode', 'bondCode')

@admin.register(PrivateFundAccount)
class PrivateFundAccountAdmin(ImportExportModelAdmin):
    resource_class = PrivateFundAccountResource
    list_display = ('compCode', 'custCode', 'accountID', 'marketing', 'referred_by_agent', 'openDate', 'status')
    list_filter = ('compCode', 'marketing', 'status')
    search_fields = ('compCode', 'accountID', 'custCode__custCode')

@admin.register(PrivateFundBalance)
class PrivateFundBalanceAdmin(ImportExportModelAdmin):
    resource_class = PrivateFundBalanceResource
    list_display = ('compCode', 'accountID', 'fundCode', 'unitBalance', 'amount', 'NAV', 'NAVdate')
    list_filter = ('compCode', 'fundCode', 'NAVdate')
    search_fields = ('compCode', 'accountID__accountID', 'fundCode')

class MFTransactionResource(BaseResource):
    AccountID = fields.Field(
        column_name='AccountID',
        attribute='AccountID',
        widget=ForeignKeyWidget(InvestorAccount, field='accountID')
    )
    class Meta:
        model = MFTransaction

@admin.register(MFTransaction)
class MFTransactionAdmin(ImportExportModelAdmin):
    resource_class = MFTransactionResource
    list_display = ('transactionID', 'accountID', 'transactionCode', 'fundCode', 'amount', 'unit', 'status', 'effectiveDate')
    list_filter = ('transactionCode', 'status', 'fundCode', 'effectiveDate')
    search_fields = ('transactionID', 'accountID__accountID', 'fundCode', )
    change_list_template = "admin/invest/mftransaction/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-trans/', self.admin_site.admin_view(self.run_etl_trans_view), name='run_etl_trans'),
        ]
        return custom_urls + urls

    def run_etl_trans_view(self, request):
        from .tasks import run_daily_fundconnext_etl_trans
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.template.response import TemplateResponse
        
        if request.method == 'POST':
            business_date = request.POST.get('business_date')
            if business_date:
                # Trigger the task asynchronously with the specified date
                run_daily_fundconnext_etl_trans.delay(business_date)
                self.message_user(request, f"Task 'run_daily_fundconnext_etl_trans' triggered for date: {business_date}")
                return redirect("..")

        from datetime import datetime, timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Run ETL Transactions',
            'default_date': yesterday,
        }
        return TemplateResponse(request, "admin/invest/run_etl_form.html", context)


# --- Custom Admin Sidebar Grouping ---
original_get_app_list = admin.AdminSite.get_app_list

def custom_get_app_list(self, request, app_label=None):
    app_list = original_get_app_list(self, request, app_label)
    
    # Locate 'invest' app to extract models
    invest_app = None
    for app in app_list:
        if app['app_label'] == 'invest':
            invest_app = app
            break
            
    if invest_app:
        investment_models = []
        mf_models = []
        bond_models = []
        pf_models = []
        other_models = []
        
        for model in invest_app['models']:
            model_name = model['object_name']
            if model_name in ['BondAccount']:
                bond_models.append(model)
            elif model_name in ['PrivateFundAccount', 'PrivateFundBalance']:
                pf_models.append(model)
            elif model_name in ['InvestorAccount', 'AccountBalance', 'MFTransaction']:
                mf_models.append(model)
            elif model_name in ['ExternalAgent','Investor','Marketing','MarketingGroup']:
                investment_models.append(model)
            else:
                other_models.append(model)
                
        # Keep only core invest models in the default group
        invest_app['models'] = other_models
        
        # Create 'Investment Data' group if there are mutual fund models
        if investment_models:
            investment_app = {
                'name': 'Investment Data',
                'app_label': 'investment_group',
                'app_url': '',
                'has_module_perms': True,
                'models': investment_models,
            }
            app_list.append(investment_app)
        # Create 'LBDU' group if there are mutual fund models
        if mf_models:
            mf_app = {
                'name': 'LBDU',
                'app_label': 'mf_group',
                'app_url': '',
                'has_module_perms': True,
                'models': mf_models,
            }
            app_list.append(mf_app)

        # Create 'Private Fund' group if there are private fund models
        if pf_models:
            pf_app = {
                'name': 'Private Fund',
                'app_label': 'private_fund_group',
                'app_url': '',
                'has_module_perms': True,
                'models': pf_models,
            }
            app_list.append(pf_app)

        # Create 'BOND' group if there are bond models
        if bond_models:
            bond_app = {
                'name': 'BOND',
                'app_label': 'bond_group',
                'app_url': '',
                'has_module_perms': True,
                'models': bond_models,
            }
            app_list.append(bond_app)
            
        

        
            
    return app_list

admin.AdminSite.get_app_list = custom_get_app_list



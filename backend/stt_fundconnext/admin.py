from datetime import datetime
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import FundProfile, FundPerformance, AssetAllocation, TopHolding, CustomerIndividual
from invest.models import Investor, InvestorAccount

class CustomerIndividualResource(resources.ModelResource):
    class Meta:
        model = CustomerIndividual

@admin.register(CustomerIndividual)
class CustomerIndividualAdmin(ImportExportModelAdmin):
    resource_class = CustomerIndividualResource
    list_display = ('card_number', 'en_first_name', 'en_last_name', 'th_first_name', 'mobile_number', 'email', 'suitability_risk_level', 'profile_status','created_at','updated_at')
    search_fields = ('card_number', 'en_first_name', 'en_last_name', 'th_first_name', 'email')
    list_filter = ('profile_status', 'suitability_risk_level', 'investor_type')
    change_list_template = "admin/stt_fundconnext/customerindividual/change_list.html"
    actions = ['create_invest_user_action']

    def create_invest_user_action(self, request, queryset):
        count = 0
        total_acc_count = 0
        for obj in queryset:
            # Map names
            full_name_en = f"{obj.en_first_name or ''} {obj.en_last_name or ''}".strip()
            full_name_th = f"{obj.th_first_name or ''} {obj.th_last_name or ''}".strip()
            
            # Map status
            status_val = 'Active' if obj.profile_status == 'ACTIVE' else 'Inactive'
            
            # Update/Create Investor
            investor, created = Investor.objects.update_or_create(
                card_number_encrypted=obj.card_number,
                defaults={
                    'compCode': 'MPS',
                    'custCode': obj.card_number,
                    'fullNameEn': full_name_en or 'N/A',
                    'fullNameTh': full_name_th or 'N/A',
                    'email': obj.email or '',
                    'mobile': obj.mobile_number or '',
                    'projects': 'mf',
                    'status': status_val,
                }
            )

            # Sync InvestorAccount
            accounts_data = obj.accounts or []
            acc_count_for_obj = 0
            for acc in accounts_data:
                acc_id = acc.get('accountId')
                if not acc_id:
                    continue
                
                # Parse approvedDateTime as openDate
                open_date = None
                approved_dt_str = acc.get('approvedDateTime')
                if approved_dt_str and len(approved_dt_str) >= 8:
                    try:
                        open_date = datetime.strptime(approved_dt_str[:8], "%Y%m%d").date()
                    except ValueError:
                        pass
                
                # Map account status
                acc_status_raw = acc.get('accountStatus', 'Active').capitalize()
                acc_status = 'Active' if acc_status_raw == 'Active' else 'Inactive'

                InvestorAccount.objects.update_or_create(
                    compCode='MPS',
                    accountID=acc_id,
                    defaults={
                        'custCode': investor,
                        'openDate': open_date,
                        'icLicense': acc.get('icLicense'),
                        'status': acc_status,
                    }
                )
                acc_count_for_obj += 1
            
            count += 1
            total_acc_count += acc_count_for_obj
        
        self.message_user(request, f"Successfully created/updated {count} invest users and {total_acc_count} accounts.")
    create_invest_user_action.short_description = "Create invest user"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-customer-individual/', self.admin_site.admin_view(self.run_etl_customer_individual_view), name='run_etl_customer_individual'),
        ]
        return custom_urls + urls

    def run_etl_customer_individual_view(self, request):
        from .tasks import run_daily_fundconnext_etl_customer_individual
        
        # Trigger the task asynchronously
        run_daily_fundconnext_etl_customer_individual.delay()
        
        self.message_user(request, "Task 'run_daily_fundconnext_etl_customer_individual' has been triggered in the background to fetch Customer Individuals.")
        return redirect("..")

class FundProfileResource(resources.ModelResource):
    class Meta:
        model = FundProfile

@admin.register(FundProfile)
class FundProfileAdmin(ImportExportModelAdmin):
    resource_class = FundProfileResource
    list_display = ('fund_code', 'amc_code', 'fund_name_th', 'fund_name_en', 'tax_type','fund_risk_level', 'registration_date')
    list_filter = ('amc_code','tax_type' ,'fund_risk_level')
    search_fields = ('fund_code', 'amc_code', 'fund_name_en', 'fund_name_th')
    change_list_template = "admin/stt_fundconnext/fundprofile/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-fund-profile/', self.admin_site.admin_view(self.run_etl_fund_profile_view), name='run_etl_fund_profile'),
        ]
        return custom_urls + urls

    def run_etl_fund_profile_view(self, request):
        from .tasks import run_daily_fundconnext_etl_fund_profile
        
        # Trigger the task asynchronously
        run_daily_fundconnext_etl_fund_profile.delay()
        
        self.message_user(request, "Task 'run_daily_fundconnext_etl_fund_profile' has been triggered in the background to fetch Fund Profiles.")
        return redirect("..")

class FundPerformanceResource(resources.ModelResource):
    class Meta:
        model = FundPerformance

@admin.register(FundPerformance)
class FundPerformanceAdmin(ImportExportModelAdmin):
    resource_class = FundPerformanceResource
    list_display = ('fund_code', 'nav_date', 'p_ytd_return', 'p_1y_return', 'p_3y_return', 'updated_at')
    search_fields = ('fund_code',)
    change_list_template = "admin/stt_fundconnext/fundperformance/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-fund-performance/', self.admin_site.admin_view(self.run_etl_fund_performance_view), name='run_etl_fund_performance'),
        ]
        return custom_urls + urls

    def run_etl_fund_performance_view(self, request):
        from .tasks import run_daily_fundconnext_etl_fund_performance
        
        # Trigger the task asynchronously
        run_daily_fundconnext_etl_fund_performance.delay()
        
        self.message_user(request, "Task 'run_daily_fundconnext_etl_fund_performance' has been triggered in the background to fetch Fund Performances.")
        return redirect("..")

class AssetAllocationResource(resources.ModelResource):
    class Meta:
        model = AssetAllocation

@admin.register(AssetAllocation)
class AssetAllocationAdmin(ImportExportModelAdmin):
    resource_class = AssetAllocationResource
    list_display = ('fund_code', 'investment_type_code', 'as_end_of', 'investment_size')
    search_fields = ('fund_code', 'investment_type_code', 'as_end_of')
    list_filter = ('as_end_of','investment_type_code',)
    change_list_template = "admin/stt_fundconnext/assetallocation/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-asset-allocation/', self.admin_site.admin_view(self.run_etl_asset_allocation_view), name='run_etl_asset_allocation'),
        ]
        return custom_urls + urls

    def run_etl_asset_allocation_view(self, request):
        from .tasks import run_daily_fundconnext_etl_asset_allocation
        
        # Trigger the task asynchronously
        run_daily_fundconnext_etl_asset_allocation.delay()
        
        self.message_user(request, "Task 'run_daily_fundconnext_etl_asset_allocation' has been triggered in the background to fetch Asset Allocations.")
        return redirect("..")

class TopHoldingResource(resources.ModelResource):
    class Meta:
        model = TopHolding

@admin.register(TopHolding)
class TopHoldingAdmin(ImportExportModelAdmin):
    resource_class = TopHoldingResource
    list_display = ('fund_code', 'securities_seq', 'securities_name', 'as_end_of', 'securities_invest_size')
    search_fields = ('fund_code', 'securities_name', 'as_end_of')
    list_filter = ('as_end_of',)
    change_list_template = "admin/stt_fundconnext/topholding/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-etl-top-holding/', self.admin_site.admin_view(self.run_etl_top_holding_view), name='run_etl_top_holding'),
        ]
        return custom_urls + urls

    def run_etl_top_holding_view(self, request):
        from .tasks import run_daily_fundconnext_etl_top_holding
        
        # Trigger the task asynchronously
        run_daily_fundconnext_etl_top_holding.delay()
        
        self.message_user(request, "Task 'run_daily_fundconnext_etl_top_holding' has been triggered in the background to fetch Top Holdings.")
        return redirect("..")


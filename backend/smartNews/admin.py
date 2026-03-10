from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Fund, FundAnalysis

@admin.register(Fund)
class FundAdmin(ImportExportModelAdmin):
    list_display = ('fund_code', 'fund_name_en', 'fund_risk_level', 'registration_date')
    search_fields = ('fund_code', 'fund_name_th', 'fund_name_en')
    list_filter = ('fund_risk_level', 'fif_flag', 'dividend_flag')

@admin.register(FundAnalysis)
class FundAnalysisAdmin(admin.ModelAdmin):
    list_display = ('fund', 'sentiment_score', 'last_analyzed')
    search_fields = ('fund__fund_code', 'fund__fund_name_en')

from django.contrib import admin
from .models import AssetManagementCompany, Fund, FundNAV, HoldingAsset, FundAnalysis, AIInsight, NewsArticle

@admin.register(AssetManagementCompany)
class AssetManagementCompanyAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name_th', 'name_en')
    search_fields = ('short_name', 'name_th', 'name_en')

@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'amc', 'fund_category', 'risk_level', 'is_dividend', 'fact_sheet_pdf')
    list_filter = ('risk_level', 'is_dividend', 'fund_category', 'amc')
    search_fields = ('fundCode', 'name_th', 'name_en')

@admin.register(FundNAV)
class FundNAVAdmin(admin.ModelAdmin):
    list_display = ('fund', 'date', 'nav', 'percent_change')
    list_filter = ('fund', 'date')
    search_fields = ('fund__fundCode',)

@admin.register(HoldingAsset)
class HoldingAssetAdmin(admin.ModelAdmin):
    list_display = ('fund', 'asset_name', 'proportion', 'as_of_date')
    list_filter = ('fund', 'as_of_date')
    search_fields = ('fund__fundCode', 'asset_name')

@admin.register(FundAnalysis)
class FundAnalysisAdmin(admin.ModelAdmin):
    list_display = ('fund', 'standard_deviation', 'sharpe_ratio_display', 'last_calculated')
    
    def sharpe_ratio_display(self, obj):
        return obj.fund.sharpe_ratio
    sharpe_ratio_display.short_description = 'Sharpe Ratio'

@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('fund', 'insight_type', 'confidence_score', 'sentiment_score', 'model_version', 'created_at')
    list_filter = ('insight_type', 'model_version', 'created_at')
    search_fields = ('fund__fundCode', 'content')

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_at', 'sentiment_score', 'impact_level')
    list_filter = ('source', 'impact_level', 'published_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('related_funds',)

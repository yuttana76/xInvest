from django.contrib import admin
from django import forms
from .models import AssetManagementCompany, FundInfo, FundNAV, FundHoldingAsset, FundAnalysis, AIInsight, NewsArticle

@admin.register(AssetManagementCompany)
class AssetManagementCompanyAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name_th', 'name_en')
    search_fields = ('short_name', 'name_th', 'name_en')

@admin.register(FundInfo)
class FundAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'amc', 'fund_category', 'risk_level')
    list_filter = ('risk_level', 'is_dividend', 'fund_category', 'amc')
    search_fields = ('fundCode', 'name_th', 'name_en')

@admin.register(FundAnalysis)
class FundAnalysisAdmin(admin.ModelAdmin):
    list_display = ('fund', 'standard_deviation', 'sharpe_ratio_display', 'last_calculated', 'sentiment_score', 'sentiment_impact_level', 'created_at', 'updated_at')
    search_fields = ('fund__fundCode',)
    readonly_fields = ('last_calculated', 'created_at', 'updated_at')

    def sharpe_ratio_display(self, obj):
        return obj.fund.sharpe_ratio
    sharpe_ratio_display.short_description = 'Sharpe Ratio'


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('fund', 'insight_type', 'sentiment_score', 'confidence_score', 'model_version', 'created_at')
    list_filter = ('insight_type', 'model_version')
    search_fields = ('fund__fundCode', 'content', 'insight_type')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


class NewsArticleAdminForm(forms.ModelForm):
    sectors = forms.MultipleChoiceField(
        choices=NewsArticle.INVESTMENT_SECTOR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Related Sectors"
    )

    class Meta:
        model = NewsArticle
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.related_sectors:
            self.initial['sectors'] = self.instance.related_sectors

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.related_sectors = self.cleaned_data.get('sectors', [])
        if commit:
            instance.save()
        return instance

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    form = NewsArticleAdminForm
    list_display = (
        'title', 'source', 'published_at',
        'ai_impact_level', 'ai_sentiment_score',
        'fund_supervisor_approve', 'fund_supervisor_approve_by',
        'published_status',
    )
    list_filter = ('fund_supervisor_approve', 'published_status', 'ai_impact_level', 'source')
    search_fields = ('title', 'source', 'content', 'related_funds__fundCode')
    filter_horizontal = ('related_funds',)
    readonly_fields = ('fund_supervisor_approve_at', 'published_at')
    ordering = ('-published_at',)
    fieldsets = (
        ('Article', {
            'fields': ('source', 'title', 'content', 'url', 'published_at', 'related_funds', 'sectors')
        }),
        ('AI Analysis', {
            'fields': ('ai_sentiment_score', 'ai_summary', 'ai_impact_level')
        }),
        ('Fund Manager Sentiment', {
            'fields': ('fm_sentiment_score', 'fm_summary', 'fm_impact_level')
        }),
        ('Approval', {
            'fields': (
                'fund_supervisor_approve', 'fund_supervisor_comment',
                'fund_supervisor_approve_at', 'fund_supervisor_approve_by',
            )
        }),
        ('Publication', {
            'fields': ('published_status', 'published_by')
        }),
    )

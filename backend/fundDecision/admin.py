from django.contrib import admin
from django import forms
from django.shortcuts import redirect
from .models import FundAnalysis, AIInsight, NewsArticle, FundFactSheet
from import_export.admin import ImportExportModelAdmin


@admin.register(FundAnalysis)
class FundAnalysisAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'standard_deviation', 'treynor_ratio', 'sortino_ratio', 'last_calculated', 'sentiment_score', 'sentiment_impact_level', 'created_at', 'updated_at')
    search_fields = ('fundCode',)
    readonly_fields = ('last_calculated', 'created_at', 'updated_at')


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'insight_type', 'sentiment_score', 'confidence_score', 'model_version', 'created_at')
    list_filter = ('fundCode','insight_type', 'model_version')
    search_fields = ('fundCode', 'content', 'insight_type')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = ['summarize_impact_for_fund']

    @admin.action(description="วิเคราะห์และสรุปผลกระทบระดับกองทุน (Fund Analysis)")
    def summarize_impact_for_fund(self, request, queryset):
        from .tasks import summarize_fund_impact_task
        
        # Group by fundCode
        fund_insights = {}
        for insight in queryset:
            if insight.fundCode not in fund_insights:
                fund_insights[insight.fundCode] = []
            fund_insights[insight.fundCode].append(insight.id)
            
        for fund_code, insight_ids in fund_insights.items():
            summarize_fund_impact_task.delay(fund_code, insight_ids)
            
        self.message_user(request, f"Triggered summary tasks for {len(fund_insights)} funds.")



class NewsArticleAdminForm(forms.ModelForm):
    
    relate_product = forms.MultipleChoiceField(
        choices=NewsArticle.RELATE_PRODUCT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Related Products"
    )

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
        if self.instance and self.instance.pk and self.instance.relate_product:
            self.initial['relate_product'] = self.instance.relate_product

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
        'title', 'source', 'published_at', 'relate_product',
        'author', 'ai_impact_level', 'ai_sentiment_score',
        'fund_supervisor_approve', 'published_status',
    )
    actions = ['analyze_with_ai', 'analyze_with_langgraph']
    list_filter = ('fund_supervisor_approve', 'published_status', 'ai_impact_level', 'source')
    search_fields = ('title', 'source', 'content', 'related_funds__fundCode')
    readonly_fields = ('fund_supervisor_approve_at', 'published_at')
    ordering = ('-published_at',)
    fieldsets = (
        ('Article', {
            'fields': ('source', 'title', 'author', 'description', 'content', 'url', 'image_url', 'relate_product', 'published_at', 'related_funds', 'sectors')
        }),
        ('AI Analysis', {
            'fields': ('ai_sentiment_score', 'ai_summary', 'ai_impact_level', 'ai_model')
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

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('fetch-news/', self.admin_site.admin_view(self.run_news_fetch_task), name='fetch-news'),
        ]
        return custom_urls + urls


    # Function exec task new fetch
    def run_news_fetch_task(self, request):
        from .tasks import fetch_daily_news

        fetch_daily_news.delay()

        self.message_user(request, "Task 'fetch_daily_news' has been queued to run in the background. Please check the logs or refresh in a few moments.")
        return redirect("..")

    @admin.action(description="Analyze selected articles with AI")
    def analyze_with_ai(self, request, queryset):
        from .tasks import analyze_news_article_task
        for article in queryset:
            analyze_news_article_task.delay(article.id)
        self.message_user(request, f"Triggered AI analysis for {queryset.count()} articles.")

    @admin.action(description="Analyze selected articles with LangGraph")
    def analyze_with_langgraph(self, request, queryset):
        from .tasks import analyze_news_langgraph_task
        for article in queryset:
            analyze_news_langgraph_task.delay(article.id)
        self.message_user(request, f"Triggered LangGraph analysis for {queryset.count()} articles.")


@admin.register(FundFactSheet)
class FundFactSheetAdmin(ImportExportModelAdmin):
    list_display = ('fund_code', 'fund_category', 'risk_level', 'as_of_date', 'ai_analysis_status', 'updated_at')
    search_fields = ('fund_code', 'fund_name_th')
    list_filter = ('ai_analysis_status', 'risk_level', 'investment_strategy')
    readonly_fields = ('created_at', 'updated_at', 'ai_error_message')
    actions = ['analyze_factsheet_with_ai']

    fieldsets = (
        ('Fund Information', {
            'fields': (
                'fund_code', 'fund_name_th', 'sec_proj_id', 
                'risk_level', 'fund_category', 'investment_strategy'
            )
        }),
        ('PDF Document', {
            'fields': ('factsheet_file', 'factsheet_url','prompt_val', 'as_of_date')
        }),
        ('Extracted Strategy & Context', {
            'fields': ('benchmark', 'dividend_policy', 'is_hedged', 'hedging_policy', 'currency_hedging')
        }),
        ('Extracted Data (JSON)', {
            'fields': ('holdings_data', 'sector_allocation')
        }),
        ('AI Analysis Status', {
            'fields': ('ai_analysis_status', 'ai_error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        is_new = not obj.pk
        # Check if file or url changed
        file_changed = 'factsheet_file' in form.changed_data
        url_changed = 'factsheet_url' in form.changed_data
        
        super().save_model(request, obj, form, change)
        
        # Trigger AI analysis if it's new and has data, or if data changed
        if (is_new or file_changed or url_changed) and (obj.factsheet_file or obj.factsheet_url):
            from .tasks import analyze_factsheet_task
            analyze_factsheet_task.delay(obj.id)
            self.message_user(request, f"AI analysis task triggered for {obj.fund_code}")

    @admin.action(description="Analyze selected Fact Sheets with AI")
    def analyze_factsheet_with_ai(self, request, queryset):
        from .tasks import analyze_factsheet_task
        for factsheet in queryset:
            analyze_factsheet_task.delay(factsheet.id)
        self.message_user(request, f"Triggered AI analysis for {queryset.count()} fact sheets.")
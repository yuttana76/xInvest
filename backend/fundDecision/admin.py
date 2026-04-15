from django.contrib import admin
from django import forms
from django.shortcuts import redirect
from .models import FundAnalysis, AIInsight, NewsArticle


@admin.register(FundAnalysis)
class FundAnalysisAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'standard_deviation', 'treynor_ratio', 'sortino_ratio', 'last_calculated', 'sentiment_score', 'sentiment_impact_level', 'created_at', 'updated_at')
    search_fields = ('fundCode',)
    readonly_fields = ('last_calculated', 'created_at', 'updated_at')


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ('fundCode', 'insight_type', 'sentiment_score', 'confidence_score', 'model_version', 'created_at')
    list_filter = ('insight_type', 'model_version')
    search_fields = ('fundCode', 'content', 'insight_type')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


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
    actions = ['analyze_with_ai']
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

        count = fetch_daily_news()

        self.message_user(request, f"Task 'fetch_daily_news' has been executed synchronously. Fetched {count} articles.")
        return redirect("..")

    @admin.action(description="Analyze selected articles with AI")
    def analyze_with_ai(self, request, queryset):
        from .tasks import analyze_news_article_task
        for article in queryset:
            analyze_news_article_task.delay(article.id)
        self.message_user(request, f"Triggered AI analysis for {queryset.count()} articles.")
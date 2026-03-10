from django.db import models

class Fund(models.Model):
    fund_code = models.CharField(max_length=30, unique=True)
    amc_code = models.CharField(max_length=15)
    fund_name_th = models.CharField(max_length=200)
    fund_name_en = models.CharField(max_length=200)
    fund_policy = models.TextField()
    tax_type = models.CharField(max_length=4, null=True, blank=True)
    fif_flag = models.BooleanField(default=False)
    dividend_flag = models.BooleanField(default=False)
    registration_date = models.DateField(null=True, blank=True)
    fund_risk_level = models.CharField(max_length=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fund_code} - {self.fund_name_en}"

class FundAnalysis(models.Model):
    fund = models.OneToOneField(Fund, on_delete=models.CASCADE, related_name='analysis')
    analysis_data = models.JSONField() # Industry proportions, fees, AI sentiment, expert notes
    sentiment_score = models.FloatField(default=0.0) # -1.0 to 1.0
    last_analyzed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.fund.fund_code}"

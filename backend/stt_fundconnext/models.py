from django.db import models

class FundProfile(models.Model):
    # Field sizes and names from data dictionary
    fund_code = models.CharField(max_length=30, primary_key=True)
    amc_code = models.CharField(max_length=15)
    fund_name_th = models.CharField(max_length=500)
    fund_name_en = models.CharField(max_length=500)
    fund_policy = models.CharField(max_length=1)
    tax_type = models.CharField(max_length=10, null=True, blank=True)
    fif_flag = models.CharField(max_length=1)
    dividend_flag = models.CharField(max_length=1)
    registration_date = models.DateField(null=True, blank=True)
    fund_risk_level = models.CharField(max_length=2)
    fx_risk_flag = models.CharField(max_length=1)
    fatca_allow_flag = models.CharField(max_length=1)
    buy_cut_off_time = models.CharField(max_length=4)
    fst_lowbuy_val = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    nxt_lowbuy_val = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    sell_cut_off_time = models.CharField(max_length=4)
    lowsell_val = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    lowsell_unit = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    lowbal_val = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    lowbal_unit = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    sell_settlement_day = models.IntegerField(null=True, blank=True)
    switching_settlement_day = models.IntegerField(null=True, blank=True)
    switch_out_flag = models.CharField(max_length=1)
    switch_in_flag = models.CharField(max_length=1)
    fund_class = models.CharField(max_length=30, null=True, blank=True)
    buy_period_flag = models.CharField(max_length=1)
    sell_period_flag = models.CharField(max_length=1)
    switch_in_period_flag = models.CharField(max_length=1, null=True, blank=True)
    switch_out_period_flag = models.CharField(max_length=1, null=True, blank=True)
    buy_pre_order_day = models.IntegerField(null=True, blank=True)
    sell_pre_order_day = models.IntegerField(null=True, blank=True)
    switch_pre_order_day = models.IntegerField(null=True, blank=True)
    auto_redeem_fund = models.CharField(max_length=300, null=True, blank=True)
    beg_ipo_date = models.DateField(null=True, blank=True)
    end_ipo_date = models.DateField(null=True, blank=True)
    plain_complex_fund = models.CharField(max_length=1)
    derivatives_flag = models.CharField(max_length=1)
    lag_allocation_day = models.IntegerField(null=True, blank=True)
    settlement_holiday_flag = models.CharField(max_length=1)
    health_insurance = models.CharField(max_length=1)
    previous_fund_code = models.CharField(max_length=30, null=True, blank=True)
    investor_alert = models.CharField(max_length=20, null=True, blank=True)
    isin = models.CharField(max_length=15, null=True, blank=True)
    lowbal_condition = models.CharField(max_length=1, null=True, blank=True)
    project_retail_type = models.CharField(max_length=1)
    fund_compare_performance_description = models.CharField(max_length=100, null=True, blank=True)
    allocate_digit = models.IntegerField(null=True, blank=True)
    etf_flag = models.CharField(max_length=1)
    trustee = models.CharField(max_length=1000, null=True, blank=True)
    registrar = models.CharField(max_length=1000, null=True, blank=True)
    register_id = models.CharField(max_length=15, null=True, blank=True)
    lmts_notice_period_amount = models.CharField(max_length=200, null=True, blank=True)
    lmts_notice_period_percent_aum = models.CharField(max_length=200, null=True, blank=True)
    lmts_adls_amount = models.CharField(max_length=200, null=True, blank=True)
    lmts_adls_percent_aum = models.CharField(max_length=200, null=True, blank=True)
    lmts_liquidity_fee_amount = models.CharField(max_length=200, null=True, blank=True)
    lmts_liquidity_fee_percent_aum = models.CharField(max_length=200, null=True, blank=True)
    other_information_url = models.CharField(max_length=200, null=True, blank=True)
    currency = models.CharField(max_length=3)
    complex_fund_presentation = models.CharField(max_length=200, null=True, blank=True)
    risk_acknowledgement_of_complex_fund = models.CharField(max_length=200, null=True, blank=True)
    redemption_type_condition = models.CharField(max_length=4, null=True, blank=True)
    internal_use = models.CharField(max_length=1, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stt_fundprofile'
        verbose_name = 'Fund Profile'
        verbose_name_plural = 'Fund Profiles'

    def __str__(self):
        return f"{self.fund_code} - {self.fund_name_en}"

class FundPerformance(models.Model):
    # Field sizes and names from data dictionary
    fund_code = models.CharField(max_length=30)
    p_ytd_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_3m_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_6m_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_1y_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_3y_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_5y_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_10y_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_si_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_1y_sd = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_3y_sd = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_5y_sd = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_10y_sd = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    nav_date = models.DateField()
    p_1m_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    p_1w_return = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    max_dd_1y = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    max_dd_3y = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    max_dd_5y = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)
    max_dd_10y = models.DecimalField(max_digits=18, decimal_places=5, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stt_fundperformance'
        verbose_name = 'Fund Performance'
        verbose_name_plural = 'Fund Performances'
        unique_together = ('fund_code', 'nav_date')

    def __str__(self):
        return f"{self.fund_code} - {self.nav_date}"

class AssetAllocation(models.Model):
    fund_code = models.CharField(max_length=30)
    investment_type_code = models.CharField(max_length=4)
    as_end_of = models.CharField(max_length=6, help_text="YYYYMM")
    investment_size = models.DecimalField(max_digits=20, decimal_places=5)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stt_assetallocation'
        verbose_name = 'Asset Allocation'
        verbose_name_plural = 'Asset Allocations'
        unique_together = ('fund_code', 'investment_type_code', 'as_end_of')

    def __str__(self):
        return f"{self.fund_code} - {self.investment_type_code} - {self.as_end_of}"

class TopHolding(models.Model):
    fund_code = models.CharField(max_length=30)
    securities_seq = models.IntegerField()
    securities_name = models.CharField(max_length=200)
    securities_abbreviation_name = models.CharField(max_length=50, null=True, blank=True)
    as_end_of = models.CharField(max_length=6, help_text="YYYYMM")
    securities_invest_size = models.DecimalField(max_digits=18, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stt_topholding'
        verbose_name = 'Top Holding'
        verbose_name_plural = 'Top Holdings'
        unique_together = ('fund_code', 'securities_seq', 'as_end_of')


class CustomerIndividual(models.Model):
    # identification
    card_number = models.CharField(max_length=20, unique=True, db_index=True)
    identification_card_type = models.CharField(max_length=50, null=True, blank=True)
    card_expiry_date = models.CharField(max_length=20, null=True, blank=True)
    accompanying_document = models.CharField(max_length=50, null=True, blank=True)
    
    # name
    title = models.CharField(max_length=50, null=True, blank=True)
    title_other = models.CharField(max_length=100, null=True, blank=True)
    en_first_name = models.CharField(max_length=200, null=True, blank=True)
    en_last_name = models.CharField(max_length=200, null=True, blank=True)
    th_first_name = models.CharField(max_length=200, null=True, blank=True)
    th_last_name = models.CharField(max_length=200, null=True, blank=True)
    
    # personal
    birth_date = models.CharField(max_length=20, null=True, blank=True)
    nationality = models.CharField(max_length=10, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    spouse = models.CharField(max_length=200, null=True, blank=True)
    
    # professional
    occupation_id = models.IntegerField(null=True, blank=True)
    occupation_other = models.CharField(max_length=200, null=True, blank=True)
    business_type_id = models.IntegerField(null=True, blank=True)
    business_type_other = models.CharField(max_length=200, null=True, blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    work_position = models.CharField(max_length=200, null=True, blank=True)
    
    # financial
    monthly_income_level = models.CharField(max_length=50, null=True, blank=True)
    asset_value = models.CharField(max_length=50, null=True, blank=True)
    income_source = models.CharField(max_length=200, null=True, blank=True)
    income_source_other = models.CharField(max_length=200, null=True, blank=True)
    income_source_country = models.CharField(max_length=10, null=True, blank=True)
    
    # compliance/risk
    related_political_person = models.BooleanField(default=False)
    political_related_person_position = models.CharField(max_length=200, null=True, blank=True)
    can_accept_fx_risk = models.BooleanField(default=False)
    can_accept_derivative_investment = models.BooleanField(default=False)
    suitability_risk_level = models.IntegerField(null=True, blank=True)
    suitability_evaluation_date = models.CharField(max_length=20, null=True, blank=True)
    fatca = models.BooleanField(default=False)
    fatca_declaration_date = models.CharField(max_length=20, null=True, blank=True)
    cdd_score = models.IntegerField(null=True, blank=True)
    cdd_date = models.CharField(max_length=20, null=True, blank=True)
    referral_person = models.CharField(max_length=200, null=True, blank=True)
    application_date = models.CharField(max_length=20, null=True, blank=True)
    accepted_by = models.CharField(max_length=200, null=True, blank=True)
    
    # settings
    open_fund_connext_form_flag = models.CharField(max_length=10, null=True, blank=True)
    approved_date = models.CharField(max_length=20, null=True, blank=True)
    approved_date_time = models.CharField(max_length=30, null=True, blank=True)
    open_channel = models.CharField(max_length=50, null=True, blank=True)
    investor_class = models.CharField(max_length=50, null=True, blank=True)
    vulnerable_flag = models.BooleanField(default=False)
    vulnerable_detail = models.TextField(null=True, blank=True)
    ndid_flag = models.BooleanField(default=False)
    ndid_request_id = models.CharField(max_length=200, null=True, blank=True)
    investor_type = models.CharField(max_length=50, null=True, blank=True)
    knowledge_assessment_result = models.BooleanField(default=False)
    profile_status = models.CharField(max_length=50, null=True, blank=True)
    
    # CRS
    crs_place_of_birth_country = models.CharField(max_length=10, null=True, blank=True)
    crs_place_of_birth_city = models.CharField(max_length=200, null=True, blank=True)
    crs_tax_residence_in_countries_other_than_the_us = models.BooleanField(default=False)
    crs_declaration_date = models.CharField(max_length=20, null=True, blank=True)
    
    # verification
    identity_verification_date_time = models.CharField(max_length=30, null=True, blank=True)
    dopa_verification_date_time = models.CharField(max_length=30, null=True, blank=True)
    
    # flags
    current_address_same_as_flag = models.CharField(max_length=50, null=True, blank=True)
    
    # Flexible JSON fields for nested data
    identification_document = models.JSONField(null=True, blank=True)
    current_address = models.JSONField(null=True, blank=True)
    work_address = models.JSONField(null=True, blank=True)
    suitability_form = models.JSONField(null=True, blank=True)
    knowledge_assessment_form = models.JSONField(null=True, blank=True)
    crs_details = models.JSONField(null=True, blank=True)
    accounts = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stt_customer_individual'
        verbose_name = 'Customer Individual'
        verbose_name_plural = 'Customer Individuals'

    def __str__(self):
        return f"{self.card_number} - {self.en_first_name} {self.en_last_name} ({self.th_first_name})"

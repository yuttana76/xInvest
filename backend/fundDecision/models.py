from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from pgvector.django import VectorField

class FundAnalysis(models.Model):  
    """เก็บค่าสถิติขั้นสูงที่ AI ต้องใช้ประมวลผล"""
    fundCode = models.CharField(max_length=20, verbose_name="ชื่อย่อกองทุน",null= False, blank= False)

    # Advanced Statistical Metrics
    standard_deviation = models.FloatField(null=True, blank=True, verbose_name="ค่าความผันผวน")
    treynor_ratio = models.FloatField(null=True, blank=True)
    sortino_ratio = models.FloatField(null=True, blank=True)
    information_ratio = models.FloatField(null=True, blank=True)
    capture_ratio_up = models.FloatField(null=True, blank=True, help_text="Upside Capture")
    capture_ratio_down = models.FloatField(null=True, blank=True, help_text="Downside Capture")

    # ข้อมูลสำหรับ AI Model (JSON format)
    raw_data_for_ai = models.JSONField(null=True, blank=True)
    last_calculated = models.DateTimeField(auto_now=True)

    # Summarised fund sentiment Analysis by fund manager & AI
    sentiment_score = models.FloatField(help_text="-1 (ร้ายสุด) ถึง 1 (ดีสุด)", null=True, blank=True) # bear = -1, bull = 1, neutral = 0
    sentiment_summary = models.TextField(blank=True, null=True, ) # สรุปสั้นๆ
    sentiment_impact_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MED', 'Medium'), ('HIGH', 'High')], null=True, blank=True)

    createBy = models.CharField(max_length=20, null=True, blank=True)
    updateBy = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AIInsight(models.Model):
    """เก็บผลลัพธ์ที่ AI วิเคราะห์และสรุปออกมา"""
    fundCode = models.CharField(max_length=20, verbose_name="ชื่อย่อกองทุน",null= False, blank= False)

    # ประเภทของ Insight เช่น 'RISK_WARNING', 'OPPORTUNITY', 'SUMMARY'
    insight_type = models.CharField(max_length=50)

    # ข้อความที่ AI สรุปให้ (รองรับ Markdown)
    content = models.TextField(verbose_name="บทวิเคราะห์จาก AI")

    # คะแนนความน่าเชื่อถือ หรือ Sentiment Score
    confidence_score = models.FloatField(default=0.0)
    sentiment_score = models.FloatField(default=0.0) # -1.0 ถึง 1.0

    model_version = models.CharField(max_length=50, help_text="ชื่อรุ่น AI เช่น GPT-4o, Claude-3")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class NewsArticle(models.Model):
    """เก็บข้อมูลข่าวสารรายวัน"""
    source = models.CharField(max_length=100) # เช่น Reuters, Bloomberg, SET
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(unique=True, max_length=1000)
    description = models.TextField(blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    published_at = models.DateTimeField(null=True, blank=True)

    RELATE_PRODUCT_CHOICES = [
        ('MF', 'Mutual Fund'),
        ('PF', 'Provident Fund'),
        ('BOND', 'Bond'),
        ]
        
    # relate product type(mf, pf, bond) can choose multi choice
    relate_product = models.JSONField(default=list, blank=True, help_text="List of products: MF, PF, Bond")

    # relate_product = models.CharField(max_length=20, null=True, blank=True, choices=RELATE_PRODUCT_CHOICES)
    
    # ความเกี่ยวข้องกับสินทรัพย์/กองทุน (type separate with ',')
    related_funds = models.CharField(max_length=255, verbose_name="ชื่อย่อกองทุน",null=True, blank=True)

    # choose from choices (investment_sector)
    # can choose multi choices
    INVESTMENT_SECTOR_CHOICES = [
        ('Tech', 'Tech'),
        ('Energy', 'Energy'),
        ('Healthcare', 'Healthcare'),
        ('Finance', 'Finance'),
        ('Consumer', 'Consumer'),
        ('Industrials', 'Industrials'),
        ('Materials', 'Materials'),
        ('Utilities', 'Utilities'),
        ('Real Estate', 'Real Estate'),
        ('Telecommunications', 'Telecommunications'),
    ]
    
    related_sectors = models.JSONField(default=list, blank=True, help_text="List of sectors: Tech, Energy, Healthcare, etc.")

    # ผลลัพธ์จาก AI Sentiment Analysis
    ai_model = models.CharField(max_length=100, null=True, blank=True)
    ai_sentiment_score = models.FloatField(help_text="-1 (ร้ายสุด) ถึง 1 (ดีสุด)", null=True, blank=True)
    ai_summary = models.TextField(blank=True, help_text="AI สรุปสั้นๆ ว่าข่าวนี้ส่งผลอย่างไร")
    ai_impact_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MED', 'Medium'), ('HIGH', 'High')], null=True, blank=True)
    
    # fund manager(fm) sentiment Analysis
    fm_sentiment_score = models.FloatField(help_text="-1 (ร้ายสุด) ถึง 1 (ดีสุด)", null=True, blank=True)
    fm_summary = models.TextField(blank=True, help_text="AI สรุปสั้นๆ ว่าข่าวนี้ส่งผลอย่างไร")
    fm_impact_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MED', 'Medium'), ('HIGH', 'High')], null=True, blank=True)

    # publish by fund supervisor
    published_status = models.BooleanField(default=False, help_text="เผยแพร่")
    published_by = models.CharField(max_length=100, null=True, blank=True)

    # fund supervisor approve
    fund_supervisor_approve = models.BooleanField(default=False, help_text="ผู้จัดการกองทุนอนุมัติ")
    fund_supervisor_comment = models.TextField(null=True, blank=True, help_text="ผู้จัดการกองทุนอนุมัติ")
    fund_supervisor_approve_at = models.DateTimeField(null=True, blank=True)
    fund_supervisor_approve_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class FundFactSheet(models.Model):
    # --- Identifiers ---
    fund_code = models.CharField(max_length=20, unique=True, verbose_name="รหัสกองทุน")
    fund_name_th = models.TextField(blank=True, verbose_name="ชื่อกองทุนภาษาไทย")
    sec_proj_id = models.CharField(max_length=50, blank=True, help_text="ID จาก SEC API")
    prompt_val = models.JSONField(null=True, blank=True, verbose_name="JSON Raw")

    # --- Core Strategy & Risk ---
    risk_level = models.IntegerField(null=True, blank=True, verbose_name="ระดับความเสี่ยง (1-8)")
    fund_category = models.TextField(blank=True, help_text="เช่น Equity Large-Cap, Global Bond")
    investment_strategy = models.CharField(max_length=50, blank=True, choices=[('Active', 'Active'), ('Passive', 'Passive')])

    # --- Advanced Context for AI ---
    holdings_data = models.JSONField(null=True, blank=True, verbose_name="ข้อมูลการถือครองหุ้น 5-10 อันดับแรก")
    sector_allocation = models.JSONField(null=True, blank=True, help_text="สัดส่วนกลุ่มอุตสาหกรรม เช่น พลังงาน 20%, แบงก์ 15%")

    # --- Currency & Global Impact ---
    is_hedged = models.BooleanField(default=False)
    hedging_policy = models.TextField(blank=True, help_text="นโยบายป้องกันความเสี่ยงค่าเงินแบบละเอียด")
    currency_hedging = models.CharField(max_length=50, blank=True, help_text="None/Partial/Fully/Discretionary")

    # --- Performance Metrics ---
    benchmark = models.TextField(blank=True)
    dividend_policy = models.BooleanField(default=False, verbose_name="นโยบายจ่ายปันผล")

    # --- Metadata ---
    factsheet_file = models.FileField(upload_to='fact_sheets/', null=True, blank=True, verbose_name="ไฟล์ Fund Fact Sheet (PDF)")
    factsheet_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="ลิงก์ Fund Fact Sheet (URL)")
    as_of_date = models.DateField(null=True, blank=True, help_text="ข้อมูลใน Fact Sheet นี้เป็นข้อมูล ณ วันที่เท่าไหร่")
    
    ai_analysis_status = models.CharField(max_length=20, default='PENDING', choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ])
    ai_error_message = models.TextField(blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fund Fact Sheet"
        verbose_name_plural = "Fund Fact Sheets"
        ordering = ['-as_of_date', '-created_at']

    def __str__(self):
        return f"{self.fund_code} - {self.fund_name_th or 'Unknown Fund'}"

class FundDocumentChunk(models.Model):
    """เก็บข้อมูลเนื้อหาจาก PDF แบ่งเป็นส่วนๆ เพื่อใช้ทำ RAG"""
    fund_code = models.CharField(max_length=20, verbose_name="รหัสกองทุน")
    content = models.TextField(verbose_name="เนื้อหา")
    embedding = VectorField(dimensions=768, verbose_name="Vector Embedding") # dimensions=768 สำหรับ Gemini
    page_number = models.IntegerField(null=True, blank=True, verbose_name="เลขหน้า")
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fund Document Chunk"
        verbose_name_plural = "Fund Document Chunks"
        indexes = [
            # การทำ HNSW index สำหรับ vector search จะต้องทำผ่าน migration แบบ manual
        ]

    def __str__(self):
        return f"{self.fund_code} - Page {self.page_number} - {self.content[:30]}..."

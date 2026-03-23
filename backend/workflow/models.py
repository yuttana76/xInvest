from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class WorkflowConfig(models.Model):
    name = models.CharField(max_length=100)  # เช่น "IT System Change Flow"
    category = models.CharField(max_length=50)  # ประเภทงานที่ใช้ Flow นี้
    description = models.TextField(blank=True)
    prefix = models.CharField(max_length=10, default="REQ", verbose_name="รหัสเรียกหน้าชื่อ")

    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    workflow = models.ForeignKey(WorkflowConfig, on_delete=models.CASCADE, related_name='steps')
    step_number = models.PositiveSmallIntegerField()  # ลำดับที่ 1, 2, 3...
    step_name = models.CharField(max_length=100)  # เช่น "หัวหน้าอนุมัติ", "ฝ่ายตรวจสอบ"

    # กำหนดสิทธิ์ผู้มีสิทธิ์อนุมัติ (ใช้ django Group เพื่อความยืดหยุ่น หรือระบุตัวบุคคล)
    required_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    is_department_manager = models.BooleanField(default=False, verbose_name="เป็นหัวหน้าแผนกของผู้สร้าง")

    class Meta:
        ordering = ['step_number']
        unique_together = ['workflow', 'step_number']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.step_number}: {self.step_name}"

class Request(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('RETURNED', 'Returned for Revision'),
        ('APPROVED', 'Approved (Waiting Execution)'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
    ]
    req_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    workflow = models.ForeignKey(WorkflowConfig, on_delete=models.PROTECT)

    # ผู้สร้างคำขอ
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_requests')
    create_department = models.CharField(max_length=50,null=True, blank=True)

    # สถานะปัจจุบัน
    current_step_number = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # ข้อมูลผู้ปฏิบัติงาน (Step สุดท้าย หรือหลังจากได้รับอนุมัติ)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')

    # บันทึกวันเวลา
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)  # บันทึกเวลาที่งานเสร็จจริง

    # Rating System (Optional)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    rating_comment = models.TextField(null=True, blank=True)

    def get_current_step_info(self):
        return self.workflow.steps.filter(step_number=self.current_step_number).first()

    def save(self, *args, **kwargs):
        if not self.req_code:
            from django.utils import timezone
            import datetime
            
            # 1. Get Prefix
            prefix = self.workflow.prefix if self.workflow.prefix else "REQ"
            
            # 2. Get Date String (ddmmyy)
            date_str = timezone.now().strftime("%d%m%y")
            
            # 3. Find the next running number for today
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + datetime.timedelta(days=1)
            
            # Filter requests with same prefix and date
            # We look for codes starting with prefix-date-
            code_prefix = f"{prefix}-{date_str}-"
            last_req = Request.objects.filter(
                req_code__startswith=code_prefix
            ).order_by('-req_code').first()
            
            if last_req:
                try:
                    last_num = int(last_req.req_code.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
                
            self.req_code = f"{code_prefix}{new_num:03d}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.req_code}] {self.title}" if self.req_code else self.title

class ApprovalLog(models.Model):
    ACTION_CHOICES = [
        ('APPROVE', 'อนุมัติ'),
        ('RETURN', 'ส่งกลับไปแก้ไข'),
        ('REJECT', 'ปฏิเสธคำขอ'),
        ('RESUBMIT', 'แก้ไขและส่งใหม่'),
        ('COMPLETE', 'ดำเนินการเสร็จสิ้น'),
    ]

    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='logs')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="ผู้ดำเนินการ")

    # บันทึกสถานะขณะนั้น
    step_number = models.PositiveSmallIntegerField(verbose_name="ขั้นตอนที่")
    step_name = models.CharField(max_length=100, verbose_name="ชื่อขั้นตอน")

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True, null=True, verbose_name="บันทึกความเห็น")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันเวลาที่ดำเนินการ")

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.request.title} - {self.action} by {self.approver}"

class RequestFile(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='workflow/requests/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"File for {self.request.title}"

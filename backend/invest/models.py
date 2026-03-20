from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MarketingGroup(models.Model):
    groupName = models.CharField(max_length=100, verbose_name="ชื่อกลุ่ม/ทีม")
    description = models.TextField(null=True, blank=True)
    # กำหนดหัวหน้ากลุ่ม (เลือกจาก Marketing)
    leader = models.ForeignKey(
        'Marketing', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='led_groups'
    )

    def __str__(self):
        return self.groupName

class Marketing(models.Model):
    # เชื่อมกับระบบ Auth ของ Django เพื่อให้ Login ได้
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='marketing_profile',null=True, blank=True)
    # เชื่อมโยงกับกลุ่ม
    group = models.ForeignKey(
        MarketingGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='members'
    )

    compCode = models.CharField(max_length=15)
    license_code = models.CharField(max_length=10)
    fullName = models.CharField(max_length=100)

    # เพิ่ม Supervisor (ชี้กลับมาที่ตัวเอง)
    # Hierarchy รายบุคคล (ยังคงไว้เผื่อกรณีสายงานข้ามกลุ่ม)
    supervisor = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates'
    )

    # ระดับตำแหน่ง (ใช้ช่วยในการแบ่ง Manager/Supervisor/Staff)
    ROLE_CHOICES = [
        ('STAFF', 'Marketing Staff'),
        ('GROUP_LEADER', 'Group Leader'), # เพิ่ม Role สำหรับหัวหน้ากลุ่ม
        ('MANAGER', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STAFF')

    def __str__(self):
        return f"{self.fullName} ({self.role})"

class ExternalAgent(models.Model):
    # เชื่อมกับ User สำหรับ Login
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile',null=True, blank=True)
    agentCode = models.CharField(max_length=20, unique=True)
    fullName = models.CharField(max_length=100)
    contactNumber = models.CharField(max_length=20, null=True, blank=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.agentCode} - {self.fullName}"

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='investor_profile', null=True, blank=True)
    compCode = models.CharField(max_length=13)
    custCode = models.CharField(max_length=13)
    fullNameEn = models.CharField(max_length=100)
    fullNameTh = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10, null=True, blank=True)
    email = models.CharField(max_length=100)
    projects = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    suitDate = models.DateField(null=True, blank=True)
    cardExpireDate = models.DateField(null=True, blank=True)
    nextKycDate = models.DateField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('compCode', 'custCode')

    def __str__(self):
        return f"{self.custCode} - {self.fullNameEn}"

class InvestorAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='accounts')
    accountID = models.CharField(max_length=15)
    openDate = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    # เพิ่ม Marketing 
    marketing = models.ForeignKey(Marketing, on_delete=models.SET_NULL, null=True, blank=True, related_name='mf_accounts')

    # เพิ่ม field ผู้แนะนำ (เป็น Optional เพราะลูกค้าบางรายอาจเดินเข้ามาเอง)
    referred_by_agent = models.ForeignKey(
        ExternalAgent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referred_mfaccount'
    )
    
    class Meta:
        unique_together = ('compCode', 'accountID')

    def __str__(self):
        return f"{self.accountID} ({self.compCode})"

class AccountBalance(models.Model):
    compCode = models.CharField(max_length=15)
    accountID = models.ForeignKey(InvestorAccount, on_delete=models.CASCADE, related_name='balances')
    fundCode = models.CharField(max_length=30)
    unitBalance = models.DecimalField(max_digits=18, decimal_places=4)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    averageCost = models.DecimalField(max_digits=13, decimal_places=4, null=True, blank=True)
    NAV = models.DecimalField(max_digits=13, decimal_places=4)
    NAVdate = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

class BondAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='bond_accounts')
    bondCode = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    fromDate = models.DateField(null=True, blank=True)
    toDate = models.DateField(null=True, blank=True)

    issuer = models.CharField(max_length=50, null=True, blank=True)
    bondSymbol = models.CharField(max_length=50, null=True, blank=True)

    paymentDate = models.DateField(null=True, blank=True)
    paymentAmount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    paymentType = models.CharField(max_length=50, null=True, blank=True)
    paymentStatus = models.CharField(max_length=50, null=True, blank=True)

    channel = models.CharField(max_length=50, null=True, blank=True)
    maturityDate = models.DateField(null=True, blank=True)
    maturityAmount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    maturityType = models.CharField(max_length=50, null=True, blank=True)
    maturityStatus = models.CharField(max_length=50, null=True, blank=True)
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Matured', 'Matured'),
        ('Default', 'Default'),
        ('Suspended', 'Suspended'),
        ('Expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    # เพิ่ม Marketing 
    marketing = models.ForeignKey(Marketing, on_delete=models.SET_NULL, null=True, blank=True, related_name='bond_accounts')

    # เพิ่ม field ผู้แนะนำ (เป็น Optional เพราะลูกค้าบางรายอาจเดินเข้ามาเอง)
    referred_by_agent = models.ForeignKey(
        ExternalAgent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referred_bond_account'
    )
    def __str__(self):
        return f"{self.custCode} - {self.bondCode or 'Bond'} ({self.compCode})"

class PrivateFundAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='private_fund_accounts')
    accountID = models.CharField(max_length=15)
    fundType = models.CharField(max_length=50, null=True, blank=True)
    openDate = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    # เพิ่ม Marketing 
    marketing = models.ForeignKey(Marketing, on_delete=models.SET_NULL, null=True, blank=True, related_name='pf_accounts')

    # เพิ่ม field ผู้แนะนำ (เป็น Optional เพราะลูกค้าบางรายอาจเดินเข้ามาเอง)
    referred_by_agent = models.ForeignKey(
        ExternalAgent, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referred_pf_account'
    )

    class Meta:
        unique_together = ('compCode', 'accountID')

    def __str__(self):
        return f"{self.accountID} ({self.compCode})"

class PrivateFundBalance(models.Model):
    compCode = models.CharField(max_length=15)
    accountID = models.ForeignKey(PrivateFundAccount, on_delete=models.CASCADE, related_name='private_fund_balances')
    fundCode = models.CharField(max_length=30)
    unitBalance = models.DecimalField(max_digits=18, decimal_places=4)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    averageCost = models.DecimalField(max_digits=13, decimal_places=4, null=True, blank=True)
    NAV = models.DecimalField(max_digits=13, decimal_places=4)
    NAVdate = models.DateField()

    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

# For Performance calculate
class PerformanceMFAccountBalance(models.Model):
    
    compCode = models.CharField(max_length=15)
    accountID = models.ForeignKey(InvestorAccount, on_delete=models.CASCADE, related_name='performance_balances')
    fundCode = models.CharField(max_length=30)
    unitBalance = models.DecimalField(max_digits=18, decimal_places=4)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    averageCost = models.DecimalField(max_digits=13, decimal_places=4, null=True, blank=True)
    NAV = models.DecimalField(max_digits=13, decimal_places=4)
    NAVdate = models.DateField()
    date = models.DateField(db_index=True,null=True,blank=True)
    marketValue = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    unrealizedGain = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    roi_percent = models.DecimalField(max_digits=10, decimal_places=4,null=True,blank=True)
    business_date_str = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode','NAVdate')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

class PerformancePrivateFundBalance(models.Model):
    compCode = models.CharField(max_length=15)
    accountID = models.ForeignKey(PrivateFundAccount,db_index=True,on_delete=models.CASCADE, related_name='performance_private_fund_balances')
    fundCode = models.CharField(max_length=30)
    #Unit
    unitBalance = models.DecimalField(max_digits=18, decimal_places=4)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    averageCost = models.DecimalField(max_digits=13, decimal_places=4, null=True, blank=True)
    #Current Price
    NAV = models.DecimalField(max_digits=13, decimal_places=4)
    #dataAsOf
    NAVdate = models.DateField()
    date = models.DateField(db_index=True,null=True,blank=True)
    marketValue = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    unrealizedGain = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    roi_percent = models.DecimalField(max_digits=10, decimal_places=4,null=True,blank=True)

    #SIS Capital Value
    sis_capital_value = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    #Gain Loss
    gain_loss = models.DecimalField(max_digits=18, decimal_places=2,null=True,blank=True)
    #Gain Loss Percent
    gain_loss_percent = models.DecimalField(max_digits=10, decimal_places=4,null=True,blank=True)
    #pct_by_port
    pct_by_port = models.DecimalField(max_digits=10, decimal_places=4,null=True,blank=True)

    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode','NAVdate')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

class MFTransaction(models.Model):
    saOrderReferenceNo = models.CharField(max_length=30, null=True, blank=True)
    transactionDateTime = models.DateTimeField(null=True, blank=True)
    accountID = models.ForeignKey(InvestorAccount, on_delete=models.CASCADE, related_name='mf_transactions', null=True, blank=True)
    amcCode = models.CharField(max_length=15)
    unitholderID = models.CharField(max_length=15)
    transactionCode = models.CharField(max_length=3)
    fundCode = models.CharField(max_length=30, null=True, blank=True)
    overrideRiskProfileFlag = models.CharField(max_length=1)
    redemptionType = models.CharField(max_length=4, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    unit = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    effectiveDate = models.DateField()
    paymentType = models.CharField(max_length=8)
    bankCode = models.CharField(max_length=4, null=True, blank=True)
    bankAccount = models.CharField(max_length=20, null=True, blank=True)
    marketingCode = models.CharField(max_length=10, blank=True, null=True)
    branchNo = models.CharField(max_length=5)
    channel = models.CharField(max_length=3)
    transactionID = models.CharField(max_length=17)
    status = models.CharField(max_length=10)
    aMCOrderReferenceNo = models.CharField(max_length=30, null=True, blank=True)
    allotmentDate = models.DateField(null=True, blank=True)
    allottedNAV = models.DecimalField(max_digits=13, decimal_places=4, null=True, blank=True)
    allottedAmount = models.DecimalField(max_digits=21, decimal_places=4, null=True, blank=True)
    allotedUnit = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    fee = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    withholdingTax = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    vat = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    brokerageFee = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amcPayDate = models.DateField(null=True, blank=True)
    rejectReason = models.CharField(max_length=50, null=True, blank=True)
    iCCode = models.CharField(max_length=10, null=True, blank=True)
    brokerageFeeVAT = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    navDate = models.DateField(null=True, blank=True)
    collateralAccount = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transactionDateTime} - {self.fundCode} - {self.transactionCode} - {self.status}"

    class Meta:
        unique_together = ('accountID', 'fundCode','transactionID')

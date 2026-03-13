from django.db import models
from django.contrib.auth.models import User

class ICLicense(models.Model):
    compCode = models.CharField(max_length=15)
    IC_license = models.CharField(max_length=10)
    fullName = models.CharField(max_length=100)

    class Meta:
        unique_together = ('compCode', 'IC_license')
        verbose_name = "IC License"
        verbose_name_plural = "IC Licenses"

    def __str__(self):
        return f"{self.IC_license} - {self.fullName}"

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='investor_profile', null=True, blank=True)
    compCode = models.CharField(max_length=13)
    custCode = models.CharField(max_length=13)
    fullNameEn = models.CharField(max_length=100)
    fullNameTh = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10, null=True, blank=True)
    email = models.CharField(max_length=100)
    projects = models.CharField(max_length=100)
    status = models.CharField(max_length=10)

    class Meta:
        unique_together = ('compCode', 'custCode')

    def __str__(self):
        return f"{self.custCode} - {self.fullNameEn}"

class InvestorAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='accounts')
    accountID = models.CharField(max_length=15)
    IC_license = models.ForeignKey(ICLicense, on_delete=models.SET_NULL, null=True, blank=True, related_name='accounts')
    openDate = models.DateField(null=True, blank=True)

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

    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

class BondAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='bond_accounts')
    bondCode = models.CharField(max_length=50, null=True, blank=True)
    Amount = models.DecimalField(max_digits=18, decimal_places=2)
    FromDate = models.DateField(null=True, blank=True)
    ToDate = models.DateField(null=True, blank=True)
    Status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.custCode} - {self.bondCode or 'Bond'} ({self.compCode})"

class PrivateFundAccount(models.Model):
    compCode = models.CharField(max_length=13)
    custCode = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='private_fund_accounts')
    accountID = models.CharField(max_length=15)
    IC_license = models.ForeignKey(ICLicense, on_delete=models.SET_NULL, null=True, blank=True, related_name='private_fund_accounts')
    openDate = models.DateField(null=True, blank=True)

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
    class Meta:
        unique_together = ('compCode', 'accountID', 'fundCode','NAVdate')

    def __str__(self):
        return f"{self.accountID} - {self.fundCode}"

class PerformancePrivateFundBalance(models.Model):
    compCode = models.CharField(max_length=15)
    accountID = models.ForeignKey(PrivateFundAccount,db_index=True,on_delete=models.CASCADE, related_name='performance_private_fund_balances')
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
    iCLicense = models.CharField(max_length=10)
    branchNo = models.CharField(max_length=5)
    channel = models.CharField(max_length=3)
    transactionID = models.CharField(max_length=17, unique=True)
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

    def __str__(self):
        return f"{self.transactionDateTime} - {self.fundCode} - {self.transactionCode} - {self.status}"

    class Meta:
        unique_together = ('accountID', 'fundCode','transactionID')

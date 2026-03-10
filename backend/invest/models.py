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

import os
import requests
import zipfile
import io
import csv
from datetime import datetime
from django.conf import settings
from decimal import Decimal
from django.db import transaction
from invest.models import MFTransaction, PerformanceMFAccountBalance, InvestorAccount, AccountBalance
from invest.services import util

import logging
logger = logging.getLogger(__name__)

class FundConnextService:
    def __init__(self):
        logger.info(f"FC_API_USER: {settings.FC_API_USER}")

        self.base_url = f"https://{settings.FC_API_URL}" if not settings.FC_API_URL.startswith("http") else settings.FC_API_URL
        self.username = settings.FC_API_USER
        self.password = settings.FC_API_PASSWORD

    def login(self):
        url = f"{self.base_url}/api/auth"
        headers = {"Content-Type": "application/json"}
        data = {
            "username": self.username,
            "password": self.password
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json().get("access_token")
        except requests.exceptions.RequestException as e:
            logger.error(f"FundConnext Login Failed: {e}")
            raise

    def download_file(self, business_date, file_type, token):
        url = f"{self.base_url}/api/files/{business_date}/{file_type}.zip"
        headers = {
            "X-Auth-Token": token,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {file_type} for date {business_date}: {e}")
            raise

    def find_header_row_and_dialect(self, lines, expected_column):
        """Helper to find where the actual CSV payload begins and guess the dilimiter."""
        for i, line in enumerate(lines):
            if expected_column.lower() in line.lower():
                dialect = csv.Sniffer().sniff(line) if ',' in line or '|' in line else None
                # Default to pipe if can't sniff it
                delimiter = dialect.delimiter if dialect else '|'
                return i, delimiter
        return -1, '|'

    def safe_decimal(self, val):
        if not val or not val.strip():
            return None
        try:
            return Decimal(val.strip().replace(',', ''))
        except (ValueError, TypeError):
            return None

    def safe_date(self, val, fmt='%Y%m%d'):
        if not val or not val.strip():
            return None
        try:
            return datetime.strptime(val.strip(), fmt).date()
        except ValueError:
            return None
            
    def safe_datetime(self, val, fmt='%Y%m%d%H%M%S'):
        if not val or not val.strip():
            return None
        try:
            return datetime.strptime(val.strip(), fmt)
        except ValueError:
            return None

    def process_allotted_transactions(self, zip_content):
        logger.info('* Welcome to Allotted Transactions')
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
                
        lines = content.splitlines()
        transactions_to_create = []
        skipped_missing_account = 0

        for line in lines:
            line = line.strip()
            # Skip header/footer or empty lines
            if not line or (line.startswith('202') and len(line.split('|')) < 5):
                continue

            parts = line.split('|')
            if len(parts) < 19: # Basic check for minimum fields including Transaction ID at 18
                continue

            # Field mappings (Positional - Adjusted to match user's preferred layout)
            # 0: SA Order Ref, 1: Account ID, 2: Transaction DateTime, 3: AMC Code, 4: Unitholder ID
            # 5: Transaction Code, 6: Fund Code, 7: Override Risk, 8: Redemption Type
            # 9: Amount, 10: Unit, 11: Effective Date, 12: Payment Type, 13: Bank Code
            # 14: Bank Account, 15: IC License, 16: Branch No, 17: Channel, 18: Transaction ID
            # 19: Status ... and so on
            
            account_id_val = parts[2].strip()
            trans_id = parts[30].strip()

            if not account_id_val:
                continue

            try:
                account = InvestorAccount.objects.get(accountID=account_id_val)
            except InvestorAccount.DoesNotExist:
                skipped_missing_account += 1
                continue

            status_val = parts[31].strip()

            # If transaction already exists, skip
            if MFTransaction.objects.filter(transactionID=trans_id, accountID=account, status=status_val).exists():
                continue

            trans = MFTransaction(
                saOrderReferenceNo=parts[0].strip(),
                # transactionDateTime=self.safe_datetime(parts[2]),
                transactionDateTime=self.safe_date(parts[2]) if len(parts) > 2 else None,
                accountID=account,
                amcCode=parts[3].strip(),
                unitholderID=parts[4].strip(),
                transactionCode=parts[6].strip(),
                fundCode=parts[7].strip(),
                overrideRiskProfileFlag=parts[8].strip(),
                redemptionType=parts[10].strip(),
                amount=self.safe_decimal(parts[11]),
                unit=self.safe_decimal(parts[12]),
                effectiveDate=self.safe_date(parts[13]),
                paymentType=parts[16].strip(),
                bankCode=parts[17].strip(),
                bankAccount=parts[18].strip(),
                marketingCode=parts[21].strip(),
                branchNo=parts[22].strip(),
                channel=parts[23].strip(),
                transactionID=trans_id,
                status=status_val,
                allotmentDate=self.safe_date(parts[33]) if len(parts) > 33 else None,
                allottedNAV=self.safe_decimal(parts[34]) if len(parts) > 34 else None,
                allottedAmount=self.safe_decimal(parts[35]) if len(parts) > 35 else None,
                allotedUnit=self.safe_decimal(parts[36]) if len(parts) > 36 else None,
                fee=self.safe_decimal(parts[37]) if len(parts) > 37 else None,
                withholdingTax=self.safe_decimal(parts[38]) if len(parts) > 38 else None,
                vat=self.safe_decimal(parts[39]) if len(parts) > 39 else None,
                brokerageFee=self.safe_decimal(parts[40]) if len(parts) > 40 else None,
                amcPayDate=self.safe_date(parts[42]) if len(parts) > 42 else None,
                rejectReason=parts[47].strip() if len(parts) > 47 else '',
                iCCode=parts[48].strip() if len(parts) > 48 else '',
                brokerageFeeVAT=self.safe_decimal(parts[52]) if len(parts) > 52 else None,
                navDate=self.safe_date(parts[54]) if len(parts) > 54 else None,
                collateralAccount=parts[55].strip() if len(parts) > 55 else '',
            )
            transactions_to_create.append(trans)

        if skipped_missing_account > 0:
            logger.warning(f"Skipped {skipped_missing_account} Allotted Transaction records because InvestorAccount does not exist in DB.")

        if transactions_to_create:
            with transaction.atomic():
                MFTransaction.objects.bulk_create(transactions_to_create, ignore_conflicts=True)
            logger.info(f"Successfully processed {len(transactions_to_create)} Allotted Transactions.")
        else:
            logger.info("Parsing finished, but 0 brand new transactions were created.")

    def process_unitholder_performance_mf_balance(self, business_date_str, zip_content):

        logger.info('* Welcome to Unitholder Balance')

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
                
        lines = content.splitlines()

        balances_to_create = []
        skipped_missing_account = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('202') and len(line.split('|')) < 5: 
                # Skip header/footer
                continue

            parts = line.split('|')
            if len(parts) < 14:
                continue

            # Field mappings based on FNC UnitholderBalance standard:
            # 0: AMC Code, 1: Account ID , 2:Unitholder ID , 3: Fund Code
            # 4: Outstanding Unit, 5: Outstanding Amount
            # 6: Available Unit, 7: Available Amount
            # 8: Pending Unit, 9: Pending Amount
            # 10: Pledge Unit, 11: Average Cost, 12: NAV, 13: NAV Date
            account_id_val = parts[1].strip()
            fund_code_val = parts[3].strip()
            unit_balance_val = parts[4] # Outstanding Unit
            amount_val = parts[5] # Outstanding Amount
            average_cost_val = parts[11]
            nav_val = parts[12]
            nav_date_val = parts[13]

            # Skip if account ID is empty or unit balance is 0
            if not account_id_val or  int(float(unit_balance_val)) <= 0:
                continue


            try:
                account = InvestorAccount.objects.get(accountID=account_id_val)
            except InvestorAccount.DoesNotExist:
                skipped_missing_account += 1
                continue

            comp_code = account.compCode


            # Calculate performance
            unitBalance_val=self.safe_decimal(unit_balance_val)
            amount_val=self.safe_decimal(amount_val)
            averageCost_val=self.safe_decimal(average_cost_val)
            NAV_val=self.safe_decimal(nav_val)
            NAVdate_val=self.safe_date(nav_date_val)
            date_val=self.safe_date(nav_date_val)

            mkt_val, gain, roi = util.calculate_performance(unitBalance_val, NAV_val, averageCost_val)
            logger.info(f"*** mkt_val: {mkt_val}, gain: {gain}, roi: {roi}")

            bal = PerformanceMFAccountBalance(
                compCode=comp_code,
                accountID=account,
                fundCode=fund_code_val,
                unitBalance=unitBalance_val,
                amount=amount_val,
                averageCost=averageCost_val,
                NAV=NAV_val,
                NAVdate=NAVdate_val,
                date=date_val,
                marketValue=mkt_val,
                unrealizedGain=gain,
                roi_percent=roi,
                business_date_str=business_date_str
            )
            balances_to_create.append(bal)

        if skipped_missing_account > 0:
            logger.warning(f"Skipped {skipped_missing_account} UnitholderBalance records because InvestorAccount does not exist in DB.")

        if balances_to_create:
            with transaction.atomic():
                PerformanceMFAccountBalance.objects.bulk_create(balances_to_create, ignore_conflicts=True)
            logger.info(f"Successfully processed {len(balances_to_create)} Unitholder Balances.")
        else:
            logger.info("Parsing finished, but 0 brand new balances were created.")

    def process_unitholder_current_mf_balance(self, zip_content):

        logger.info('* Welcome to Unitholder Balance')

        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
                
        lines = content.splitlines()

        balances_to_create = []
        skipped_missing_account = 0
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('202') and len(line.split('|')) < 5: 
                # Skip header/footer
                continue

            parts = line.split('|')
            if len(parts) < 14:
                continue

            # Field mappings based on FNC UnitholderBalance standard:
            # 0: AMC Code, 1: Account ID , 2:Unitholder ID , 3: Fund Code
            # 4: Outstanding Unit, 5: Outstanding Amount
            # 6: Available Unit, 7: Available Amount
            # 8: Pending Unit, 9: Pending Amount
            # 10: Pledge Unit, 11: Average Cost, 12: NAV, 13: NAV Date
            account_id_val = parts[1].strip()
            fund_code_val = parts[3].strip()
            unit_balance_val = parts[4] # Outstanding Unit
            amount_val = parts[5] # Outstanding Amount
            average_cost_val = parts[11]
            nav_val = parts[12]
            nav_date_val = parts[13]

            if account_id_val=="M1901362":
                logger.info(f"Processing UnitholderBalance: {account_id_val} - F:{fund_code_val} - U:{unit_balance_val} - A:{amount_val}")

            # Skip if account ID is empty or unit balance is 0
            if not account_id_val or  int(float(unit_balance_val)) <= 0:
                continue

            try:
                account = InvestorAccount.objects.get(accountID=account_id_val)
            except InvestorAccount.DoesNotExist:
                skipped_missing_account += 1
                continue

            comp_code = account.compCode

            bal = AccountBalance(
                compCode=comp_code,
                accountID=account,
                fundCode=fund_code_val,
                unitBalance=self.safe_decimal(unit_balance_val),
                amount=self.safe_decimal(amount_val),
                averageCost=self.safe_decimal(average_cost_val),
                NAV=self.safe_decimal(nav_val),
                NAVdate=self.safe_date(nav_date_val)
            )
            balances_to_create.append(bal)

        if skipped_missing_account > 0:
            logger.warning(f"Skipped {skipped_missing_account} UnitholderBalance records because InvestorAccount does not exist in DB.")

        if balances_to_create:
            target_comp_codes = [b.compCode for b in balances_to_create]
            target_account_ids = [b.accountID for b in balances_to_create]
            with transaction.atomic():
                # 2. ลบเฉพาะรายการที่ตรงกับ compCode และ accountID ในชุดข้อมูลใหม่
                AccountBalance.objects.filter(
                    compCode__in=target_comp_codes,
                    accountID__in=target_account_ids
                ).delete()

                # 2. บันทึกข้อมูลชุดใหม่เข้าไปแบบ Bulk
                AccountBalance.objects.bulk_create(balances_to_create, ignore_conflicts=True)

            logger.info(f"Successfully processed {len(balances_to_create)} Unitholder Balances.")
        else:
            logger.info("Parsing finished, but 0 brand new balances were created.")


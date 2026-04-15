import json
import io
import zipfile
from django.test import TestCase
from .models import CustomerIndividual
from .services import STTFundConnextService
from invest.models import Investor, InvestorAccount

class CustomerIndividualETLTest(TestCase):
    def setUp(self):
        self.service = STTFundConnextService()
        self.sample_customer = {
            "cardNumber": "1234567890123",
            "enFirstName": "John",
            "enLastName": "Doe",
            "thFirstName": "จอห์น",
            "thLastName": "โด",
            "email": "john.doe@example.com",
            "suitabilityRiskLevel": 4,
            "identificationDocument": {"no": "123", "soi": "Test Soi"},
            "current": {"no": "456", "road": "Test Road"},
            "accounts": [
                {
                    "accountId": "ACC001", 
                    "accountStatus": "ACTIVE",
                    "icLicense": "IC123",
                    "approvedDateTime": "20260409195113"
                }
            ]
        }
        
        # Create a mock investor to test sync
        self.investor = Investor.objects.create(
            compCode="MPS",
            custCode="1234567890123",
            fullNameEn="John Doe",
            fullNameTh="จอห์น โด",
            email="john.doe@example.com"
        )

    def create_mock_zip(self, data):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('20260410_MPS_INDIVIDUAL.json', json.dumps(data))
        return buf.getvalue()

    def test_process_customer_individual_create(self):
        zip_content = self.create_mock_zip([self.sample_customer])
        
        self.service.process_customer_individual(zip_content)
        
        customer = CustomerIndividual.objects.get(card_number="1234567890123")
        self.assertEqual(customer.en_first_name, "John")
        self.assertEqual(customer.email, "john.doe@example.com")
        self.assertEqual(customer.suitability_risk_level, 4)
        
        # Verify InvestorAccount sync is NOT happening (commented out in services.py)
        self.assertFalse(InvestorAccount.objects.filter(accountID="ACC001").exists())

    def test_process_customer_individual_update(self):
        # Create initial
        CustomerIndividual.objects.create(
            card_number="1234567890123",
            en_first_name="Old Name"
        )
        
        zip_content = self.create_mock_zip([self.sample_customer])
        self.service.process_customer_individual(zip_content)
        
        customer = CustomerIndividual.objects.get(card_number="1234567890123")
        self.assertEqual(customer.en_first_name, "John") # Updated
        self.assertEqual(customer.suitability_risk_level, 4)

    def test_create_invest_user_action(self):
        from stt_fundconnext.admin import CustomerIndividualAdmin
        from django.contrib.admin.sites import AdminSite
        from django.test import RequestFactory
        from unittest.mock import patch

        # Ensure CustomerIndividual exists
        ci = CustomerIndividual.objects.create(
            card_number="9998887776661",
            en_first_name="Alice",
            en_last_name="Smith",
            th_first_name="อลิซ",
            th_last_name="สมิธ",
            email="alice@example.com",
            mobile_number="0881112222",
            suitability_risk_level=5,
            profile_status="ACTIVE",
            accounts=[
                {
                    "accountId": "ACC001", 
                    "accountStatus": "ACTIVE",
                    "icLicense": "IC123",
                    "approvedDateTime": "20260409195113"
                }
            ]
        )
        
        # Setup Admin
        site = AdminSite()
        admin = CustomerIndividualAdmin(CustomerIndividual, site)
        
        # Call action with mocked messages
        request = RequestFactory().get('/admin/')
        queryset = CustomerIndividual.objects.filter(card_number="9998887776661")
        
        with patch('django.contrib.messages.add_message') as mock_add_message:
            admin.create_invest_user_action(request, queryset)
        
        # Verify Investor
        investor = Investor.objects.get(card_number_encrypted="9998887776661")
        self.assertEqual(investor.custCode, "9998887776661")
        self.assertEqual(investor.fullNameEn, "Alice Smith")
        self.assertEqual(investor.fullNameTh, "อลิซ สมิธ")
        self.assertEqual(investor.email, "alice@example.com")
        self.assertEqual(investor.status, "Active")
        self.assertEqual(investor.projects, "mf")

        # Verify InvestorAccount sync via admin action
        acc = InvestorAccount.objects.get(accountID="ACC001")
        self.assertEqual(acc.custCode, investor)
        self.assertEqual(acc.status, "Active")
        self.assertEqual(acc.icLicense, "IC123")
        self.assertEqual(acc.openDate.strftime("%Y%m%d"), "20260409")

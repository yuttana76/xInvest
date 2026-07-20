from django.test import TestCase
from fundDecision.models import FundFactSheet

class TestFieldLimits(TestCase):
    def test_long_fields(self):
        """Verify that FundFactSheet fields can handle strings longer than 255 characters."""
        long_string = "A" * 1000
        
        try:
            factsheet = FundFactSheet.objects.create(
                fund_code="TEST_LONG",
                fund_name_th=long_string,
                fund_category="C" * 255, # max_length was 100, now 255
                benchmark=long_string
            )
            self.assertEqual(len(factsheet.fund_name_th), 1000)
            self.assertEqual(len(factsheet.benchmark), 1000)
            self.assertEqual(len(factsheet.fund_category), 255)
            
            # Refresh from DB to be sure
            factsheet.refresh_from_db()
            self.assertEqual(len(factsheet.fund_name_th), 1000)
            self.assertEqual(len(factsheet.benchmark), 1000)
            
        except Exception as e:
            self.fail(f"Saving long fields failed: {e}")

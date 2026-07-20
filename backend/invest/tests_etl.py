from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

class ETLAdminTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')
        self.client = Client()
        self.client.login(username='admin', password='password')

    @patch('invest.tasks.run_daily_fundconnext_etl_current_mf_balance.delay')
    def test_run_etl_current_balance_view_post(self, mock_task):
        url = '/admin/invest/accountbalance/run-etl-current-balance/'
        response = self.client.post(url, {'business_date': '20240415'})
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check if task was called with correct argument
        mock_task.assert_called_once_with('20240415')

    @patch('invest.tasks.run_daily_fundconnext_etl_trans.delay')
    def test_run_etl_trans_view_post(self, mock_task):
        url = '/admin/invest/mftransaction/run-etl-trans/'
        response = self.client.post(url, {'business_date': '20240416'})
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check if task was called with correct argument
        mock_task.assert_called_once_with('20240416')

    def test_run_etl_current_balance_view_get(self):
        url = '/admin/invest/accountbalance/run-etl-current-balance/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/invest/run_etl_form.html")
        self.assertContains(response, "Business Date:")

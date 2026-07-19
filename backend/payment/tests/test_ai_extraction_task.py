from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from payment.ai_schemas import InvoiceExtractionResult
from payment.models import SourceDocument
from payment.tasks import extract_invoice_task

User = get_user_model()


class ExtractInvoiceTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='uploader', password='secret')
        self.doc = SourceDocument.objects.create(
            doc_type='INVOICE',
            file=SimpleUploadedFile('invoice.pdf', b'%PDF-1.4 fake content', content_type='application/pdf'),
            uploaded_by=self.user,
        )

    @patch('payment.tasks.InvoiceAIService')
    def test_successful_extraction_sets_success_status(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service.extract_text_from_pdf.return_value = 'some invoice text'
        mock_service.extract_invoice_data.return_value = InvoiceExtractionResult(
            supplier_name='ACME', tax_id='1234567890123', invoice_no='INV-001',
            subtotal=1000, vat_amount=70, wht_amount=0, net_total=1070, confidence=0.95,
        )
        mock_service_cls.return_value = mock_service

        extract_invoice_task(self.doc.id)

        self.doc.refresh_from_db()
        self.assertEqual(self.doc.extraction_status, 'SUCCESS')
        self.assertEqual(self.doc.extracted_data['supplier_name'], 'ACME')

    @patch('payment.tasks.InvoiceAIService')
    def test_low_confidence_sets_needs_review_status(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service.extract_text_from_pdf.return_value = 'some invoice text'
        mock_service.extract_invoice_data.return_value = InvoiceExtractionResult(
            supplier_name='ACME', tax_id='1234567890123', invoice_no='INV-001',
            subtotal=1000, vat_amount=70, wht_amount=0, net_total=1070, confidence=0.4,
        )
        mock_service_cls.return_value = mock_service

        extract_invoice_task(self.doc.id)

        self.doc.refresh_from_db()
        self.assertEqual(self.doc.extraction_status, 'NEEDS_REVIEW')

    @patch('payment.tasks.InvoiceAIService')
    def test_none_result_sets_failed_status(self, mock_service_cls):
        mock_service = MagicMock()
        mock_service.extract_text_from_pdf.return_value = 'some invoice text'
        mock_service.extract_invoice_data.return_value = None
        mock_service_cls.return_value = mock_service

        extract_invoice_task(self.doc.id)

        self.doc.refresh_from_db()
        self.assertEqual(self.doc.extraction_status, 'FAILED')

    @patch('payment.tasks.InvoiceAIService')
    def test_exception_sets_failed_status_with_error_message(self, mock_service_cls):
        mock_service_cls.side_effect = RuntimeError('boom')

        extract_invoice_task(self.doc.id)

        self.doc.refresh_from_db()
        self.assertEqual(self.doc.extraction_status, 'FAILED')
        self.assertIn('boom', self.doc.ai_error_message)

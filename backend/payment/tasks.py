import logging
from celery import shared_task

from .models import SourceDocument
from .ai_service import InvoiceAIService

logger = logging.getLogger(__name__)


@shared_task
def extract_invoice_task(source_document_id):
    """
    Extract structured invoice/quotation data from an uploaded SourceDocument's PDF using AI.
    """
    try:
        doc = SourceDocument.objects.get(id=source_document_id)
    except SourceDocument.DoesNotExist:
        logger.error(f"SourceDocument {source_document_id} not found")
        return

    try:
        doc.extraction_status = 'PROCESSING'
        doc.save(update_fields=['extraction_status'])

        ai_service = InvoiceAIService()
        pdf_text = ai_service.extract_text_from_pdf(doc.file.path)

        logger.info(f"*(TASK) Extracting invoice data for SourceDocument {source_document_id}")
        result = ai_service.extract_invoice_data(pdf_text)

        if result:
            doc.extracted_data = result.model_dump()
            if result.confidence is not None and result.confidence < 0.7:
                doc.extraction_status = 'NEEDS_REVIEW'
            else:
                doc.extraction_status = 'SUCCESS'
            doc.ai_error_message = ""
            doc.save()
            logger.info(f"Successfully extracted invoice data for SourceDocument {source_document_id}")
        else:
            doc.extraction_status = 'FAILED'
            doc.ai_error_message = "AI extraction failed or returned no result."
            doc.save()
            logger.warning(f"Failed to extract invoice data for SourceDocument {source_document_id}")

    except Exception as e:
        logger.error(f"Error in extract_invoice_task for {source_document_id}: {e}")
        try:
            doc = SourceDocument.objects.get(id=source_document_id)
            doc.extraction_status = 'FAILED'
            doc.ai_error_message = str(e)
            doc.save()
        except Exception:
            pass

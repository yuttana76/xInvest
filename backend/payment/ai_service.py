import logging
from typing import Optional

from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .ai_schemas import InvoiceExtractionResult

logger = logging.getLogger(__name__)


class InvoiceAIService:
    def __init__(self):
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            logger.error("GEMINI_API_KEY not found in settings")
            self.llm = None
        else:
            logger.info("GEMINI_API_KEY found, searching for available models...")
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)

                priority_list = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-2.0-flash",
                    "gemini-pro",
                    "gemini-1.5-pro",
                ]

                available_models = [
                    m.name.replace("models/", "") for m in genai.list_models()
                    if "generateContent" in m.supported_generation_methods
                ]

                selected_model = None
                for model_candidate in priority_list:
                    if model_candidate in available_models:
                        selected_model = model_candidate
                        break

                if not selected_model and available_models:
                    selected_model = available_models[0]
                    logger.warning(f"No priority models found. Falling back to: {selected_model}")

                if selected_model:
                    logger.info(f"Selected model for invoice extraction: {selected_model}")
                    self.llm = ChatGoogleGenerativeAI(
                        model=selected_model,
                        google_api_key=api_key,
                        temperature=0,
                    )
                else:
                    logger.error("No available Gemini models found for this API key.")
                    self.llm = None
            except Exception as e:
                logger.error(f"Error during dynamic model discovery: {e}")
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0,
                )

        self.parser = PydanticOutputParser(pydantic_object=InvoiceExtractionResult)

        self.system_prompt = (
            "คุณคือผู้เชี่ยวชาญด้านการเงินและบัญชี มีหน้าที่สกัดข้อมูลจากใบแจ้งหนี้/ใบเสนอราคาของซัพพลายเออร์ "
            "กรุณาอ่านเอกสารและตอบกลับเป็นรูปแบบ JSON ตามโครงสร้างที่กำหนดเท่านั้น\n{format_instructions}"
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "Content from PDF:\n{pdf_text}")
        ]).partial(format_instructions=self.parser.get_format_instructions())

    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract text from PDF using pypdf."""
        try:
            logger.info(f"*InvoiceAIService.extract_text_from_pdf() PDF: {pdf_file_path}")
            from pypdf import PdfReader
            reader = PdfReader(pdf_file_path)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def extract_invoice_data(self, text: str) -> Optional[InvoiceExtractionResult]:
        """Analyzes extracted invoice/quotation text and returns the structured extraction result."""
        if not self.llm:
            logger.error("LLM not initialized. Check GEMINI_API_KEY.")
            return None

        if not text:
            logger.error("Empty text passed to extract_invoice_data")
            return None

        models_to_try = [self.llm.model]
        for m in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro", "gemini-2.0-flash"]:
            if m not in models_to_try:
                models_to_try.append(m)

        max_chars = 20000
        processed_text = text
        if len(processed_text) > max_chars:
            processed_text = processed_text[:max_chars] + "..."

        for current_model in models_to_try:
            try:
                if self.llm.model != current_model:
                    logger.info(f"Retrying invoice extraction with fallback model: {current_model}")
                    self.llm.model = current_model

                prompt_val = self.prompt.invoke({"pdf_text": processed_text})
                raw_response = self.llm.invoke(prompt_val)

                content_str = raw_response.content
                if isinstance(content_str, list):
                    content_str = " ".join(
                        part.get("text", "") if isinstance(part, dict) else str(part) for part in content_str
                    )

                if not content_str:
                    logger.warning(f"Empty content received from {current_model}")
                    continue

                try:
                    result = self.parser.parse(content_str)
                    logger.info(f"Invoice extraction successful with {current_model}")
                    return result
                except Exception as parse_err:
                    logger.error(f"Failed to parse response from {current_model}: {parse_err}")
                    # Fallback: try to extract JSON via regex
                    import re
                    import json
                    match = re.search(r'\{.*\}', content_str, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(0))
                            return InvoiceExtractionResult(**data)
                        except Exception as json_err:
                            logger.error(f"Regex JSON fallback failed: {json_err}")
                    continue

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    logger.warning(f"Quota exceeded (429) for model {current_model}. Trying next fallback...")
                    continue
                elif "404" in error_msg or "NOT_FOUND" in error_msg:
                    logger.warning(f"Model {current_model} not found (404). Trying next fallback...")
                    continue
                else:
                    logger.error(f"Unexpected error during invoice extraction with {current_model}: {e}")
                    continue

        logger.error("All AI models failed or quota exhausted for invoice extraction.")
        return None

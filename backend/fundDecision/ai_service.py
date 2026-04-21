from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class NewsAnalysisResult(BaseModel):
    related_sectors: List[str] = Field(description="List of investment sectors related to the news. Choices: Tech, Energy, Healthcare, Finance, Consumer, Industrials, Materials, Utilities, Real Estate, Telecommunications")
    ai_sentiment_score: float = Field(description="Sentiment score between -1.0 (very negative) and 1.0 (very positive)")
    ai_summary: str = Field(description="A concise summary (in Thai) of how this news impacts investment")
    ai_impact_level: str = Field(description="Impact level on the market. Choices: LOW, MED, HIGH")
    ai_model: str = Field(description="Model used for analysis")

class NewsAIService:
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
                
                # Priority list for models
                priority_list = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-2.0-flash",
                    "gemini-pro",
                    "gemini-1.5-pro",
                ]
                
                available_models = [m.name.replace("models/", "") for m in genai.list_models() 
                                   if "generateContent" in m.supported_generation_methods]
                
                selected_model = None
                for model_candidate in priority_list:
                    if model_candidate in available_models:
                        selected_model = model_candidate
                        break
                
                if not selected_model and available_models:
                    # Fallback to first available model if none of the priority ones are found
                    selected_model = available_models[0]
                    logger.warning(f"No priority models found. Falling back to: {selected_model}")
                
                if selected_model:
                    logger.info(f"Selected model for analysis: {selected_model}")
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
                # Fallback to a safe default if listing fails
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0,
                )
        
        self.parser = PydanticOutputParser(pydantic_object=NewsAnalysisResult)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert financial analyst. Analyze the provided news article and extract investment insights. "
                        "Return the results in the specified JSON format.\n{format_instructions}"),
            ("user", "Title: {title}\n\nContent: {content}")
        ]).partial(format_instructions=self.parser.get_format_instructions())

    def analyze_news(self, title: str, content: str) -> Optional[NewsAnalysisResult]:
        logger.info(f"Analyzing news: {title[:100]}...")
        if not self.llm:
            logger.error("LLM not initialized. Check GEMINI_API_KEY.")
            return None
            
        # List of models to try if the first one fails due to quota (429)
        # We start with the one already selected during __init__
        models_to_try = [self.llm.model]
        
        # Add other potential models if not already in the list
        for m in ["gemini-pro", "gemini-1.5-flash", "gemini-flash-latest"]:
            if m not in models_to_try:
                models_to_try.append(m)

        for current_model in models_to_try:
            try:
                # Update LLM if we are retrying with a different model
                if self.llm.model != current_model:
                    logger.info(f"Retrying analysis with fallback model: {current_model}")
                    self.llm.model = current_model

                # Token optimization: Truncate long content
                processed_content = content
                max_chars = 10000
                if processed_content and len(processed_content) > max_chars:
                    logger.info(f"Truncating content from {len(processed_content)} to {max_chars} characters.")
                    processed_content = processed_content[:max_chars] + "..."

                logger.info(f"Calling Gemini API ({current_model}) to analyze news: {title[:50]}...")
                
                # Step 1: Generate response from LLM
                prompt_val = self.prompt.invoke({"title": title, "content": processed_content})
                logger.info(f"Prompt: {prompt_val}")
                raw_response = self.llm.invoke(prompt_val)
                
                # Log raw response content
                content_str = raw_response.content
                if isinstance(content_str, list):
                    # Handle multi-part content
                    content_str = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content_str])
                
                # logger.info(f"Raw AI Response from {current_model}: {content_str[:200]}...")
                
                if not content_str:
                    logger.warning(f"Empty content received from {current_model}")
                    continue # Try next model
                    
                # Step 2: Parse response
                try:
                    result = self.parser.parse(content_str)
                    result.ai_model = current_model
                    if result:
                        logger.info(f"AI Analysis successful with {current_model}")
                        return result
                except Exception as parse_err:
                    logger.error(f"Failed to parse response from {current_model}: {parse_err}")
                    continue # Try next model
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    logger.warning(f"Quota exceeded (429) for model {current_model}. Trying next fallback...")
                    continue
                elif "404" in error_msg or "NOT_FOUND" in error_msg:
                    logger.warning(f"Model {current_model} not found (404). Trying next fallback...")
                    continue
                else:
                    logger.error(f"Unexpected error during AI news analysis with {current_model}: {e}")
                    # For critical errors, we might want to stop, but for now let's try next model
                    continue
                    
        logger.error("All AI analysis models failed or quota exhausted.")
        return None

class FactSheetAnalysisResult(BaseModel):
    fund_code: str = Field(description="รหัสย่อกองทุน")
    fund_name_th: str = Field(description="ชื่อเต็มกองทุนภาษาไทย")
    risk_level: int = Field(description="ระดับความเสี่ยง (เลข 1-8)")
    fund_category: str = Field(description="ประเภทกลุ่มกองทุน ")
    investment_strategy: str = Field(description="กลยุทธ์การลงทุน (Active หรือ Passive)")
    top_5_holdings: List[dict] = Field(description="รายชื่อสินทรัพย์ 5 อันดับแรก (name, ticker, ratio)")
    sector_allocation: List[dict] = Field(description="สัดส่วนกลุ่มอุตสาหกรรม 5 อันดับแรก (sector_name, ratio)")
    currency_hedging: str = Field(description="นโยบายการป้องกันความเสี่ยงค่าเงิน (None/Partial/Fully/Discretionary)")
    benchmark: str = Field(description="ดัชนีชี้วัดที่ใช้เปรียบเทียบ")
    as_of_date: str = Field(description="วันที่ของข้อมูลพอร์ตล่าสุด (YYYY-MM-DD)")

class FactSheetAIService:
    def __init__(self):
        # Reuse existing LLM setup logic from NewsAIService
        news_service = NewsAIService()
        self.llm = news_service.llm
        self.parser = PydanticOutputParser(pydantic_object=FactSheetAnalysisResult)
        
        self.system_prompt = (
            "คุณคือนักวิเคราะห์ข้อมูลการเงินที่มีหน้าที่สกัดข้อมูลจาก PDF Fund Fact Sheet ของกองทุนไทย "
            "กรุณาอ่านเอกสารที่แนบมาและตอบกลับเป็นรูปแบบ JSON บริสุทธิ์ (Pure JSON) เท่านั้น "
            "ห้ามมีข้อความเกริ่นนำหรือคำอธิบายเพิ่มเติม ข้อมูลต้องแม่นยำตามที่ปรากฏในเอกสาร"
        )
        
        self.user_prompt_template = (
            "วิเคราะห์ไฟล์ PDF นี้และสกัดข้อมูลเข้าสู่โครงสร้าง JSON ดังนี้:\n\n"
            "1. fund_code: รหัสย่อกองทุน\n"
            "2. fund_name_th: ชื่อเต็มกองทุนภาษาไทย\n"
            "3. risk_level: ระดับความเสี่ยง (เลข 1-8)\n"
            "4. fund_category: ประเภทกลุ่มกองทุน\n"
            "5. investment_strategy: กลยุทธ์การลงทุน (ตอบเฉพาะ \"Active\" หรือ \"Passive\")\n"
            "6. top_5_holdings: รายชื่อสินทรัพย์ 5 อันดับแรก (ระบุ name, ticker ถ้ามี, และ ratio เป็นตัวเลข %)\n"
            "7. sector_allocation: สัดส่วนกลุ่มอุตสาหกรรม 5 อันดับแรก (ระบุ sector_name และ ratio %)\n"
            "8. currency_hedging: นโยบายการป้องกันความเสี่ยงค่าเงิน (None/Partial/Fully/Discretionary)\n"
            "9. benchmark: ดัชนีชี้วัดที่ใช้เปรียบเทียบ\n"
            "10. as_of_date: วันที่ของข้อมูลพอร์ตล่าสุดในเอกสาร (รูปแบบ YYYY-MM-DD)\n\n"
            "{format_instructions}\n\n"
            "Content from PDF:\n{pdf_text}"
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", self.user_prompt_template)
        ]).partial(format_instructions=self.parser.get_format_instructions())

    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract text from PDF using pypdf."""
        try:
            logger.info(f"*AI extract_text_from_pdf() PDF: {pdf_file_path}")
            from pypdf import PdfReader
            reader = PdfReader(pdf_file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def analyze_factsheet(self, pdf_file_path: str) -> Optional[FactSheetAnalysisResult]:
        """Analyzes a Fund Fact Sheet PDF and returns the extracted data."""
        logger.info(f"*AI analyze_factsheet() PDF: {pdf_file_path}")
        if not self.llm:
            logger.error("LLM not initialized")
            return None
            
        pdf_text = self.extract_text_from_pdf(pdf_file_path)
        if not pdf_text:
            logger.error("Failed to extract text from PDF")
            return None
            
        # List of models to try if the first one fails
        models_to_try = [self.llm.model]
        for m in ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro", "gemini-2.0-flash"]:
            if m not in models_to_try:
                models_to_try.append(m)

        for current_model in models_to_try:
            try:
                # Update LLM if retrying
                if self.llm.model != current_model:
                    logger.info(f"Retrying factsheet analysis with fallback model: {current_model}")
                    self.llm.model = current_model

                # Token optimization
                max_chars = 30000 
                processed_text = pdf_text
                if len(processed_text) > max_chars:
                    processed_text = processed_text[:max_chars] + "..."
                    
                prompt_val = self.prompt.invoke({"pdf_text": processed_text})
                raw_response = self.llm.invoke(prompt_val)
                
                content_str = raw_response.content
                if isinstance(content_str, list):
                    content_str = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content_str])
                
                logger.info(f"** Raw FactSheet AI Response from {current_model}: {content_str[:200]}...")
                
                return self.parser.parse(content_str)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    logger.warning(f"Quota exceeded (429) for model {current_model} during factsheet analysis. Trying next fallback...")
                    continue
                else:
                    logger.error(f"Unexpected error during FactSheet AI analysis with {current_model}: {e}")
                    continue
                    
        logger.error("All AI analysis models failed or quota exhausted for factsheet analysis.")
        return None

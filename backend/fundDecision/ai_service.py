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
                raw_response = self.llm.invoke(prompt_val)
                
                # Log raw response content
                content_str = raw_response.content
                if isinstance(content_str, list):
                    # Handle multi-part content
                    content_str = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content_str])
                
                logger.info(f"Raw AI Response from {current_model}: {content_str[:200]}...")
                
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

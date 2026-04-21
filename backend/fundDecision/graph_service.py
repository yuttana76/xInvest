from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from django.conf import settings
from .ai_service import NewsAnalysisResult, NewsAIService, FactSheetAnalysisResult
import logging
import json

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    title: str
    content: str
    analysis: Optional[NewsAnalysisResult]
    iterations: int
    error: Optional[str]
    matched_fund_codes: List[str]
    fund_insights: List[dict]

class NewsGraphService:
    def __init__(self):
        # We can reuse the LLM discovery logic from NewsAIService or just instantiate here
        ai_service = NewsAIService()
        self.llm = ai_service.llm
        if not self.llm:
            logger.error("LLM not initialized in NewsGraphService")
            
        # Discover available models dynamically for fallback
        discovered_models = []
        try:
            import google.generativeai as genai
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                discovered_models = [m.name.replace("models/", "") for m in models 
                                    if "generateContent" in m.supported_generation_methods]
                logger.info(f"NewsGraphService dynamically discovered models: {discovered_models}")
        except Exception as e:
            logger.warning(f"Failed to discover models in NewsGraphService: {e}")

        # Define priority order for fallback
        priority = [
            "gemini-1.5-flash", 
            "gemini-2.0-flash", 
            "gemini-1.5-flash-latest", 
            "gemini-1.5-pro", 
            "gemini-pro"
        ]
        
        if discovered_models:
            self.retry_models = [m for m in priority if m in discovered_models]
            for m in discovered_models:
                if m not in self.retry_models:
                    self.retry_models.append(m)
        else:
            self.retry_models = priority
            
        logger.info(f"NewsGraphService final retry_models sequence: {self.retry_models}")

        # Build the graph
        workflow = StateGraph(GraphState)
        
        workflow.add_node("analyzer", self.analyzer_node)
        workflow.add_node("refiner", self.refiner_node)
        workflow.add_node("fund_matcher", self.fund_matcher_node)
        workflow.add_node("insight_generator", self.insight_generator_node)
        
        workflow.set_entry_point("analyzer")
        workflow.add_edge("analyzer", "refiner")
        workflow.add_edge("refiner", "fund_matcher")
        workflow.add_edge("fund_matcher", "insight_generator")
        workflow.add_edge("insight_generator", END)
        
        self.app = workflow.compile()

    def analyzer_node(self, state: GraphState) -> GraphState:
        """
        Initial analysis node. Uses Gemini to extract investment insights, 
        sentiment scores, and summaries from the news article.
        """
        logger.info(f"Graph Node: analyzer for {state['title'][:50]}")
        try:
            # Use the same prompt logic as NewsAIService but via direct LLM call for more flexibility in the graph
            ai_service = NewsAIService()
            result = ai_service.analyze_news(state['title'], state['content'])
            return {**state, "analysis": result, "iterations": state.get("iterations", 0) + 1}
        except Exception as e:
            logger.error(f"Error in analyzer node: {e}")
            return {**state, "error": str(e)}

    def refiner_node(self, state: GraphState) -> GraphState:
        """
        Refinement node. Validates the analysis result, polishes the Thai summary,
        and adds structural metadata like the [LangGraph] prefix.
        """
        logger.info(f"Graph Node: refiner for {state['title'][:50]}")
        if state.get("error") or not state.get("analysis"):
            # Ensure required list fields are present even on error
            return {**state, "matched_fund_codes": state.get("matched_fund_codes", []), "fund_insights": state.get("fund_insights", [])}
            
        analysis = state["analysis"]
        # Add "[LangGraph]" prefix to the summary to distinguish it
        if analysis and analysis.ai_summary and not analysis.ai_summary.startswith("[LangGraph]"):
            analysis.ai_summary = f"[LangGraph] {analysis.ai_summary}"
            
        return {**state, "analysis": analysis, "matched_fund_codes": [], "fund_insights": []}

    def fund_matcher_node(self, state: GraphState) -> GraphState:
        """
        Matches news sectors and holdings with available FundFactSheets.
        """
        logger.info(f"Graph Node: fund_matcher for {state['title'][:50]}")
        if not state.get("analysis"):
            return state
            
        from .models import FundFactSheet
        from django.db.models import Q
        related_sectors = state["analysis"].related_sectors
        content = state["content"].lower()
        title = state["title"].lower()
        full_text = f"{title} {content}"
        
        matched_codes = set()
        
        # 1. Match by Sector
        logger.info(f"**Graph Node: fund_matcher for {state['title'][:50]} related_sectors: {related_sectors}")
        if related_sectors:
            for sector in related_sectors:
                # Search in fund_category or sector_allocation (JSON string representation for simple search)
                funds = FundFactSheet.objects.filter(
                    Q(fund_category__icontains=sector) |
                    Q(sector_allocation__icontains=sector)
                )
                logger.info(f"**Graph Node: fund_matcher funds: {funds}")
                for fund in funds:
                    matched_codes.add(fund.fund_code)
        
        # 2. Match by Holdings (Keywords)
        all_funds = FundFactSheet.objects.exclude(holdings_data__isnull=True)
        for fund in all_funds:
            if fund.holdings_data:
                for holding in fund.holdings_data:
                    name = str(holding.get('name', '')).lower()
                    ticker = str(holding.get('ticker', '')).lower()
                    if (name and len(name) > 2 and name in full_text) or \
                       (ticker and len(ticker) > 1 and ticker in full_text):
                        matched_codes.add(fund.fund_code)
                        break
        
        logger.info(f"Matched {len(matched_codes)} funds: {list(matched_codes)}")
        return {**state, "matched_fund_codes": list(matched_codes)}

    def insight_generator_node(self, state: GraphState) -> GraphState:
        """
        Generates specific insights for each matched fund using LLM.
        """
        logger.info(f"Graph Node: insight_generator for {len(state.get('matched_fund_codes', []))} funds")
        matched_codes = state.get("matched_fund_codes", [])
        if not matched_codes or not self.llm:
            return {**state, "fund_insights": []}
            
        from .models import FundFactSheet
        insights = []
        
        # Limit to top 5 funds to avoid excessive tokens/time
        for code in matched_codes[:5]:
            try:
                fund = FundFactSheet.objects.get(fund_code=code)
                insight_data = self._generate_single_fund_insight(state, fund)
                if insight_data:
                    insight_data['fundCode'] = code
                    insights.append(insight_data)
            except Exception as e:
                logger.error(f"Error generating insight for {code}: {e}")
                
        return {**state, "fund_insights": insights}

    def _generate_single_fund_insight(self, state: GraphState, fund) -> Optional[dict]:
        """
        Calls LLM to generate a specific impact analysis for a fund.
        """
        try:
            analysis = state["analysis"]
            
            system_prompt = (
                "You are an expert investment advisor. analyze how the provided news impacts a specific mutual fund. "
                "Provide a concise analysis in Thai, a sentiment score (-1.0 to 1.0), and a confidence score (0.0 to 1.0). "
                "Format your response as a JSON object: {\"content\": \"...\", \"sentiment_score\": 0.0, \"confidence_score\": 0.0}"
            )
            
            fund_context = (
                f"Fund: {fund.fund_code} - {fund.fund_name_th}\n"
                f"Category: {fund.fund_category}\n"
                f"Strategy: {fund.investment_strategy}\n"
                f"Holdings: {json.dumps(fund.holdings_data, ensure_ascii=False)}\n"
                f"Sector Allocation: {json.dumps(fund.sector_allocation, ensure_ascii=False)}"
            )
            
            news_context = (
                f"News Title: {state['title']}\n"
                f"News Summary: {analysis.ai_summary}\n"
                f"Related Sectors: {', '.join(analysis.related_sectors)}"
            )
            
            user_prompt = f"Analyze the impact of this news on this fund:\n\n[FUND CONTEXT]\n{fund_context}\n\n[NEWS CONTEXT]\n{news_context}"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Implementation of model fallback and retry for 429 errors
            models_to_try = [self.llm.model]
            for m in self.retry_models:
                if m not in models_to_try:
                    models_to_try.append(m)
            
            for current_model in models_to_try:
                try:
                    if self.llm.model != current_model:
                        logger.info(f"Retrying single fund insight with fallback model: {current_model}")
                        self.llm.model = current_model
                        
                    response = self.llm.invoke(messages)
                    content_str = response.content
                    
                    # Simple JSON extraction from response
                    import re
                    json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        data['insight_type'] = 'NEWS_IMPACT'
                        data['model_version'] = f"LangGraph-{current_model}"
                        return data
                    else:
                        logger.warning(f"No JSON found in response from {current_model}")
                        continue
                        
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        import time
                        logger.warning(f"Quota exceeded (429) for model {current_model}. Waiting 3s and trying next fallback...")
                        time.sleep(3)
                        continue
                    else:
                        logger.error(f"Error calling model {current_model} for single fund insight: {e}")
                        continue
                
        except Exception as e:
            logger.error(f"Failed to generate single fund insight: {e}")
            
        return None

    def analyze_news(self, title: str, content: str) -> dict:
        """
        Modified to return the full state or at least the insights.
        """
        if not self.llm:
            return {}
            
        initial_state = {
            "title": title,
            "content": content,
            "analysis": None,
            "iterations": 0,
            "error": None,
            "matched_fund_codes": [],
            "fund_insights": []
        }
        
        try:
            result_state = self.app.invoke(initial_state)
            return result_state
        except Exception as e:
            logger.error(f"Error during graph execution: {e}")
            return initial_state

class FactSheetGraphState(TypedDict):
    fund_code: str
    pdf_path: str
    pdf_text: Optional[str]
    analysis: Optional[FactSheetAnalysisResult]
    iterations: int
    current_model: str
    models_to_try: List[str]
    error: Optional[str]

class FactSheetGraphService:
    def __init__(self):
        from .ai_service import FactSheetAIService, NewsAIService
        self.ai_service = FactSheetAIService()
        
        # Discover available models dynamically to avoid 404s
        discovered_models = []
        try:
            import google.generativeai as genai
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                discovered_models = [m.name.replace("models/", "") for m in models 
                                    if "generateContent" in m.supported_generation_methods]
                logger.info(f"FactSheetGraphService dynamically discovered models: {discovered_models}")
        except Exception as e:
            logger.warning(f"Failed to discover models in FactSheetGraphService: {e}")
            
        # Define priority order
        # We use a broad list of potential names to handle different API versions/regions
        priority = [
            "gemini-2.0-flash", 
            "gemini-1.5-flash", 
            "gemini-1.5-flash-latest", 
            "gemini-1.5-pro", 
            "gemini-pro"
        ]
        
        # If discovery worked, use only confirmed models in priority order
        if discovered_models:
            self.retry_models = [m for m in priority if m in discovered_models]
            # Add remaining discovered models at the end
            for m in discovered_models:
                if m not in self.retry_models:
                    self.retry_models.append(m)
        else:
            # If discovery failed, use the hardcoded priority as a safety net
            self.retry_models = priority
            
        logger.info(f"FactSheetGraphService final retry_models sequence: {self.retry_models}")
        
        # Build the graph
        workflow = StateGraph(FactSheetGraphState)
        
        workflow.add_node("pdf_extractor", self.pdf_extractor_node)
        workflow.add_node("ai_extractor", self.ai_extractor_node)
        workflow.add_node("validator", self.validator_node)
        
        workflow.set_entry_point("pdf_extractor")
        workflow.add_edge("pdf_extractor", "ai_extractor")
        workflow.add_edge("ai_extractor", "validator")
        
        workflow.add_conditional_edges(
            "validator",
            self.should_continue,
            {
                "retry": "ai_extractor",
                "end": END
            }
        )
        
        self.app = workflow.compile()

    def pdf_extractor_node(self, state: FactSheetGraphState) -> FactSheetGraphState:
        """Node to extract text from PDF."""
        logger.info(f"*GRAPH pdf_extractor_node for {state['pdf_path']}")
        text = self.ai_service.extract_text_from_pdf(state['pdf_path'])

        if not text:
            return {**state, "error": "Failed to extract text from PDF"}
        return {**state, "pdf_text": text}

    def ai_extractor_node(self, state: FactSheetGraphState) -> FactSheetGraphState:
        """Node to perform AI extraction using current model."""
        model = state.get("current_model", "gemini-2.0-flash")
        logger.info(f"*GRAPH ai_extractor_node using model {model}")
        
        if not state.get("pdf_text"):
            return {**state, "error": "No PDF text available for AI extraction"}
            
        try:
            # Temporarily set the model for this call
            self.ai_service.llm.model = model
            
            # Use the core logic from ai_service but we could also put prompt logic here
            # For consistency, we use the service's refined prompts
            max_chars = 30000
            pdf_text = state['pdf_text']
            if len(pdf_text) > max_chars:
                pdf_text = pdf_text[:max_chars] + "..."
                
            prompt_val = self.ai_service.prompt.invoke({"pdf_text": pdf_text})
            
            # Save prompt_val to model
            from .models import FundFactSheet
            try:
                factsheet = FundFactSheet.objects.get(fund_code=state['fund_code'])
                # Convert ChatPromptValue to serializable messages
                serializable_messages = []
                for m in prompt_val.to_messages():
                    serializable_messages.append({
                        "type": getattr(m, "type", "unknown"),
                        "content": str(m.content)
                    })
                factsheet.prompt_val = serializable_messages
                factsheet.save()
            except Exception as e:
                logger.warning(f"Failed to save prompt_val to FundFactSheet: {e}")


            logger.info(f"*GRAPH ai_extractor_node model: {self.ai_service.llm.model}")
            raw_response = self.ai_service.llm.invoke(prompt_val)
            
            content_str = raw_response.content
            if isinstance(content_str, list):
                content_str = " ".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content_str])
            
            result = self.ai_service.parser.parse(content_str)
            return {**state, "analysis": result, "iterations": state.get("iterations", 0) + 1, "error": None}
        except Exception as e:
            logger.warning(f"Error in ai_extractor with {model}: {e}")
            return {**state, "error": str(e), "iterations": state.get("iterations", 0) + 1}

    def validator_node(self, state: FactSheetGraphState) -> FactSheetGraphState:
        """Node to validate the result and decide if we need to switch models."""
        logger.info("*GRAPH validator_node")
        if not state.get("analysis") or state.get("error"):
            # If we have more models to try, move to next
            available_models = state.get("models_to_try", [])
            current_model = state.get("current_model")
            
            if current_model in available_models:
                idx = available_models.index(current_model)
                if idx + 1 < len(available_models):
                    next_model = available_models[idx + 1]
                    
                    # If it was a rate limit error, wait a few seconds before retrying
                    err_str = str(state.get("error", "")).upper()
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        import time
                        logger.info(f"Rate limit hit. Waiting 5s before retrying with {next_model}...")
                        time.sleep(5)
                        
                    logger.info(f"Validator decided to retry with next model: {next_model}")
                    return {**state, "current_model": next_model, "error": None}
            
            logger.error("No more models to try or critical error.")
            return {**state, "error": state.get("error") or "Max retries reached"}
            
        return state

    def should_continue(self, state: FactSheetGraphState) -> str:
        """Conditional edge logic."""
        # 1. ถ้ามี error และจำนวนครั้งที่ลอง (iterations) ยังไม่ครบจำนวน Model ที่มี
        if state.get("error") and state.get("iterations", 0) < len(state.get("models_to_try", [])):
            if "RESOURCE_EXHAUSTED" in str(state.get("error")) or "429" in str(state.get("error")):
                return "retry"
        
        # 2. หรือถ้าไม่มีผลลัพธ์ (analysis) และยังลองไม่ครบ
        if not state.get("analysis") and state.get("iterations", 0) < len(state.get("models_to_try", [])):
            return "retry"

        # 3. ถ้ามีผลลัพธ์แล้ว (analysis) และยังลองไม่ครบ
        return "end"

    def analyze_factsheet(self, fund_code: str, pdf_path: str) -> Optional[FactSheetAnalysisResult]:
        models = self.retry_models
        initial_state = {
            "fund_code": fund_code,
            "pdf_path": pdf_path,
            "pdf_text": None,
            "analysis": None,
            "iterations": 0,
            "current_model": models[0] if models else "gemini-2.0-flash",
            "models_to_try": models,
            "error": None
        }
        
        try:
            result_state = self.app.invoke(initial_state)
            return result_state.get("analysis")
        except Exception as e:
            logger.error(f"Error during factsheet graph execution: {e}")
            return None

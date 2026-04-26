from celery import shared_task
from .news_service import NewsFetcher
from .models import NewsArticle, AIInsight
from .ai_service import NewsAIService, SmartFundAIService
from .graph_service import NewsGraphService
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_daily_news():
    """
    Celery task to fetch news from NewsAPI and RSS feeds.
    Scheduled for 7:00 AM daily.
    """
    logger.info("Starting scheduled news fetch...")
    fetcher = NewsFetcher()
    count = fetcher.fetch_all()
    logger.info(f"Finished scheduled news fetch. Saved {count} new articles.")
    
    # Trigger AI analysis for articles without analysis
    # pending_articles = NewsArticle.objects.filter(ai_sentiment_score__isnull=True)[:50]
    # for article in pending_articles:
    #     analyze_news_article_task.delay(article.id)
        
    return count

@shared_task
def analyze_news_article_task(article_id):
    """
    Analyzes a news article using AI.
    """
    try:
        article = NewsArticle.objects.get(id=article_id)
        ai_service = NewsAIService()

        logger.info(f"*(TASK)Analyzing article {article_id}: {article.title}")
        
        # If content/description is null or very short, try to fetch from URL
        content_to_analyze = article.content or article.description or ""
        if len(content_to_analyze.strip()) < 100 and article.url:
            logger.info(f"*(TASK)Content too short ({len(content_to_analyze)} chars). Fetching from URL: {article.url}")
            fetcher = NewsFetcher()
            fetched_content = fetcher.fetch_content_from_url(article.url)
            if fetched_content:
                logger.info(f"*(TASK)Successfully fetched content from URL ({len(fetched_content)} chars)")
                article.content = fetched_content
                article.save()
                content_to_analyze = fetched_content
        
        result = ai_service.analyze_news(article.title, content_to_analyze)
        
        logger.info(f"*(TASK)AI Analysis result for article {article_id}: {result}")
        if result:
            article.ai_sentiment_score = result.ai_sentiment_score
            article.ai_summary = result.ai_summary
            article.ai_impact_level = result.ai_impact_level
            article.related_sectors = result.related_sectors
            article.ai_model = result.ai_model
            article.save()
            logger.info(f"Successfully analyzed article {article_id}")
        else:
            logger.warning(f"Failed to analyze article {article_id}")
    except NewsArticle.DoesNotExist:
        logger.error(f"Article {article_id} not found")
    except Exception as e:
        logger.error(f"Error in analyze_news_article_task for {article_id}: {e}")

@shared_task
def analyze_news_langgraph_task(article_id):
    """
    Analyzes a news article using LangGraph.
    """
    try:
        article = NewsArticle.objects.get(id=article_id)
        graph_service = NewsGraphService()

        # Re-use content fetching logic or similar if needed
        content_to_analyze = article.content or article.description or ""
        if len(content_to_analyze.strip()) < 100 and article.url:
            fetcher = NewsFetcher()
            fetched_content = fetcher.fetch_content_from_url(article.url)
            if fetched_content:
                article.content = fetched_content
                article.save()
                content_to_analyze = fetched_content

        logger.info(f"*(GRAPH TASK)Analyzing article {article_id} with LangGraph: {article.title}")
        state = graph_service.analyze_news(article.title, content_to_analyze)
        
        analysis = state.get("analysis")
        if analysis:
            article.ai_sentiment_score = analysis.ai_sentiment_score
            article.ai_summary = analysis.ai_summary
            article.ai_impact_level = analysis.ai_impact_level
            article.related_sectors = analysis.related_sectors
            article.ai_model = f"LangGraph-{analysis.ai_model}"
            article.save()
            
            # Save Insights
            insights = state.get("fund_insights", [])
            for ins in insights:
                article_id ='news_'+ str(article.id)
                ins['content'] = ins['content'] + f"\n** News **\nSource: {article.source}\nTitle: {article.title}\nURL: {article.url}\nDate: {article.published_at}"
                AIInsight.objects.create(
                    fundCode=ins['fundCode'],
                    insight_type=article_id,
                    content=ins['content'],
                    sentiment_score=ins['sentiment_score'],
                    confidence_score=ins['confidence_score'],
                    model_version=ins['model_version']
                )
            
            logger.info(f"Successfully analyzed article {article_id} with LangGraph. Saved {len(insights)} insights.")
        else:
            logger.warning(f"Failed to analyze article {article_id} with LangGraph or no analysis result found.")
    except NewsArticle.DoesNotExist:
        logger.error(f"Article {article_id} not found")
    except Exception as e:
        logger.error(f"Error in analyze_news_langgraph_task for {article_id}: {e}")

@shared_task
def analyze_factsheet_task(factsheet_id):
    """
    Analyzes a Fund Fact Sheet using LangGraph.
    """
    from .models import FundFactSheet
    from .graph_service import FactSheetGraphService
    
    try:
        factsheet = FundFactSheet.objects.get(id=factsheet_id)
        factsheet.ai_analysis_status = 'PROCESSING'
        factsheet.save()
        
        pdf_path = None
        if factsheet.factsheet_file:
            pdf_path = factsheet.factsheet_file.path
        elif factsheet.factsheet_url:
            # Download PDF from URL
            import requests
            import os
            from django.core.files.temp import NamedTemporaryFile
            from django.core.files import File
            
            logger.info(f"Downloading PDF from URL: {factsheet.factsheet_url}")
            response = requests.get(factsheet.factsheet_url)
            if response.status_code == 200:
                temp_file = NamedTemporaryFile(delete=True)
                temp_file.write(response.content)
                temp_file.flush()
                
                # Save to model to keep a local copy
                filename = os.path.basename(factsheet.factsheet_url.split('?')[0]) or f"factsheet_{factsheet_id}.pdf"
                factsheet.factsheet_file.save(filename, File(temp_file))
                pdf_path = factsheet.factsheet_file.path
            else:
                raise ValueError(f"Failed to download PDF from URL. Status code: {response.status_code}")
        
        if not pdf_path:
            raise ValueError("No PDF file or valid URL provided.")
            
        graph_service = FactSheetGraphService()
        logger.info(f"*(FACTSHEET TASK)Analyzing factsheet {factsheet_id}: {factsheet.fund_code}")
        
        result = graph_service.analyze_factsheet(factsheet.fund_code, factsheet.factsheet_file.path)
        
        if result:
            factsheet.fund_name_th = result.fund_name_th or factsheet.fund_name_th
            factsheet.risk_level = result.risk_level
            factsheet.fund_category = result.fund_category
            factsheet.investment_strategy = result.investment_strategy
            factsheet.holdings_data = result.top_5_holdings
            factsheet.sector_allocation = result.sector_allocation
            factsheet.currency_hedging = result.currency_hedging
            factsheet.benchmark = result.benchmark
            factsheet.as_of_date = result.as_of_date
            
            # Simple logic for is_hedged
            if result.currency_hedging and result.currency_hedging.lower() != 'none':
                factsheet.is_hedged = True
            
            factsheet.ai_analysis_status = 'SUCCESS'
            factsheet.ai_error_message = ""
            factsheet.save()
            
            # Trigger Vector Ingestion for RAG
            ingest_factsheet_to_vector_db.delay(factsheet.fund_code)
            
            logger.info(f"Successfully analyzed factsheet {factsheet_id} and queued vector ingestion.")
        else:
            factsheet.ai_analysis_status = 'FAILED'
            factsheet.ai_error_message = "AI extraction failed or returned no result."
            factsheet.save()
            logger.warning(f"Failed to analyze factsheet {factsheet_id}")
            
    except FundFactSheet.DoesNotExist:
        logger.error(f"Factsheet {factsheet_id} not found")
    except Exception as e:
        logger.error(f"Error in analyze_factsheet_task for {factsheet_id}: {e}")
        try:
            factsheet = FundFactSheet.objects.get(id=factsheet_id)
            factsheet.ai_analysis_status = 'FAILED'
            factsheet.ai_error_message = str(e)
            factsheet.save()
        except:
            pass

# @shared_task(bind=True, max_retries=2, default_retry_delay=120)
# def ingest_factsheet_to_vector_db(self, fund_code):
#     """Task to index a fund's PDF into the vector database for RAG."""
#     from .models import FundFactSheet
#     try:
#         factsheet = FundFactSheet.objects.get(fund_code=fund_code)
#         if not factsheet.factsheet_file:
#             logger.warning(f"No PDF file for fund {fund_code}")
#             return
#             
#         smart_ai = SmartFundAIService()
#         smart_ai.ingest_pdf(fund_code, factsheet.factsheet_file.path)
#         logger.info(f"Vector ingestion complete for {fund_code}")
#     except RuntimeError as e:
#         logger.error(f"Vector ingestion FAILED for {fund_code}: {e}")
#         # Retry the task after 2 minutes (rate limit cooldown)
#         raise self.retry(exc=e)
#     except Exception as e:
#         logger.error(f"Error in ingest_factsheet_to_vector_db for {fund_code}: {e}")

@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def ingest_factsheet_to_vector_db(self, fund_code):
    """Task to index a fund's database fields into the vector database for RAG (replacing PDF extraction)."""
    try:
        smart_ai = SmartFundAIService()
        smart_ai.ingest_factsheet_data(fund_code)
        logger.info(f"Vector ingestion from fields complete for {fund_code}")
    except RuntimeError as e:
        logger.error(f"Vector ingestion FAILED for {fund_code}: {e}")
        # Retry the task after 2 minutes
        raise self.retry(exc=e)
    except Exception as e:
        logger.error(f"Error in ingest_factsheet_to_vector_db for {fund_code}: {e}")

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def summarize_fund_impact_task(self, fund_code, insight_ids):
    """
    Task to summarize the impact of selected AIInsight records for a specific fund.
    """
    from .models import AIInsight, FundAnalysis
    from .ai_service import FundImpactAIService
    
    try:
        insights = AIInsight.objects.filter(id__in=insight_ids)
        if not insights.exists():
            logger.warning(f"No insights found for IDs {insight_ids}")
            return
            
        logger.info(f"Summarizing {insights.count()} insights for fund {fund_code}")
        
        # Combine insight context
        combined_content = ""
        for idx, insight in enumerate(insights, 1):
            combined_content += f"[{idx}] ประเภท: {insight.insight_type}\nข้อความ: {insight.content}\nคะแนนเดิม: {insight.sentiment_score}\n---\n"
            
        ai_service = FundImpactAIService()
        
        # If LangChain fails inside the service, it returns None.
        result = ai_service.summarize_fund_impact(fund_code, combined_content)
        
        if result:
            # Create a new FundAnalysis record
            new_analysis = FundAnalysis.objects.create(
                fundCode=fund_code,
                sentiment_score=result.sentiment_score,
                sentiment_summary=result.sentiment_summary,
                sentiment_impact_level=result.sentiment_impact_level,
                createBy="System-AI_Summary",
                status="ACTIVE"
            )
            logger.info(f"Successfully created FundAnalysis ID {new_analysis.id} for fund {fund_code}")
        else:
            logger.warning(f"Failed to generate summary for fund {fund_code}. Service returned None. Proceeding to retry.")
            raise Exception("AI Service returned None. Possibly due to rate limits or API errors.")
            
    except Exception as e:
        logger.warning(f"Retrying summarize_fund_impact_task for fund {fund_code} due to error: {e}")
        # Automatically retry the task if there's an exception
        raise self.retry(exc=e)

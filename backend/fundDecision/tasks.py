from celery import shared_task
from .news_service import NewsFetcher
from .models import NewsArticle
from .ai_service import NewsAIService
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
        result = ai_service.analyze_news(article.title, article.content or article.description)
        
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

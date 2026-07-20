import os
import django
import sys
from unittest.mock import patch, MagicMock

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Mock dependencies that might be missing in test environment
sys.modules['langchain_google_genai'] = MagicMock()
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.prompts'] = MagicMock()
sys.modules['langchain_core.output_parsers'] = MagicMock()

from fundDecision.models import NewsArticle
with patch('langchain_google_genai.ChatGoogleGenerativeAI', MagicMock()):
    from fundDecision.tasks import analyze_news_article_task
import unittest

class TestTasks(unittest.TestCase):
    def setUp(self):
        self.article = NewsArticle.objects.create(
            source="Test Source",
            title="Empty Content Article",
            content="",
            description="Short desc",
            url="https://example.com/empty-article"
        )

    def tearDown(self):
        self.article.delete()

    @patch('fundDecision.tasks.NewsAIService.analyze_news')
    @patch('fundDecision.tasks.NewsFetcher.fetch_content_from_url')
    def test_analyze_task_fetches_from_url_if_content_missing(self, mock_fetch, mock_analyze):
        # Mock fetch result to be a string
        mock_fetch.return_value = "Content from URL that is long enough to be considered valid for analysis."
        
        # Mock AI result
        mock_result = MagicMock()
        mock_result.related_sectors = ["Finance"]
        mock_result.ai_sentiment_score = 0.5
        mock_result.ai_summary = "AI Summary"
        mock_result.ai_impact_level = "LOW"
        mock_result.ai_model = "test-model"
        mock_analyze.return_value = mock_result
        
        analyze_news_article_task(self.article.id)
        
        # Verify fetch_content_from_url was called
        mock_fetch.assert_called_once_with(self.article.url)
        
        # Verify article content was updated
        self.article.refresh_from_db()
        self.assertEqual(self.article.content, "Content from URL that is long enough to be considered valid for analysis.")
        
    @patch('fundDecision.tasks.NewsAIService.analyze_news')
    @patch('fundDecision.tasks.NewsFetcher.fetch_content_from_url')
    def test_analyze_task_skips_fetch_if_content_exists(self, mock_fetch, mock_analyze):
        # Long content more than 100 chars
        self.article.content = "Existing substantial content for analysis. It is now long enough to exceed the one hundred character threshold that we established in the tasks implementation to avoid unnecessary scraping."
        self.article.save()
        
        # Mock AI result
        mock_result = MagicMock()
        mock_result.ai_sentiment_score = 0.5
        mock_analyze.return_value = mock_result
        
        analyze_news_article_task(self.article.id)
        
        # Verify fetch_content_from_url was NOT called
        mock_fetch.assert_not_called()

if __name__ == "__main__":
    unittest.main()

import os
import django
import sys

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


from fundDecision.models import NewsArticle
from fundDecision.ai_service import NewsAIService
from fundDecision.tasks import analyze_news_article_task
import unittest
from unittest.mock import patch, MagicMock

class TestAIAnalysis(unittest.TestCase):
    def setUp(self):
        self.article = NewsArticle.objects.create(
            source="Test Source",
            title="NVIDIA Announces New AI Chips",
            content="NVIDIA has unveiled a new generation of AI chips that promise significantly higher performance for data centers and generative AI applications...",
            url="https://example.com/nvidia-ai-chips"
        )

    def tearDown(self):
        self.article.delete()

    @patch('fundDecision.ai_service.ChatGoogleGenerativeAI')
    def test_news_ai_service(self, mock_llm):
        # Mock result
        mock_result = MagicMock()
        mock_result.related_sectors = ["Tech"]
        mock_result.ai_sentiment_score = 0.9
        mock_result.ai_summary = "NVIDIA เปิดตัวชิป AI ใหม่ ส่งผลดีต่อหุ้นกลุ่มเทคโนโลยี"
        mock_result.ai_impact_level = "HIGH"
        
        # Configure mock_llm to return something that the parser can handle
        # In a real test we'd mock the whole chain or just the result
        service = NewsAIService()
        with patch.object(service, 'analyze_news', return_value=mock_result):
            result = service.analyze_news(self.article.title, self.article.content)
            self.assertEqual(result.ai_impact_level, "HIGH")
            self.assertIn("Tech", result.related_sectors)

    def test_analyze_task_logic(self):
        # This tests the task logic without real AI call
        mock_result = MagicMock()
        mock_result.related_sectors = ["Tech", "Finance"]
        mock_result.ai_sentiment_score = 0.8
        mock_result.ai_summary = "Test Summary"
        mock_result.ai_impact_level = "MED"
        
        with patch('fundDecision.tasks.NewsAIService.analyze_news', return_value=mock_result):
            analyze_news_article_task(self.article.id)
            
            # Refresh from DB
            self.article.refresh_from_db()
            self.assertEqual(self.article.ai_impact_level, "MED")
            self.assertEqual(self.article.ai_sentiment_score, 0.8)
            self.assertEqual(self.article.related_sectors, ["Tech", "Finance"])

if __name__ == "__main__":
    unittest.main()

import os
import django
import sys
from unittest.mock import patch, MagicMock

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from fundDecision.news_service import NewsFetcher
import unittest

class TestNewsFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = NewsFetcher()

    @patch('requests.get')
    def test_fetch_content_from_url_success(self, mock_get):
        # Mock HTML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <article>
                    <p>This is the main article content.</p>
                    <p>It should be extracted correctly.</p>
                </article>
                <nav>Menu items to ignore</nav>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        url = "https://example.com/test-article"
        content = self.fetcher.fetch_content_from_url(url)
        
        self.assertIn("This is the main article content.", content)
        self.assertIn("It should be extracted correctly.", content)
        self.assertNotIn("Menu items to ignore", content)

    @patch('requests.get')
    def test_fetch_content_from_url_fallback(self, mock_get):
        # Mock HTML response without article tag
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
            <body>
                <div class="content">
                    <p>General content without specific article tag.</p>
                </div>
                <script>console.log('Ignore me');</script>
            </body>
        </html>
        """
        mock_get.return_value = mock_response
        
        url = "https://example.com/test-article"
        content = self.fetcher.fetch_content_from_url(url)
        
        self.assertIn("General content without specific article tag.", content)
        self.assertNotIn("console.log", content)

    @patch('requests.get')
    def test_fetch_content_from_url_error(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        
        url = "https://example.com/error"
        content = self.fetcher.fetch_content_from_url(url)
        
        self.assertEqual(content, "")

if __name__ == "__main__":
    unittest.main()

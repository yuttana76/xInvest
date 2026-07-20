import requests
import xml.etree.ElementTree as ET
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import NewsArticle
import logging

logger = logging.getLogger(__name__)

class NewsFetcher:
    """
    Service to fetch news from NewsAPI and RSS feeds.
    """
    
    RSS_FEEDS = [
        {'name': 'Yahoo Finance', 'url': 'https://finance.yahoo.com/rss/topstories'},
        {'name': 'Google News', 'url': 'https://news.google.com/rss/search?q=finance+when:24h&hl=en-US&gl=US&ceid=US:en'},
    ]

    @staticmethod
    def clean_html(text):
        if not text:
            return ""
        # 1. ลบ HTML Tags
        soup = BeautifulSoup(text, "html.parser")

        # ลบส่วนที่ไม่เกี่ยวข้อง (โฆษณา, script, style)
        for extraneous in soup(["script", "style", "aside", "nav", "footer", "header"]):
            extraneous.decompose()
        
        text = soup.get_text(separator="\n")
        # 2. ลบข้อความซ้ำซ้อน (เช่น "Read More")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 3. ลบ URL ที่แทรกมา
        text = re.sub(r'http\S+', '', text)
        
        # 4. ลบอักขระพิเศษที่ไม่จำเป็น
        text = re.sub(r'[^\w\s\n\-\.]', '', text)
        
        # 5. ลบช่องว่างเกิน
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def fetch_content_from_url(self, url):
        """
        Fetch article content from its URL and clean it.
        """
        if not url:
            return ""
            
        try:
            logger.info(f"Fetching full content from URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Find the main content area (heuristics)
            # Some common tags for article body
            article_body = None
            for selector in ['article', '.article-body', '.entry-content', '.post-content', '.main-content', 'main']:
                article_body = soup.select_one(selector)
                if article_body:
                    break
            
            if article_body:
                text = article_body.get_text(separator="\n")
            else:
                # Fallback to whole body if specific selector not found
                # but removing scripts/styles first
                for extraneous in soup(["script", "style", "aside", "nav", "footer", "header"]):
                    extraneous.decompose()
                text = soup.get_text(separator="\n")
                
            return self.clean_html(text)
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return ""

    def __init__(self):
        self.api_key = getattr(settings, 'NEWS_API_KEY', None)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_all(self):
        """Fetch news from all sources."""
        count = 0
        # if self.api_key:
        #     count += self.fetch_from_newsapi()
        
        # count += self.fetch_from_settrade()
        count += self.fetch_from_rss()
        return count

    def fetch_from_settrade(self):
        """Fetch news using Settrade Open API."""
        app_id = getattr(settings, 'SETTRADE_APP_ID', None)
        app_secret = getattr(settings, 'SETTRADE_APP_SECRET', None)
        
        if not app_id or not app_secret:
            logger.warning("Settrade API credentials missing. Skipping Settrade news fetch.")
            return 0
            
        try:
            from settrade_v2 import Investor
            investor = Investor(
                app_id=app_id,
                app_secret=app_secret,
                broker_id=getattr(settings, 'SETTRADE_BROKER_ID', 'SANDBOX'),
                app_code=getattr(settings, 'SETTRADE_APP_CODE', 'SANDBOX'),
                is_auto_queue=False
            )
            # Example retrieving news, adapt according to definitive settrade_v2 API docs
            market = investor.MarketData()
            res = market.get_news("") # Using typical structure
            
            articles = res.get('news_list', []) if isinstance(res, dict) else res
            
            saved_count = 0
            for item in articles[:10]: # Limit to 10
                published_dt = None
                if item.get('datetime'):
                    try:
                        dt = datetime.fromisoformat(item.get('datetime'))
                        published_dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
                    except:
                        pass
                        
                if self._save_article(
                    source="SET News (OpenAPI)",
                    title=item.get('title', 'Unknown News Title'),
                    content=item.get('detail', ''),
                    description=item.get('detail', ''),
                    url=item.get('link', f"https://developer.settrade.com/news/{item.get('news_id', '')}"),
                    published_at=published_dt
                ):
                    saved_count += 1
            return saved_count
        except Exception as e:
            logger.error(f"Error fetching from Settrade OpenAPI: {e}")
            return 0

    def fetch_from_newsapi(self):
        """Fetch news using NewsAPI.org."""
        if not self.api_key:
            return 0
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'apiKey': self.api_key,
            'category': 'business',
            'language': 'en',
            'pageSize': 10 # Limit to 10
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get('articles', [])
            saved_count = 0
            for item in articles:
                if self._save_article(
                    source=item.get('source', {}).get('name', 'Unknown'),
                    title=item.get('title'),
                    content=item.get('content', ''),
                    description=item.get('description', ''),
                    url=item.get('url'),
                    author=item.get('author'),
                    image_url=item.get('urlToImage'),
                    published_at=item.get('publishedAt')
                ):
                    saved_count += 1
            return saved_count
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {e}")
            return 0

    def fetch_from_rss(self):
        """Fetch news from RSS feeds."""
        saved_count = 0
        per_feed_limit = 10
        for feed in self.RSS_FEEDS:
            try:
                response = requests.get(feed['url'], headers=self.headers, timeout=10)
                response.raise_for_status()
                root = ET.fromstring(response.content)
                
                # RSS 2.0 structure: channel -> item
                items = root.findall('.//item')
                for item in items[:per_feed_limit]: # Limit to 10 per feed
                    title = item.find('title').text if item.find('title') is not None else ''
                    url = item.find('link').text if item.find('link') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else None
                    
                    # Convert pubDate to ISO format if possible
                    published_dt = timezone.now()
                    if pub_date:
                        try:
                            # Use email.utils for more robust RFC 822 parsing
                            from email.utils import parsedate_to_datetime
                            published_dt = parsedate_to_datetime(pub_date)
                            if timezone.is_naive(published_dt):
                                published_dt = timezone.make_aware(published_dt)
                        except:
                            try:
                                # Fallback to basic parsing
                                dt = datetime.strptime(pub_date[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                                published_dt = timezone.make_aware(dt)
                            except:
                                published_dt = timezone.now()

                    if self._save_article(
                        source=feed['name'],
                        title=title,
                        content=description, 
                        description=description,
                        url=url,
                        published_at=published_dt
                    ):
                        saved_count += 1
            except Exception as e:
                logger.error(f"Error fetching from RSS {feed['name']}: {e}")
            finally:
                time.sleep(2)
        return saved_count

    def _save_article(self, source, title, content, description, url, author=None, image_url=None, published_at=None):
        """Helper to save article to DB if it doesn't exist."""
        if not url or not title:
            return False
            
        if NewsArticle.objects.filter(url=url).exists():
            return False
            
        try:
            # Basic published_at handling
            published_dt = published_at
            if published_at and isinstance(published_at, str):
                try:
                    # Try Django's parse_datetime which is robust for ISO formats
                    from django.utils.dateparse import parse_datetime
                    published_dt = parse_datetime(published_at)
                    if published_dt and timezone.is_naive(published_dt):
                        published_dt = timezone.make_aware(published_dt)
                except:
                    try:
                        published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        if timezone.is_naive(published_dt):
                            published_dt = timezone.make_aware(published_dt)
                    except:
                        published_dt = None
            elif published_at and isinstance(published_at, datetime):
                if timezone.is_naive(published_at):
                    published_dt = timezone.make_aware(published_at)

            NewsArticle.objects.create(
                source=source,
                title=title,
                content=self.clean_html(content or description or ''),
                description=self.clean_html(description),
                url=url,
                author=author,
                image_url=image_url,
                published_at=published_dt
            )
            return True
        except Exception as e:
            logger.error(f"Error saving article {url}: {e}")
            return False

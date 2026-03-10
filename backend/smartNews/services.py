import yfinance as yf
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
import os
from .models import Fund, FundAnalysis

class FundAggregatorService:
    @staticmethod
    def fetch_fund_data(fund_code):
        # Example fetching logic (Mock for now, can be expanded with real Scrapers/APIs)
        # Using yfinance for prices if it matches a ticker, or scraping for Thai funds
        try:
            # Placeholder for Thai fund scraping or yfinance
            data = {
                "nav": 15.2345,
                "holdings": [
                    {"name": "CPALL", "weight": 8.5},
                    {"name": "AOT", "weight": 7.2},
                    {"name": "PTT", "weight": 6.8},
                ],
                "sector_allocation": {
                    "Commerce": 15.0,
                    "Transport": 12.0,
                    "Energy": 18.0,
                    "Others": 55.0
                }
            }
            return data
        except Exception as e:
            print(f"Error fetching data for {fund_code}: {e}")
            return None

class AISentimentService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def analyze_news(self, news_items):
        if not self.model:
            return {"note": "AI service not configured.", "sentiment": 0.0}
        
        prompt = f"Analyze the following investment news and summarize the impact on relevant funds in 3 clear lines. Also provide a sentiment score from -1.0 (very bearish) to 1.0 (very bullish).\n\nNews: {news_items}"
        
        try:
            response = self.model.generate_content(prompt)
            # Simple parsing of response text (can be improved with JSON mode)
            return {
                "note": response.text,
                "sentiment": 0.5 # Mock score for now
            }
        except Exception as e:
            print(f"AI Analysis error: {e}")
            return {"note": "Error in AI analysis.", "sentiment": 0.0}

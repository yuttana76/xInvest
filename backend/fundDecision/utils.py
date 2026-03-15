# tasks.py (Celery Task)
# import requests
# from .models import NewsArticle, Fund
# from .ai_utils import analyze_sentiment

# def fetch_daily_finance_news():
#     api_key = "YOUR_NEWS_API_KEY"
#     url = f"https://newsapi.org/v2/everything?q=investment+thailand&apiKey={api_key}"
    
#     response = requests.get(url).json()
#     articles = response.get('articles', [])

#     for art in articles:
#         # 1. บันทึกข่าวลง Database
#         news_obj, created = NewsArticle.objects.get_or_create(
#             url=art['url'],
#             defaults={
#                 'title': art['title'],
#                 'content': art['description'],
#                 'published_at': art['publishedAt']
#             }
#         )

#         # 2. ส่งให้ AI วิเคราะห์ (ถ้าเป็นข่าวใหม่)
#         if created:
#             sentiment_data = analyze_sentiment(art['title'], art['description'])
#             news_obj.sentiment_score = sentiment_data['sentiment_score']
#             news_obj.ai_summary = sentiment_data['ai_advice']
#             news_obj.save()

import pandas as pd
import numpy as np
from .models import FundNAV

def calculate_fund_metrics(fund_id):
    # 1. ดึงข้อมูล NAV ย้อนหลังมาเป็น DataFrame
    nav_data = FundNAV.objects.filter(fund_id=fund_id).order_by('date').values('date', 'nav')
    df = pd.DataFrame(list(nav_data))
    
    if df.empty or len(df) < 2:
        return None

    # 2. คำนวณผลตอบแทนรายวัน (Daily Returns)
    df['nav'] = df['nav'].astype(float)
    df['returns'] = df['nav'].pct_change()
    
    # 3. คำนวณค่าสถิติ (สมมติให้ Risk-free rate = 2.5% ต่อปี หรือ 0.025/252 ต่อวัน)
    rf_daily = 0.025 / 252
    
    # Sharpe Ratio
    avg_return = df['returns'].mean()
    std_dev = df['returns'].std()
    sharpe_ratio = (avg_return - rf_daily) / std_dev * np.sqrt(252) if std_dev != 0 else 0
    
    # Max Drawdown
    cumulative_returns = (1 + df['returns']).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    
    # Volatility (Annualized)
    volatility = std_dev * np.sqrt(252)

    return {
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown": round(max_drawdown * 100, 2), # %
        "volatility": round(volatility * 100, 2)      # %
    }
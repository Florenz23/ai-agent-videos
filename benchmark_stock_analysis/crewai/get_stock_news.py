# stock_news.py

import yfinance as yf
from datetime import datetime

def get_company_news(ticker, num_articles=8):
    stock = yf.Ticker(ticker)
    all_news = stock.news
    
    # Get the latest news articles
    latest_news = []
    for article in all_news[:num_articles]:
        latest_news.append({
            'Title': article['title'],
            'Publisher': article['publisher'],
            'Link': article['link'],
            'Date': datetime.fromtimestamp(article['providerPublishTime']).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return latest_news

if __name__ == "__main__":
    # Example usage
    nvidia_news = get_company_news('NVDA')
    for i, article in enumerate(nvidia_news, 1):
        print(f"\n{i}. {article['Title']}")
        print(f"   Publisher: {article['Publisher']}")
        print(f"   Date: {article['Date']}")
        print(f"   Link: {article['Link']}")
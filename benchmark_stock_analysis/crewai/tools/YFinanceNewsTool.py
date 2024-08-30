from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import yfinance as yf
from datetime import datetime
from typing import Type

# Define the input schema using Pydantic
class YFinanceNewsToolInput(BaseModel):
    """Input schema for YFinanceNewsTool."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)")
    num_articles: int = Field(8, description="Number of latest news articles to retrieve")

# Define the tool class
class YFinanceNewsTool(BaseTool):
    name: str = "YFinance News Tool"
    description: str = "Fetches the latest news articles for a given stock ticker using yfinance."
    args_schema: Type[BaseModel] = YFinanceNewsToolInput

    def _run(self, ticker: str, num_articles: int = 8) -> str:
        """
        Fetches the latest news articles for a given stock ticker using yfinance.

        :param ticker: Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)
        :param num_articles: Number of latest news articles to retrieve (default: 8)
        :return: A string containing the titles, publishers, dates, and links of the latest news articles.
        """
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
        
        # Formatting the news articles for output
        output = []
        for i, article in enumerate(latest_news, 1):
            output.append(f"{i}. {article['Title']}\n   Publisher: {article['Publisher']}\n   Date: {article['Date']}\n   Link: {article['Link']}")
        
        return "\n\n".join(output)

    async def _arun(self, ticker: str, num_articles: int = 8) -> str:
        """Asynchronous version of the _run method."""
        return self._run(ticker, num_articles)

# Example usage within CrewAI
if __name__ == "__main__":
    tool_instance = YFinanceNewsTool()
    nvidia_news = tool_instance.run(ticker='NVDA')
    print(nvidia_news)

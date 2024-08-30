from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import yfinance as yf
from typing import Type

# Define the input schema using Pydantic
class YFinanceStockAnalysisToolInput(BaseModel):
    """Input schema for YFinanceStockAnalysisTool."""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)")

# Define the tool class
class YFinanceStockAnalysisTool(BaseTool):
    name: str = "YFinance Stock Analysis Tool"
    description: str = "Fetches and analyzes stock data for a given ticker using yfinance, including Buffett-style analysis."
    args_schema: Type[BaseModel] = YFinanceStockAnalysisToolInput

    def _run(self, ticker: str) -> str:
        """
        Fetches and analyzes stock data for a given ticker using yfinance, including Buffett-style analysis.
        :param ticker: Stock ticker symbol (e.g., 'AAPL' for Apple Inc.)
        :return: A string containing the stock's financial KPIs and Buffett-style analysis.
        """
        # Fetch the stock data
        stock = yf.Ticker(ticker)
        
        # Get the info dictionary
        info = stock.info
        
        # Get historical data
        history = stock.history(period="5y")
        
        # Calculate 52-Week High/Low
        week_52_high = history['High'].tail(252).max()
        week_52_low = history['Low'].tail(252).min()
        
        # Calculate 5-year revenue growth rate
        financials = stock.financials
        if not financials.empty and 'Total Revenue' in financials.index:
            revenue_5y = financials.loc['Total Revenue'].iloc[:5]
            revenue_growth = (revenue_5y.iloc[0] / revenue_5y.iloc[-1]) ** (1/5) - 1 if len(revenue_5y) >= 5 else None
        else:
            revenue_growth = None
        
        # Prepare the analysis results
        analysis = {
            'Ticker Symbol': ticker,
            'Company Name': info.get('longName', 'N/A'),
            'Current Price': info.get('currentPrice', 'N/A'),
            '52-Week High': round(week_52_high, 2),
            '52-Week Low': round(week_52_low, 2),
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'P/B Ratio': info.get('priceToBook', 'N/A'),
            'Debt-to-Equity Ratio': info.get('debtToEquity', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
            'Dividend Yield (%)': info.get('dividendYield', 'N/A'),
            '5-Year Revenue Growth Rate (%)': revenue_growth,
            'Free Cash Flow': info.get('freeCashflow', 'N/A'),
            'Profit Margin': info.get('profitMargins', 'N/A'),
            'Operating Margin': info.get('operatingMargins', 'N/A'),
            'Earnings Growth': info.get('earningsGrowth', 'N/A'),
            'Revenue Growth': info.get('revenueGrowth', 'N/A'),
            'Analyst Target Price': info.get('targetMedianPrice', 'N/A'),
            'Beta': info.get('beta', 'N/A'),
            '5-Year Average Return on Equity (%)': info.get('returnOnEquity', 'N/A')
        }
        
        # Convert percentage values
        for key in ['Dividend Yield (%)', '5-Year Revenue Growth Rate (%)', 'Profit Margin', 'Operating Margin', 'Earnings Growth', 'Revenue Growth', '5-Year Average Return on Equity (%)']:
            if analysis[key] not in ['N/A', None]:
                analysis[key] = round(analysis[key] * 100, 2)
        
        # Format the analysis results for output
        output = "\n".join([f"{key}: {value}" for key, value in analysis.items()])
        
        return output

    async def _arun(self, ticker: str) -> str:
        """Asynchronous version of the _run method."""
        return self._run(ticker)

# Example usage within CrewAI
if __name__ == "__main__":
    tool_instance = YFinanceStockAnalysisTool()
    nvidia_analysis = tool_instance.run(ticker='NVDA')
    print(nvidia_analysis)
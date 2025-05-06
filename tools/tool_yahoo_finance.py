import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    """
    Retrieve stock data from Yahoo Finance for a specific ticker,
    including key performance indicators.
    
    Parameters:
    -----------
    ticker : str
        The stock ticker symbol (e.g., 'AAPL' for Apple).
        
    Returns:
    --------
    list
        List of key performance indicators
    """
    try:
        # Create a Ticker object
        stock = yf.Ticker(ticker)
        
        # Get stock info
        info = stock.info
        
        # Create list of KPIs
        kpis = [
            f"Company: {info.get('shortName', 'N/A')}",
            f"Sector: {info.get('sector', 'N/A')}",
            f"Industry: {info.get('industry', 'N/A')}",
            f"Market Cap (B): {round(info.get('marketCap', 0) / 1_000_000_000, 2)}",
            f"P/E Ratio: {info.get('trailingPE', 'N/A')}",
            f"Forward P/E: {info.get('forwardPE', 'N/A')}",
            f"EPS (TTM): {info.get('trailingEps', 'N/A')}",
            f"Dividend Yield (%): {round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 'N/A'}",
            f"Profit Margin (%): {round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else 'N/A'}",
            f"ROE (%): {round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 'N/A'}",
            f"Debt to Equity: {info.get('debtToEquity', 'N/A')}",
            f"Beta (5Y): {info.get('beta', 'N/A')}",
            f"52-Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}",
            f"52-Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}",
            f"Analyst Rating: {info.get('recommendationKey', 'N/A').capitalize() if info.get('recommendationKey') else 'N/A'}",
            f"Target Price: {info.get('targetMeanPrice', 'N/A')}"
        ]
        
        return kpis
    
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return []

# Example usage
if __name__ == "__main__":
    # Get data for Apple (AAPL)
    ticker_symbol = "AAPL"
    kpis = get_stock_data(ticker_symbol)
    
    # Print KPIs
    print(f"\n===== Key Performance Indicators for {ticker_symbol} =====")
    for kpi in kpis:
        print(kpi)
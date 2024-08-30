import yfinance as yf

def yahoo_finance_tool(ticker_sombol: str) -> dict:
    """
    Input: Ticker symbol of a stock, it will return stock data
    """
    # Fetch the stock data
    stock = yf.Ticker(ticker_sombol)
    
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
        revenue_growth = (revenue_5y.iloc[0] / revenue_5y.iloc[-1]) ** (1/5) - 1
    else:
        revenue_growth = 'N/A'
    
    # Prepare the analysis results
    analysis = {
        'Ticker Symbol': ticker_sombol,
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
        '5-Year Revenue Growth Rate (%)': revenue_growth if isinstance(revenue_growth, float) else 'N/A',
        'Free Cash Flow': info.get('freeCashflow', 'N/A'),
        'Profit Margin': info.get('profitMargins', 'N/A'),
        'Operating Margin': info.get('operatingMargins', 'N/A'),
        'Earnings Growth': info.get('earningsGrowth', 'N/A'),
        'Revenue Growth': info.get('revenueGrowth', 'N/A'),
        'Analyst Target Price': info.get('targetMedianPrice', 'N/A'),
        'Beta': info.get('beta', 'N/A')
    }
    
    # Convert percentage values
    for key in ['Dividend Yield (%)', '5-Year Revenue Growth Rate (%)', 'Profit Margin', 'Operating Margin', 'Earnings Growth', 'Revenue Growth']:
        if analysis[key] != 'N/A':
            analysis[key] = round(analysis[key] * 100, 2)
    
    return analysis


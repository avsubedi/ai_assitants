import os 
import yfinance as yf
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
client = genai.Client(api_key = os.environ["GEMINI_API_KEY"])
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a stock research assistant that uses Yahoo Finance data.
- Use search_symbol to find tickers when the user gives a company name or theme.
- Use get_stock_snapshot to fetch data before commenting on any stock. Never invent numbers.
- For recommendations, compare several candidates, then give a clear view
  (e.g. Buy / Hold / Avoid) with reasons based on valuation, momentum, analyst
  consensus, and risks.
- Keep answers concise and mention data limitations.
- End recommendations with a short note that this is not financial advice."""

def search_symbol(query: str) -> dict:
    """Search Yahoo Finance for stock tickers by company name or keyword.

    Args:
        query: Company name or keyword, e.g. "Nvidia" or "solar energy".
    """
    try:
        results = yf.Search(query, max_results=6).quotes
        return {
            "results": [
                {
                    "symbol": r.get("symbol"),
                }
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def get_stock_snapshot(ticker: str) -> dict:
    """Get price, valuation, analyst, and momentum data for a stock ticker.

    Args:
        ticker: Stock symbol, e.g. "AAPL".
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="1y")

        data = {
            "ticker": ticker.upper(),
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "market_cap": info.get("marketCap"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "analyst_rating": info.get("recommendationKey"),
            "analyst_target_mean": info.get("targetMeanPrice"),
            "num_analysts": info.get("numberOfAnalystOpinions"),
            "revenue_growth": info.get("revenueGrowth"),
            "profit_margin": info.get("profitMargins"),
            "debt_to_equity": info.get("debtToEquity"),
        }

        if not hist.empty:
            close = hist["Close"]
            data["1y_return_pct"] = round((close.iloc[-1] / close.iloc[0] - 1) * 100, 2)
            data["50d_avg"] = round(close.tail(50).mean(), 2)
            data["200d_avg"] = round(close.tail(200).mean(), 2)

        return data
    except Exception as e:
        return {"error": f"Could not fetch {ticker}: {e}"}
    
def main():
    
    
    while True:
        user_input = input('Enter ticker symbol or quit to exit ').lower()
        if user_input == 'quit':
            print('have a nice day')
            break
        else:
            result = search_symbol(user_input)
            print(result)
            answer = input(f'would you like to search for stock info for {result}')
            if answer != 'no':
                print(get_stock_snapshot(result))
        
main()
        
# Fetch market prices and Treasury yields
import yfinance as yf
from src.signal_engine import analyze_market
from datetime import datetime, timedelta, timezone


TICKERS = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
   # "2Y Treasury": "^IRX",   # temporary — we'll replace with proper Treasury data
    "VIX": "^VIX",
}


def get_market_snapshot():
    results = {}

    for name, ticker in TICKERS.items():
        data = yf.Ticker(ticker).history(period="5d")

        if data.empty:
            results[name] = None
            continue

        current = data["Close"].iloc[-1]
        previous = data["Close"].iloc[-2]

        change_pct = ((current - previous) / previous) * 100

        results[name] = {
            "value": round(float(current), 2),
            "change_pct": round(float(change_pct), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
}

    return results

if __name__ == "__main__":

    market_data = get_market_snapshot()
    print(get_market_snapshot())
    print("\nMARKET DATA")
    print(market_data)

    analysis = analyze_market(market_data)

    print("\nMARKET SIGNAL")
    print("Sentiment:", analysis["sentiment"])
    print("Score:", analysis["score"])

    print("\nReasons:")

    for reason in analysis["reasons"]:
        print("-", reason)
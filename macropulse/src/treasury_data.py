import os
import requests
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

SERIES = {
    "2Y": "DGS2",
    "5Y": "DGS5",
    "10Y": "DGS10",
}


def get_treasury_yields():

    if not FRED_API_KEY:
        raise ValueError("FRED_API_KEY is missing from .env")

    results = {}

    for maturity, series_id in SERIES.items():

        url = "https://api.stlouisfed.org/fred/series/observations"

        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        observations = response.json()["observations"]

        # FRED can contain "." for missing observations.
        valid = [
            obs for obs in observations
            if obs["value"] != "."
        ]

        if len(valid) < 2:
            results[maturity] = None
            continue

        current = float(valid[0]["value"])
        previous = float(valid[1]["value"])

        # 1 percentage point = 100 basis points
        change_bps = (current - previous) * 100

        results[maturity] = {
            "yield": round(current, 3),
            "previous": round(previous, 3),
            "change_bps": round(change_bps, 1),
            "date": valid[0]["date"]
        }

    return results


if __name__ == "__main__":
    print(get_treasury_yields())
import requests
from datetime import datetime


BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

SERIES = {
    "unemployment_rate": "LNS14000000",
    "nonfarm_payrolls": "CES0000000001",
    "avg_hourly_earnings": "CES0500000003",
}


def get_bls_labor_data():

    current_year = datetime.now().year
    start_year = current_year - 1

    payload = {
        "seriesid": list(SERIES.values()),
        "startyear": str(start_year),
        "endyear": str(current_year)
    }

    response = requests.post(
        BLS_URL,
        json=payload,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    if data["status"] != "REQUEST_SUCCEEDED":
        raise RuntimeError(
            f'BLS request failed: {data.get("message")}'
        )

    id_to_name = {
        series_id: name
        for name, series_id in SERIES.items()
    }

    results = {}

    for series in data["Results"]["series"]:

        series_id = series["seriesID"]
        name = id_to_name[series_id]

        monthly_rows = [
            item
            for item in series["data"]
            if item["period"].startswith("M")
            and item["period"] != "M13"
        ]

        monthly_rows.sort(
            key=lambda x: (
                int(x["year"]),
                int(x["period"][1:])
            ),
            reverse=True
        )

        latest = monthly_rows[0]
        previous = monthly_rows[1]

        results[name] = {
            "latest": float(latest["value"]),
            "previous": float(previous["value"]),
            "year": latest["year"],
            "month": latest["periodName"]
        }

    return results

def calculate_payroll_change(labor_data):

    payroll = labor_data["nonfarm_payrolls"]

    current = payroll["latest"]
    previous = payroll["previous"]

    change = current - previous

    return round(change, 1)

def calculate_wage_change(labor_data):

    wages = labor_data["avg_hourly_earnings"]

    current = wages["latest"]
    previous = wages["previous"]

    pct_change = (
        (current - previous) / previous
    ) * 100

    return round(pct_change, 2)

if __name__ == "__main__":
        data = get_bls_labor_data()

        print(data)

        payroll_change = calculate_payroll_change(data)

        print("\nNFP monthly change:", payroll_change, "K")
from datetime import datetime, date


def check_treasury_freshness(treasury_data):

    dates = [
        item["date"]
        for item in treasury_data.values()
        if item is not None
    ]

    if not dates:
        return {
            "status": "NO DATA",
            "latest_date": None
        }

    latest_date = max(dates)

    observation_date = datetime.strptime(
        latest_date,
        "%Y-%m-%d"
    ).date()

    today = date.today()

    age_days = (today - observation_date).days

    if age_days == 0:
        status = "CURRENT"

    elif age_days <= 1:
        status = "RECENT"

    else:
        status = "STALE"

    return {
        "status": status,
        "latest_date": latest_date,
        "age_days": age_days
    }
# Interpret market and macro signals
def analyze_market(market_data):

    sp500 = market_data["S&P 500"]["change_pct"]
    nasdaq = market_data["Nasdaq"]["change_pct"]
    vix = market_data["VIX"]["change_pct"]

    score = 0
    reasons = []

    # S&P 500
    if sp500 > 0:
        score += 1
        reasons.append("S&P 500 is rising")
    else:
        score -= 1
        reasons.append("S&P 500 is falling")

    # Nasdaq
    if nasdaq > 0:
        score += 1
        reasons.append("Nasdaq is rising")
    else:
        score -= 1
        reasons.append("Nasdaq is falling")

    # VIX works in the opposite direction
    if vix < 0:
        score += 1
        reasons.append("VIX is falling")
    else:
        score -= 1
        reasons.append("VIX is rising")

    if score >= 2:
        sentiment = "RISK-ON"
    elif score <= -2:
        sentiment = "RISK-OFF"
    else:
        sentiment = "MIXED"

    return {
        "sentiment": sentiment,
        "score": score,
        "reasons": reasons
    }


def analyze_rates(treasury_data):
    """Analyze treasury yields and generate a signal."""
    reasons = []

    changes = {
        maturity: data["change_bps"]
        for maturity, data in treasury_data.items()
        if data is not None
    }

    if not changes:
        return {
            "signal": "NO DATA",
            "reasons": ["Treasury data unavailable"]
        }

    two_year = changes.get("2Y")
    five_year = changes.get("5Y")
    ten_year = changes.get("10Y")

    # All major yields falling
    if (
        two_year is not None
        and five_year is not None
        and ten_year is not None
        and two_year < 0
        and five_year < 0
        and ten_year < 0
    ):
        signal = "YIELDS FALLING"

    # All major yields rising
    elif (
        two_year is not None
        and five_year is not None
        and ten_year is not None
        and two_year > 0
        and five_year > 0
        and ten_year > 0
    ):
        signal = "YIELDS RISING"

    else:
        signal = "MIXED"

    for maturity, change in changes.items():

        if change < 0:
            direction = "falling"
        elif change > 0:
            direction = "rising"
        else:
            direction = "unchanged"

        reasons.append(
            f"{maturity} yield is {direction} ({change:+.1f} bps)"
        )

    return {
        "signal": signal,
        "reasons": reasons
    }

def analyze_narrative(market_analysis, rates_analysis):
    market = market_analysis["sentiment"]
    rates = rates_analysis["signal"]

    if market == "RISK-ON" and rates == "YIELDS FALLING":
        narrative = "FED RELIEF"
        explanation = (
            "Stocks are rising while Treasury yields are falling. "
            "Markets may be responding positively to lower rate expectations."
        )

    elif market == "RISK-OFF" and rates == "YIELDS FALLING":
        narrative = "GROWTH FEAR"
        explanation = (
            "Stocks and Treasury yields are both falling. "
            "Lower yields may reflect concerns about economic growth "
            "rather than simply Fed relief."
        )

    elif market == "RISK-OFF" and rates == "YIELDS RISING":
        narrative = "HAWKISH PRESSURE"
        explanation = (
            "Stocks are falling while Treasury yields are rising. "
            "Higher rate expectations or inflation concerns may be "
            "pressuring equity valuations."
        )

    elif market == "RISK-ON" and rates == "YIELDS RISING":
        narrative = "STRONG GROWTH / RISK-ON"
        explanation = (
            "Stocks and Treasury yields are both rising. "
            "Markets may be pricing stronger economic growth despite "
            "higher interest rates."
        )

    else:
        narrative = "MIXED / NO CONFIRMATION"
        explanation = (
            "Equity and Treasury signals do not currently provide "
            "a clean cross-market confirmation."
        )

    return {
        "narrative": narrative,
        "explanation": explanation
    }


def analyze_labor(
    actual_nfp,
    forecast_nfp,
    actual_unemployment,
    forecast_unemployment,
    actual_wages=None,
    forecast_wages=None
):

    weak_score = 0
    strong_score = 0
    reasons = []

    # NFP
    if actual_nfp < forecast_nfp:
        weak_score += 1
        reasons.append(
            f"NFP missed forecast: "
            f"{actual_nfp}K vs {forecast_nfp}K"
        )
    else:
        strong_score += 1
        reasons.append(
            f"NFP beat forecast: "
            f"{actual_nfp}K vs {forecast_nfp}K"
        )

    # Unemployment
    if actual_unemployment > forecast_unemployment:
        weak_score += 1
        reasons.append(
            f"Unemployment higher than expected: "
            f"{actual_unemployment}% vs "
            f"{forecast_unemployment}%"
        )
    else:
        strong_score += 1
        reasons.append(
            f"Unemployment at/below forecast: "
            f"{actual_unemployment}%"
        )

    # Wages
    if (
        actual_wages is not None
        and forecast_wages is not None
    ):
        if actual_wages < forecast_wages:
            weak_score += 1
            reasons.append(
                "Wage growth was softer than expected"
            )
        else:
            strong_score += 1
            reasons.append(
                "Wage growth was stronger than expected"
            )

    if weak_score > strong_score:
        signal = "LABOR WEAKER THAN EXPECTED"

    elif strong_score > weak_score:
        signal = "LABOR STRONGER THAN EXPECTED"

    else:
        signal = "LABOR MIXED"

    return {
        "signal": signal,
        "weak_score": weak_score,
        "strong_score": strong_score,
        "reasons": reasons
    }
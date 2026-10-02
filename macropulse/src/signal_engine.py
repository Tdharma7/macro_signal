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

def analyze_narrative(
    labor_analysis,
    fed_analysis,
    market_analysis,
    rates_analysis
):
    """
    Combine labor, Fed expectations, rates and equity behavior
    to identify the dominant macro narrative.
    """

    labor = labor_analysis["signal"]
    fed = fed_analysis["signal"]
    market = market_analysis["sentiment"]
    rates = rates_analysis["signal"]

    scores = {
        "FED RELIEF": 0,
        "GROWTH FEAR": 0,
        "HAWKISH PRESSURE": 0,
        "STRONG GROWTH": 0
    }

    evidence = []

    # -------------------------------------------------
    # 1. LABOR
    # -------------------------------------------------

    if labor == "LABOR WEAKER THAN EXPECTED":

        scores["FED RELIEF"] += 1
        scores["GROWTH FEAR"] += 2

        evidence.append(
            "Labor data is weaker than expected"
        )

    elif labor == "LABOR STRONGER THAN EXPECTED":

        scores["STRONG GROWTH"] += 2
        scores["HAWKISH PRESSURE"] += 1

        evidence.append(
            "Labor data is stronger than expected"
        )

    else:

        evidence.append(
            "Labor data is mixed"
        )

    # -------------------------------------------------
    # 2. FED EXPECTATIONS
    # -------------------------------------------------

    if fed == "LESS HAWKISH":

        scores["FED RELIEF"] += 2

        evidence.append(
            "Fed expectations became less hawkish"
        )

    elif fed == "MORE DOVISH":

        scores["FED RELIEF"] += 2
        scores["GROWTH FEAR"] += 1

        evidence.append(
            "Fed expectations shifted toward rate cuts"
        )

    elif fed == "MORE HAWKISH":

        scores["HAWKISH PRESSURE"] += 3

        evidence.append(
            "Fed expectations became more hawkish"
        )

    elif fed == "LESS DOVISH":

        scores["HAWKISH PRESSURE"] += 1

        evidence.append(
            "Rate-cut expectations decreased"
        )

    else:

        evidence.append(
            "Fed expectations showed no material change"
        )

    # -------------------------------------------------
    # 3. TREASURY RATES
    # -------------------------------------------------

    if rates == "YIELDS FALLING":

        scores["FED RELIEF"] += 1
        scores["GROWTH FEAR"] += 1

        evidence.append(
            "Treasury yields are falling"
        )

    elif rates == "YIELDS RISING":

        scores["HAWKISH PRESSURE"] += 2
        scores["STRONG GROWTH"] += 1

        evidence.append(
            "Treasury yields are rising"
        )

    else:

        evidence.append(
            "Treasury yields are mixed"
        )

    # -------------------------------------------------
    # 4. EQUITY MARKET
    # -------------------------------------------------

    if market == "RISK-ON":

        scores["FED RELIEF"] += 2
        scores["STRONG GROWTH"] += 1

        evidence.append(
            "Equity markets are risk-on"
        )

    elif market == "RISK-OFF":

        scores["GROWTH FEAR"] += 3
        scores["HAWKISH PRESSURE"] += 1

        evidence.append(
            "Equity markets are risk-off"
        )

    else:

        evidence.append(
            "Equity sentiment is mixed"
        )

    # -------------------------------------------------
    # DETERMINE WINNER
    # -------------------------------------------------

    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    winner, winner_score = sorted_scores[0]
    second_place, second_score = sorted_scores[1]

    # Avoid forcing a narrative when scores are tied
    if winner_score == second_score:

        narrative = "MIXED / NO CLEAR NARRATIVE"

    else:

        narrative = winner

    total_score = sum(scores.values())

    if total_score > 0:
        agreement = round(
            (winner_score / total_score) * 100
        )
    else:
        agreement = 0

    return {
        "narrative": narrative,
        "scores": scores,
        "agreement": agreement,
        "evidence": evidence
    }



def analyze_fed(fed_data, threshold=2.0):

    hold_change = fed_data["hold"]["change"]
    hike_change = fed_data["hike"]["change"]
    cut_change = fed_data["cut"]["change"]

    reasons = []

    if abs(hold_change) >= threshold:
        reasons.append(
            f"Hold probability changed {hold_change:+.1f} percentage points"
        )

    if abs(hike_change) >= threshold:
        reasons.append(
            f"Hike probability changed {hike_change:+.1f} percentage points"
        )

    if abs(cut_change) >= threshold:
        reasons.append(
            f"Cut probability changed {cut_change:+.1f} percentage points"
        )

    # More dovish:
    # Probability is moving toward an actual rate cut.
    if cut_change >= threshold:
        signal = "MORE DOVISH"

    # More hawkish:
    # Probability is moving toward an actual hike.
    elif hike_change >= threshold:
        signal = "MORE HAWKISH"

    # Less hawkish:
    # Hike odds are falling, but cut odds are not meaningfully rising.
    elif hike_change <= -threshold and hold_change >= threshold:
        signal = "LESS HAWKISH"

    # Less dovish:
    # Cut odds are falling and hold odds are increasing.
    elif cut_change <= -threshold and hold_change >= threshold:
        signal = "LESS DOVISH"

    else:
        signal = "NO MATERIAL CHANGE"

    return {
        "signal": signal,
        "hold_change": hold_change,
        "hike_change": hike_change,
        "cut_change": cut_change,
        "reasons": reasons
    }



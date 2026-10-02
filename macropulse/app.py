import streamlit as st

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------

from src.market_data import get_market_snapshot
from src.treasury_data import get_treasury_yields

from src.labor_data import (
    get_bls_labor_data,
    calculate_payroll_change,
    calculate_wage_change,
)

from src.fed_data import build_fed_data

from src.signal_engine import (
    analyze_market,
    analyze_rates,
    analyze_fed,
    analyze_narrative,
)

from src.data_quality import check_treasury_freshness


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="MacroPulse",
    page_icon="📈",
    layout="wide",
)

st.title("📈 MacroPulse")
st.caption("Cross-Asset Macro Signal Dashboard")


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.header("Market Expectations")

    st.caption(
        "Enter market consensus forecasts before "
        "the economic release."
    )

    # ------------------------------
    # LABOR EXPECTATIONS
    # ------------------------------

    nfp_forecast = st.number_input(
        "NFP Forecast (K)",
        value=90.0,
        step=10.0,
    )

    unemployment_forecast = st.number_input(
        "Unemployment Forecast (%)",
        value=4.1,
        step=0.1,
        format="%.1f",
    )

    wage_forecast = st.number_input(
        "Hourly Earnings Forecast MoM (%)",
        value=0.3,
        step=0.1,
        format="%.1f",
    )

    st.divider()

    # ------------------------------
    # FEDWATCH EXPECTATIONS
    # ------------------------------

    st.header("FedWatch Expectations")

    st.caption(
        "For now, enter CME FedWatch probabilities manually."
    )

    previous_hold = st.number_input(
        "Previous Hold Probability (%)",
        value=75.6,
        step=0.1,
    )

    current_hold = st.number_input(
        "Current Hold Probability (%)",
        value=81.7,
        step=0.1,
    )

    previous_hike = st.number_input(
        "Previous Hike Probability (%)",
        value=24.4,
        step=0.1,
    )

    current_hike = st.number_input(
        "Current Hike Probability (%)",
        value=18.3,
        step=0.1,
    )

    previous_cut = st.number_input(
        "Previous Cut Probability (%)",
        value=0.0,
        step=0.1,
    )

    current_cut = st.number_input(
        "Current Cut Probability (%)",
        value=0.0,
        step=0.1,
    )


# ==================================================
# LOAD DATA
# ==================================================

market_data = get_market_snapshot()

treasury_data = get_treasury_yields()

labor_data = get_bls_labor_data()


# ==================================================
# CALCULATE LABOR DATA
# ==================================================

nfp_actual = calculate_payroll_change(
    labor_data
)

wage_actual = calculate_wage_change(
    labor_data
)

unemployment_actual = (
    labor_data["unemployment_rate"]["latest"]
)


# ==================================================
# MARKET ANALYSIS
# ==================================================

market_analysis = analyze_market(
    market_data
)


# ==================================================
# RATES ANALYSIS
# ==================================================

rates_analysis = analyze_rates(
    treasury_data
)

freshness = check_treasury_freshness(
    treasury_data
)


# ==================================================
# LABOR ANALYSIS
# ==================================================
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
            f"{actual_unemployment}% vs "
            f"{forecast_unemployment}%"
        )

    # Wages
    if (
        actual_wages is not None
        and forecast_wages is not None
    ):
        if actual_wages < forecast_wages:
            weak_score += 1
            reasons.append(
                f"Wage growth softer than expected: "
                f"{actual_wages}% vs "
                f"{forecast_wages}%"
            )
        else:
            strong_score += 1
            reasons.append(
                f"Wage growth stronger than expected: "
                f"{actual_wages}% vs "
                f"{forecast_wages}%"
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



labor_analysis = analyze_labor(
    actual_nfp=nfp_actual,
    forecast_nfp=nfp_forecast,
    actual_unemployment=unemployment_actual,
    forecast_unemployment=unemployment_forecast,
    actual_wages=wage_actual,
    forecast_wages=wage_forecast,
)


# ==================================================
# FED ANALYSIS
# ==================================================

fed_data = build_fed_data(
    previous_hold=previous_hold,
    current_hold=current_hold,
    previous_hike=previous_hike,
    current_hike=current_hike,
    previous_cut=previous_cut,
    current_cut=current_cut,
)

fed_analysis = analyze_fed(
    fed_data
)


# ==================================================
# NARRATIVE ENGINE
# ==================================================

if freshness["status"] in [
    "CURRENT",
    "RECENT",
]:

    narrative = analyze_narrative(
        labor_analysis=labor_analysis,
        fed_analysis=fed_analysis,
        market_analysis=market_analysis,
        rates_analysis=rates_analysis,
    )

else:

    narrative = {
        "narrative": "INSUFFICIENT CURRENT DATA",
        "scores": {},
        "agreement": 0,
        "evidence": [
            "Treasury data is stale."
        ],
    }


# ==================================================
# EQUITY MARKETS
# ==================================================

st.subheader("📊 Equity Markets")

col1, col2, col3 = st.columns(3)

sp500 = market_data["S&P 500"]
nasdaq = market_data["Nasdaq"]
vix = market_data["VIX"]


col1.metric(
    "S&P 500",
    f'{sp500["value"]:,.2f}',
    f'{sp500["change_pct"]:+.2f}%',
)


col2.metric(
    "Nasdaq",
    f'{nasdaq["value"]:,.2f}',
    f'{nasdaq["change_pct"]:+.2f}%',
)


col3.metric(
    "VIX",
    f'{vix["value"]:.2f}',
    f'{vix["change_pct"]:+.2f}%',
)


st.write(
    "**Equity Signal:**",
    market_analysis["sentiment"],
)


# ==================================================
# LABOR MARKET
# ==================================================

st.divider()

st.subheader("👷 Labor Market")

l1, l2, l3 = st.columns(3)


l1.metric(
    "Non-Farm Payrolls",
    f"{nfp_actual:+.0f}K",
    f"Forecast: {nfp_forecast:.0f}K",
)


l2.metric(
    "Unemployment Rate",
    f"{unemployment_actual:.1f}%",
    f"Forecast: {unemployment_forecast:.1f}%",
)


l3.metric(
    "Hourly Earnings MoM",
    f"{wage_actual:+.2f}%",
    f"Forecast: {wage_forecast:.1f}%",
)


st.write(
    "**Labor Signal:**",
    labor_analysis["signal"],
)


with st.expander(
    "Why did MacroPulse generate this labor signal?"
):

    for reason in labor_analysis["reasons"]:
        st.write("•", reason)


# ==================================================
# FED EXPECTATIONS
# ==================================================

st.divider()

st.subheader("🏦 Fed Expectations")

f1, f2, f3 = st.columns(3)


f1.metric(
    "Hold",
    f'{fed_data["hold"]["current"]:.1f}%',
    f'{fed_data["hold"]["change"]:+.1f} pp',
)


f2.metric(
    "Hike",
    f'{fed_data["hike"]["current"]:.1f}%',
    f'{fed_data["hike"]["change"]:+.1f} pp',
)


f3.metric(
    "Cut",
    f'{fed_data["cut"]["current"]:.1f}%',
    f'{fed_data["cut"]["change"]:+.1f} pp',
)


st.write(
    "**Fed Signal:**",
    fed_analysis["signal"],
)


with st.expander(
    "Why did MacroPulse generate this Fed signal?"
):

    for reason in fed_analysis["reasons"]:
        st.write("•", reason)


# ==================================================
# TREASURY YIELDS
# ==================================================

st.divider()

st.subheader("💵 Treasury Yields")

t1, t2, t3 = st.columns(3)


two_year = treasury_data["2Y"]
five_year = treasury_data["5Y"]
ten_year = treasury_data["10Y"]


if two_year:

    t1.metric(
        "2-Year",
        f'{two_year["yield"]:.2f}%',
        f'{two_year["change_bps"]:+.1f} bps',
    )

else:

    t1.metric(
        "2-Year",
        "No Data",
    )


if five_year:

    t2.metric(
        "5-Year",
        f'{five_year["yield"]:.2f}%',
        f'{five_year["change_bps"]:+.1f} bps',
    )

else:

    t2.metric(
        "5-Year",
        "No Data",
    )


if ten_year:

    t3.metric(
        "10-Year",
        f'{ten_year["yield"]:.2f}%',
        f'{ten_year["change_bps"]:+.1f} bps',
    )

else:

    t3.metric(
        "10-Year",
        "No Data",
    )


st.write(
    "**Rates Signal:**",
    rates_analysis["signal"],
)


with st.expander(
    "Treasury signal details"
):

    for reason in rates_analysis["reasons"]:
        st.write("•", reason)


# ==================================================
# MACRO SIGNAL SUMMARY
# ==================================================

st.divider()

st.subheader("🧠 Macro Signals")

s1, s2, s3, s4 = st.columns(4)


s1.metric(
    "Labor",
    labor_analysis["signal"],
)


s2.metric(
    "Fed",
    fed_analysis["signal"],
)


s3.metric(
    "Equities",
    market_analysis["sentiment"],
)


s4.metric(
    "Rates",
    rates_analysis["signal"],
)


# ==================================================
# DOMINANT NARRATIVE
# ==================================================

st.divider()

st.subheader("🎯 Dominant Macro Narrative")

st.header(
    narrative["narrative"]
)


# --------------------------------------------------
# NARRATIVE SCORES
# --------------------------------------------------

if narrative["scores"]:

    st.write(
        f'**Signal Agreement: '
        f'{narrative["agreement"]}%**'
    )

    st.write("### Narrative Scores")

    n1, n2, n3, n4 = st.columns(4)


    n1.metric(
        "Fed Relief",
        narrative["scores"][
            "FED RELIEF"
        ],
    )


    n2.metric(
        "Growth Fear",
        narrative["scores"][
            "GROWTH FEAR"
        ],
    )


    n3.metric(
        "Hawkish Pressure",
        narrative["scores"][
            "HAWKISH PRESSURE"
        ],
    )


    n4.metric(
        "Strong Growth",
        narrative["scores"][
            "STRONG GROWTH"
        ],
    )


# --------------------------------------------------
# EVIDENCE
# --------------------------------------------------

st.write("### Evidence")

for item in narrative["evidence"]:
    st.write(
        "•",
        item,
    )


# ==================================================
# DATA QUALITY
# ==================================================

st.divider()

st.subheader("🔎 Data Quality")


dq1, dq2 = st.columns(2)


dq1.metric(
    "Treasury Data Status",
    freshness["status"],
)


dq2.metric(
    "Treasury Data Age",
    f'{freshness.get("age_days", "Unknown")} day(s)',
)


st.write(
    "**Latest Treasury observation:**",
    freshness["latest_date"],
)


# --------------------------------------------------
# STALE DATA WARNING
# --------------------------------------------------

if freshness["status"] == "STALE":

    st.warning(
        "Treasury data is stale. "
        "MacroPulse will not generate a "
        "current cross-asset narrative until "
        "fresh Treasury data is available."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "MacroPulse is an analytical research dashboard. "
    "Signals describe market conditions and are not "
    "buy or sell recommendations."
)
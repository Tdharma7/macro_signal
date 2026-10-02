import streamlit as st

from src.market_data import get_market_snapshot
from src.treasury_data import get_treasury_yields
from src.signal_engine import (
    analyze_market,
    analyze_rates,
    analyze_narrative
)
from src.data_quality import check_treasury_freshness
from src.labor_data import (
    get_bls_labor_data,
    calculate_payroll_change,
    calculate_wage_change
)

from src.signal_engine import analyze_labor

st.set_page_config(
    page_title="MacroPulse",
    page_icon="📈",
    layout="wide"
)

st.title("MacroPulse")
st.caption("Cross-asset macro signal dashboard")

with st.sidebar:

    st.header("Market Expectations")

    nfp_forecast = st.number_input(
        "NFP Forecast (K)",
        value=90.0,
        step=10.0
    )

    unemployment_forecast = st.number_input(
        "Unemployment Forecast (%)",
        value=4.1,
        step=0.1,
        format="%.1f"
    )

    wage_forecast = st.number_input(
        "Hourly Earnings Forecast MoM (%)",
        value=0.3,
        step=0.1,
        format="%.1f"
    )




# -------------------------
# LOAD DATA
# -------------------------

market_data = get_market_snapshot()
treasury_data = get_treasury_yields()


labor_data = get_bls_labor_data()

nfp_actual = calculate_payroll_change(labor_data)
wage_actual = calculate_wage_change(labor_data)

unemployment_actual = (
    labor_data["unemployment_rate"]["latest"]
)



# -------------------------
# ANALYSIS
# -------------------------

market_analysis = analyze_market(market_data)
rates_analysis = analyze_rates(treasury_data)

freshness = check_treasury_freshness(treasury_data)
labor_analysis = analyze_labor(
    actual_nfp=nfp_actual,
    forecast_nfp=nfp_forecast,
    actual_unemployment=unemployment_actual,
    forecast_unemployment=unemployment_forecast,
    actual_wages=wage_actual,
    forecast_wages=wage_forecast
)

# Only trust narrative if rates are fresh enough
if freshness["status"] in ["CURRENT", "RECENT"]:

    narrative = analyze_narrative(
        market_analysis,
        rates_analysis
    )

else:

    narrative = {
        "narrative": "INSUFFICIENT CURRENT DATA",
        "explanation": (
            "Treasury data is stale, so MacroPulse will not "
            "infer a current cross-market narrative."
        )
    }


# -------------------------
# EQUITIES
# -------------------------

st.subheader("Equity Markets")

col1, col2, col3 = st.columns(3)

sp500 = market_data["S&P 500"]
nasdaq = market_data["Nasdaq"]
vix = market_data["VIX"]

col1.metric(
    "S&P 500",
    sp500["value"],
    f'{sp500["change_pct"]:+.2f}%'
)

col2.metric(
    "Nasdaq",
    nasdaq["value"],
    f'{nasdaq["change_pct"]:+.2f}%'
)

col3.metric(
    "VIX",
    vix["value"],
    f'{vix["change_pct"]:+.2f}%'
)


# -------------------------
# TREASURIES
# -------------------------

st.subheader("Treasury Yields")

t1, t2, t3 = st.columns(3)

two_year = treasury_data["2Y"]
five_year = treasury_data["5Y"]
ten_year = treasury_data["10Y"]

t1.metric(
    "2-Year",
    f'{two_year["yield"]:.2f}%',
    f'{two_year["change_bps"]:+.1f} bps'
)

t2.metric(
    "5-Year",
    f'{five_year["yield"]:.2f}%',
    f'{five_year["change_bps"]:+.1f} bps'
)

t3.metric(
    "10-Year",
    f'{ten_year["yield"]:.2f}%',
    f'{ten_year["change_bps"]:+.1f} bps'
)


# -------------------------
# SIGNALS
# -------------------------

st.subheader("Macro Signals")

s1, s2, s3 = st.columns(3)

s1.metric(
    "Equity Sentiment",
    market_analysis["sentiment"]
)

s2.metric(
    "Rates Signal",
    rates_analysis["signal"]
)

s3.metric(
    "Data Quality",
    freshness["status"]
)


# -------------------------
# NARRATIVE
# -------------------------

st.divider()

st.subheader("Dominant Narrative")

st.header(narrative["narrative"])

st.write(narrative["explanation"])


# -------------------------
# DATA QUALITY
# -------------------------

st.divider()

st.subheader("Data Freshness")

st.write(
    f'Treasury latest observation: '
    f'{freshness["latest_date"]}'
)

st.write(
    f'Treasury data age: '
    f'{freshness.get("age_days", "Unknown")} day(s)'
)


from market_data import get_market_snapshot
from treasury_data import get_treasury_yields
from signal_engine import (
    analyze_market,
    analyze_rates,
    analyze_narrative
)


def main():

    # 1. Collect data
    market_data = get_market_snapshot()
    treasury_data = get_treasury_yields()

    # 2. Analyze individual markets
    market_analysis = analyze_market(market_data)
    rates_analysis = analyze_rates(treasury_data)

    # 3. Combine signals
    narrative = analyze_narrative(
        market_analysis,
        rates_analysis
    )

    print("\n========== MACROPULSE ==========")

    print("\nEQUITY SIGNAL")
    print(market_analysis["sentiment"])

    for reason in market_analysis["reasons"]:
        print(" -", reason)

    print("\nRATES SIGNAL")
    print(rates_analysis["signal"])

    for reason in rates_analysis["reasons"]:
        print(" -", reason)

    print("\nDOMINANT NARRATIVE")
    print(narrative["narrative"])

    print("\nINTERPRETATION")
    print(narrative["explanation"])

    print("\n===============================")


if __name__ == "__main__":
    main()
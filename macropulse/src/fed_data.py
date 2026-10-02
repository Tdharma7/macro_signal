# Fetch Federal Reserve data
def build_fed_data(
    previous_hold,
    current_hold,
    previous_hike,
    current_hike,
    previous_cut=0.0,
    current_cut=0.0,
):
    """
    Build a structured dictionary containing
    previous and current FedWatch probabilities.
    """

    return {
        "hold": {
            "previous": previous_hold,
            "current": current_hold,
            "change": round(
                current_hold - previous_hold,
                2
            ),
        },

        "hike": {
            "previous": previous_hike,
            "current": current_hike,
            "change": round(
                current_hike - previous_hike,
                2
            ),
        },

        "cut": {
            "previous": previous_cut,
            "current": current_cut,
            "change": round(
                current_cut - previous_cut,
                2
            ),
        },
    }


# -----------------------------------------
# TEST
# -----------------------------------------

if __name__ == "__main__":

    fed_data = build_fed_data(
        previous_hold=75.6,
        current_hold=81.7,
        previous_hike=24.4,
        current_hike=18.3,
        previous_cut=0.0,
        current_cut=0.0,
    )

    print(fed_data)
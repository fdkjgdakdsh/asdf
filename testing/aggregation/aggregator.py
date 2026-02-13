import numpy as np
from collections import defaultdict

def aggregate_exposure(chain, greek, exposure_mode):
    calls = chain["calls"]
    puts  = chain["puts"]

    # grid[(dte, strike)] = {"call": x, "put": y}
    grid = defaultdict(lambda: {"call": 0.0, "put": 0.0})

    # --- Collect CALL exposure ---
    for contract in calls:
        strike = int(contract["strikePrice"])
        dte = int(contract["daysToExpiration"])
        exposure = float(contract[f"{greek} exposure"])
        grid[(dte, strike)]["call"] += exposure

    # --- Collect PUT exposure ---
    for contract in puts:
        strike = int(contract["strikePrice"])
        dte = int(contract["daysToExpiration"])
        exposure = float(contract[f"{greek} exposure"])
        grid[(dte, strike)]["put"] += exposure

    # --- Axes ---
    dtes = sorted({k[0] for k in grid.keys()})
    strikes = sorted({k[1] for k in grid.keys()})

    dte_index = {d: i for i, d in enumerate(dtes)}
    strike_index = {s: i for i, s in enumerate(strikes)}

    matrix = np.zeros((len(dtes), len(strikes)))

    # --- Aggregate ---
    for (dte, strike), v in grid.items():
        c = v["call"]
        p = v["put"]

        if exposure_mode.lower() == "net":
            value = abs(c) - abs(p)
            
        elif exposure_mode.lower() == "absolute":
            value = abs(c) + abs(p)
        else:
            raise ValueError("exposure_mode must be 'Net' or 'Absolute'")

        i = dte_index[dte]
        j = strike_index[strike]
        matrix[i, j] = value

    return {
        "underlying": chain["underlying_price"],
        "dtes": dtes,
        "strikes": strikes,
        "matrix": matrix
    }

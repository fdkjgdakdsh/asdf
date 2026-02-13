import math
from scipy.stats import norm
from utils.time_utils import time_to_expiry_years

def bs_price(S, K, T, r, q, sigma, option_type):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "call":
        return S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    else:
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)

def to_py_float(x):
    return float(x) if hasattr(x, "item") else x


def bs_greeks(S, K, T, r, q, sigma, option_type):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    pdf = norm.pdf(d1)

    delta = (
        math.exp(-q * T) * norm.cdf(d1)
        if option_type == "call"
        else -math.exp(-q * T) * norm.cdf(-d1)
    )

    gamma = math.exp(-q * T) * pdf / (S * sigma * math.sqrt(T))
    vega = S * math.exp(-q * T) * pdf * math.sqrt(T)

    theta = (
        -S * pdf * sigma * math.exp(-q * T) / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2)
        + q * S * math.exp(-q * T) * norm.cdf(d1 if option_type == "call" else -d1)
    )

    return delta, gamma, vega, theta


def implied_volatility(price, S, K, T, r, q, option_type):
    low, high = 1e-6, 5.0  # 500% IV max
    for _ in range(100):
        mid = (low + high) / 2
        p = bs_price(S, K, T, r, q, mid, option_type)

        if abs(p - price) < 1e-6:
            return mid

        if p > price:
            high = mid
        else:
            low = mid

    return (low + high) / 2


def charm(S, K, T, r, q, sigma, option_type):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    pdf = norm.pdf(d1)

    if option_type == "call":
        return (-pdf * (2*(r - q)*T - d2*sigma*math.sqrt(T)) / (2*T*sigma*math.sqrt(T))
                - q * math.exp(-q*T) * norm.cdf(d1))
    else:
        return (-pdf * (2*(r - q)*T - d2*sigma*math.sqrt(T)) / (2*T*sigma*math.sqrt(T))
                + q * math.exp(-q*T) * norm.cdf(-d1))


def vanna(S, K, T, r, q, sigma):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    pdf = norm.pdf(d1)

    return math.exp(-q*T) * pdf * (d2 / sigma)


def enrich_chain(chain, r, q, greek):
    S = chain["underlying_price"]

    def compute_greek(S, K, T, r, q, sigma, option_type, greek):
        if greek == "Delta":
            return bs_greeks(S, K, T, r, q, sigma, option_type)[0]
        if greek == "Gamma":
            return bs_greeks(S, K, T, r, q, sigma, option_type)[1]
        if greek == "Vega":
            return bs_greeks(S, K, T, r, q, sigma, option_type)[2]
        if greek == "Theta":
            return bs_greeks(S, K, T, r, q, sigma, option_type)[3]
        if greek == "Charm":
            return charm(S, K, T, r, q, sigma, option_type)
        if greek == "Vanna":
            return vanna(S, K, T, r, q, sigma)
        return None

    def enrich(contract, option_type):
        bid = contract["bid"]
        ask = contract["ask"]

        if bid <= 0 or ask <= 0 or ask < bid:
            return None

        mid = (bid + ask) / 2
        
        T = time_to_expiry_years(contract["expirationDate"])
        K = contract["strikePrice"]

        iv = implied_volatility(mid, S, K, T, r, q, option_type)
        if iv is None:
            return None

        greek_value = compute_greek(S, K, T, r, q, iv, option_type, greek)
        if greek_value is None:
            return None
        
        if greek == "Gamma":
            exposure = greek_value * S**2 * contract["openInterest"] * 100
        else:
            exposure = greek_value * contract["openInterest"] * 100

        return {
            **contract,
            greek + " exposure": float(exposure),
            "impliedVolatility": float(iv),
        }

    calls = filter(None, (enrich(c, "call") for c in chain["calls"]))
    puts  = filter(None, (enrich(p, "put") for p in chain["puts"]))

    return {
        "underlying_price": S,
        "calls": list(calls),
        "puts": list(puts),
    }


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
    

    def enrich(contract, option_type):
        bid = contract["bid"]
        ask = contract["ask"]
        
        iv = contract["volatility"]/100
        if bid <= 0 or ask <= 0 or ask < bid:
            return None

        mid = (bid + ask) / 2
        S = chain["underlying_price"]
        T = time_to_expiry_years(contract["expirationDate"])
        K = contract["strikePrice"]
        def greek_exposure(contract, greek):
            if greek == "Delta": 
                return contract["delta"] * contract["openInterest"] * 100
            if greek == "Gamma":
                return contract["gamma"] * S**2 * contract["openInterest"] * 100
            if greek == "Vega":
                return contract["vega"] * 0.01 * contract["openInterest"] * 100
            if greek == "Theta":
                return contract["theta"] / 365 * contract["openInterest"] * 100
            if greek == "Charm":
                return charm(S, K, T, r, q, iv, option_type) * contract["openInterest"] * 100
            if greek == "Vanna":
                return vanna(S, K, T, r, q, iv) * contract["openInterest"] * 100
            return None
        greek_value = greek_exposure(contract, greek)
        return {
            **contract,
            greek + " exposure": greek_value,
            "impliedVolatility": float(iv),
        }

    calls = filter(None, (enrich(c, "call") for c in chain["calls"]))
    puts  = filter(None, (enrich(p, "put") for p in chain["puts"]))

    return {
        "underlying_price": chain["underlying_price"],
        "calls": list(calls),
        "puts": list(puts),
    }

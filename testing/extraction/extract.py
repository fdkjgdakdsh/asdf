FIELDS = [
    "strikePrice",
    "daysToExpiration",
    "openInterest",
    "bid",
    "ask",
    "expirationDate",
    "volatility",
    "gamma",
    "delta",
    "theta",
    "vega",
]

# ② Small helper: extract only those fields from ONE contract
def extract_contract(contract: dict) -> dict:
    return {field: contract[field] for field in FIELDS}
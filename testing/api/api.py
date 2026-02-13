import schwabdev
from datetime import datetime
from extraction.extract import extract_contract
#from exposure.enrich import enrich_chain
from exposure.bs_api import enrich_chain
client = schwabdev.Client(
    "CVNi8j7CA8LyENAmresfuoptHMXFVUezAeXY24MFa2UwDXPp",
    "sXblFQ3cP7Rd6ZYbC8QbTQA0sJ7sbGwjVZctjmvSHweGEBHT8eBt1mg7VmjFntGb"
)

date = datetime.now().date().isoformat()


def fetch_options(ticker: str, strike: int, date_end: str, greek: str):
    data = client.option_chains(
        ticker,
        strikeCount=strike,
        contractType="ALL",
        fromDate=date,
        toDate=date_end
    ).json()

    # basic data
    underlying_price = data["underlyingPrice"]
    div_yield = data["dividendYield"]
    def underlying():
        return underlying_price
    # risk-free rate (SOFR)
    r = 0.0366

    # build raw chain
    call_chain = data["callExpDateMap"]
    put_chain = data["putExpDateMap"]

    call_contracts = []
    put_contracts = []

    for exp_key, strikes in call_chain.items():
        for strike_key, contract_list in strikes.items():
            contract = contract_list[0]
            call_contracts.append(extract_contract(contract))

    for exp_key, strikes in put_chain.items():
        for strike_key, contract_list in strikes.items():
            contract = contract_list[0]
            put_contracts.append(extract_contract(contract))

    raw_chain = {
        "underlying_price": underlying_price,
        "calls": call_contracts,
        "puts": put_contracts,
    }
    
    # enrich chain using BS engine
    enriched = enrich_chain(raw_chain, r, div_yield, greek)

    return enriched
    
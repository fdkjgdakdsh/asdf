import streamlit as st
import pandas as pd
from datetime import datetime
date = datetime.now().date().isoformat()
from api.api import fetch_options
from aggregation.aggregator import aggregate_exposure
from visuals.visuals import show_heatmap, build_dataframe_from_chain

st.title("stock data")

ticker = st.sidebar.text_input("Enter Stock Ticker", "QQQ")
greek = st.sidebar.selectbox("Select Greek", ["Delta", "Gamma", "Theta", "Vega", "Charm", "Vanna", "iv"])
strike = st.sidebar.number_input("enter strike count", min_value=1)
date_end = st.sidebar.text_input("input end date (dte), format YYYY-MM-DD", date)
exposure_mode = st.sidebar.selectbox("Exposure Mode", ["Net", "Absolute"])


if st.button("Get Stock Data"):
    # 1) Fetch chain data
    chain = fetch_options(ticker, strike, date_end, greek)
    
    # 2) Aggregate into grid
    agg = aggregate_exposure(chain, greek, exposure_mode)
    df = build_dataframe_from_chain(chain, greek, exposure_mode)
    # 3) Display heatmap
    show_heatmap(df, exposure_mode)



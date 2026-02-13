import pandas as pd
import streamlit as st
from aggregation.aggregator import aggregate_exposure

def format_number(x):
    if x is None:
        return ""
    x = float(x)
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:.2f}k"
    return f"{x:.0f}"

def build_dataframe_from_chain(chain, greek, exposure_mode):
    # Delegate aggregation to the corrected aggregator
    agg_result = aggregate_exposure(chain, greek, exposure_mode)
    
    # agg_result["matrix"] is shape (n_dtes, n_strikes)
    # We want rows=strikes, columns=dtes
    matrix = agg_result["matrix"]
    dtes = agg_result["dtes"]
    strikes = agg_result["strikes"]
    
    # create DataFrame: index=dtes, columns=strikes
    df_dtes_rows = pd.DataFrame(matrix, index=dtes, columns=strikes)
    
    # Transpose to get index=strikes, columns=dtes
    return df_dtes_rows.T

def show_heatmap(df, exposure_mode):
    if exposure_mode == "Net":
        # Calculate symmetric limit for centering at 0
        # Use a small epsilon to avoid error if all values are 0
        limit = max(abs(df.min().min()), abs(df.max().max()))
        if limit == 0:
            limit = 1.0

        styled = (
            df.style
            .background_gradient(cmap="RdBu", vmin=-limit, vmax=limit, axis=None)
            .format(format_number)
            .set_properties(**{"font-weight": "bold"})
        )
    else:
        styled = (
            df.style
            .background_gradient(cmap="Purples", axis=None)
            .format(format_number)
            .set_properties(**{"font-weight": "bold"})
        )

    st.dataframe(styled)

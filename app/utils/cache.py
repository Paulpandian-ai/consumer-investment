"""Caching utilities for the Factor Impact Intelligence app."""

import streamlit as st


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str) -> dict:
    """Cache yfinance data to reduce API calls (1 hour TTL)."""
    import yfinance as yf

    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period='1y')

    return {
        'info': info,
        'history_dates': hist.index.strftime('%Y-%m-%d').tolist(),
        'history_close': hist['Close'].tolist(),
    }


@st.cache_data(ttl=86400)
def get_macro_data() -> dict:
    """Cache FRED macro data (24 hour TTL)."""
    try:
        from fredapi import Fred

        api_key = st.secrets.get('FRED_API_KEY', '')
        if not api_key:
            return _default_macro_data()

        fred = Fred(api_key=api_key)
        fed_rate = fred.get_series('FEDFUNDS').iloc[-1]
        cpi = fred.get_series('CPIAUCSL').pct_change(12).iloc[-1] * 100
        ten_year = fred.get_series('DGS10').iloc[-1]

        return {
            'fed_rate': float(fed_rate),
            'cpi': float(cpi),
            'ten_year': float(ten_year),
        }
    except Exception:
        return _default_macro_data()


def _default_macro_data() -> dict:
    """Return sensible defaults when FRED is unavailable."""
    return {
        'fed_rate': 5.25,
        'cpi': 3.2,
        'ten_year': 4.5,
    }


@st.cache_data(ttl=3600)
def get_ai_summary(ticker: str, factor: str, data_hash: str) -> str:
    """Cache AI-generated summaries (1 hour TTL)."""
    from app.analysis.llm_reasoning import generate_factor_summary

    return generate_factor_summary(ticker, factor, data_hash)

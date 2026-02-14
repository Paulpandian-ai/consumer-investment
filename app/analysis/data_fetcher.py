"""Data fetching utilities for stock and macro data."""

import yfinance as yf
import pandas as pd
import streamlit as st


def fetch_stock_info(ticker: str) -> dict:
    """Fetch basic stock info from yfinance."""
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        st.warning(f"Could not fetch data for {ticker}: {e}")
        return {}


def fetch_stock_history(ticker: str, period: str = '1y') -> pd.DataFrame:
    """Fetch historical price data."""
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period=period)
    except Exception:
        return pd.DataFrame()


def fetch_peer_history(tickers: list, period: str = '6mo') -> dict:
    """Fetch historical data for multiple tickers (for correlation analysis)."""
    results = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period=period)
            if not hist.empty:
                results[t] = hist['Close']
        except Exception:
            continue
    return results


def get_sector_etf(sector: str) -> str:
    """Map sector name to the corresponding SPDR sector ETF."""
    sector_etfs = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financial Services': 'XLF',
        'Financials': 'XLF',
        'Consumer Cyclical': 'XLY',
        'Consumer Defensive': 'XLP',
        'Energy': 'XLE',
        'Industrials': 'XLI',
        'Basic Materials': 'XLB',
        'Real Estate': 'XLRE',
        'Utilities': 'XLU',
        'Communication Services': 'XLC',
    }
    return sector_etfs.get(sector, 'SPY')


def get_sector_peers(ticker: str, sector: str) -> list:
    """Return a list of peer tickers in the same sector."""
    sector_peers = {
        'Technology': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'AVGO', 'INTC', 'GOOGL', 'META', 'CRM', 'ORCL'],
        'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'BMY', 'AMGN'],
        'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB'],
        'Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB'],
        'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'NKE', 'MCD', 'SBUX', 'LOW', 'TGT', 'BKNG', 'CMG'],
        'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'PM', 'CL', 'MDLZ', 'MO', 'GIS'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL'],
        'Industrials': ['CAT', 'BA', 'HON', 'UPS', 'RTX', 'DE', 'GE', 'MMM', 'LMT', 'UNP'],
        'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS', 'ATVI', 'EA'],
    }
    peers = sector_peers.get(sector, ['SPY', 'QQQ', 'DIA'])
    # Exclude the stock itself
    return [p for p in peers if p != ticker][:5]

"""Analyze page - Deep single-stock analysis."""

import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(page_title="Analyze | Factor Impact Intelligence", page_icon="\U0001f50d", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #1E1E1E; }
    .block-container { padding-top: 2rem; }
    .stButton > button {
        background: linear-gradient(135deg, #00C805, #00A804);
        color: white; border: none; border-radius: 12px;
        padding: 12px 24px; font-weight: 600;
    }
    .stTextInput > div > div > input {
        background: #2A2A2A; border: 1px solid #3A3A3A;
        border-radius: 12px; color: white; padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

from app.analysis.factor_engine import analyze_stock
from app.components.risk_weather import render_risk_weather
from app.components.signal_badge import render_signal
from app.components.factor_cards import render_all_factor_cards
from app.components.alternatives import render_alternatives
from app.components.charts import render_simple_chart, render_price_header
from app.utils.cache import get_stock_data

st.title("\U0001f50d Analyze a Stock")
st.caption("Get a full 6-factor breakdown for any stock")

ticker = st.text_input(
    "",
    placeholder="Enter a ticker symbol (e.g., NVDA)",
    key="analyze_ticker",
    label_visibility="collapsed",
)

if ticker:
    ticker_clean = ticker.strip().upper()

    with st.spinner(f"Running 6-factor analysis on {ticker_clean}..."):
        results = analyze_stock(ticker_clean)

    # Price + chart
    render_price_header(results['ticker'], results['name'], results['price'], results['change_pct'])

    try:
        stock_data = get_stock_data(ticker_clean)
        if stock_data['history_dates']:
            # Time period selector
            period_options = {'1M': -21, '3M': -63, '6M': -126, '1Y': None}
            period = st.radio("Period", list(period_options.keys()), horizontal=True, index=3)
            sl = period_options[period]
            dates = stock_data['history_dates'][sl:] if sl else stock_data['history_dates']
            values = stock_data['history_close'][sl:] if sl else stock_data['history_close']
            render_simple_chart(dates, values, height=250)
    except Exception:
        pass

    st.markdown("---")

    # Weather + Signal side by side
    col_w, col_s = st.columns(2)
    with col_w:
        render_risk_weather(results['composite_score'], results['factors'])
    with col_s:
        render_signal(results['signal'], results['confidence'], results['reasoning'])

    st.markdown("---")

    # Full factor breakdown
    st.markdown("### \U0001f4ca Detailed Factor Breakdown")
    render_all_factor_cards(results['factors'])

    # Alternatives
    if results['signal'] != 'BUY' and results['alternatives']:
        st.markdown("---")
        render_alternatives(ticker_clean, results['signal'], results['alternatives'])

else:
    st.markdown(
        """
        <div style="text-align: center; padding: 80px 20px; color: #9B9B9B;">
            <div style="font-size: 48px; margin-bottom: 16px;">\U0001f50d</div>
            <div style="font-size: 18px;">Type a ticker symbol above to start your analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

"""Home page - Portfolio overview and Risk Weather."""

import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(page_title="Home | Factor Impact Intelligence", page_icon="\U0001f3e0", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #1E1E1E; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

from app.analysis.factor_engine import analyze_stock
from app.components.risk_weather import render_risk_weather
from app.components.signal_badge import render_signal
from app.components.charts import render_simple_chart, render_price_header
from app.utils.cache import get_stock_data

st.title("\U0001f3e0 Home")
st.caption("Your portfolio overview")

# Watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['AAPL', 'NVDA', 'MSFT']

# Add to watchlist
with st.expander("Edit watchlist"):
    new_ticker = st.text_input("Add a ticker", placeholder="e.g., TSLA")
    col_add, col_clear = st.columns(2)
    with col_add:
        if st.button("Add", use_container_width=True) and new_ticker:
            cleaned = new_ticker.strip().upper()
            if cleaned not in st.session_state.watchlist:
                st.session_state.watchlist.append(cleaned)
                st.rerun()
    with col_clear:
        if st.button("Clear all", use_container_width=True):
            st.session_state.watchlist = []
            st.rerun()

# Display watchlist cards
if not st.session_state.watchlist:
    st.info("Your watchlist is empty. Add some tickers above!")
else:
    for t in st.session_state.watchlist:
        with st.container():
            st.markdown(f"#### {t}")
            try:
                with st.spinner(f"Loading {t}..."):
                    results = analyze_stock(t)

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    render_price_header(results['ticker'], results['name'], results['price'], results['change_pct'])

                with col2:
                    render_risk_weather(results['composite_score'], results['factors'])

                with col3:
                    render_signal(results['signal'], results['confidence'], results['reasoning'])

                # Mini chart
                try:
                    stock_data = get_stock_data(t)
                    if stock_data['history_dates']:
                        render_simple_chart(stock_data['history_dates'], stock_data['history_close'], height=120)
                except Exception:
                    pass

            except Exception as e:
                st.error(f"Could not load {t}: {e}")

            st.markdown("---")

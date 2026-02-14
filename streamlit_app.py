"""Factor Impact Intelligence - Consumer-friendly stock analysis app.

Root-level entry point for Streamlit Cloud deployment.
Run with: streamlit run streamlit_app.py
"""

import sys
import os

# Ensure the project root is on sys.path so `app.*` imports work.
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

# ---------------------------------------------------------------------------
# Page config (MUST be the first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Factor Impact Intelligence",
    page_icon="\U0001f3af",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Dark mode */
    .stApp {
        background-color: #1E1E1E;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00C805, #00A804);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        color: white;
    }

    /* Text input */
    .stTextInput > div > div > input {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        color: white;
        padding: 12px 16px;
    }

    /* Reduce default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background: #2A2A2A;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Imports (after path setup)
# ---------------------------------------------------------------------------
from app.analysis.factor_engine import analyze_stock
from app.components.risk_weather import render_risk_weather
from app.components.signal_badge import render_signal
from app.components.factor_cards import render_all_factor_cards
from app.components.alternatives import render_alternatives
from app.components.charts import render_simple_chart, render_price_header
from app.utils.cache import get_stock_data

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("\U0001f3af Factor Impact Intelligence")
st.caption("Know what moves your stocks")

# ---------------------------------------------------------------------------
# Trending stock callback
# ---------------------------------------------------------------------------
def _select_trending(symbol: str):
    """Set the selected ticker from a trending button click."""
    st.session_state['selected_ticker'] = symbol

# ---------------------------------------------------------------------------
# Search bar
# ---------------------------------------------------------------------------
default_value = st.session_state.pop('selected_ticker', '')
ticker = st.text_input(
    "",
    value=default_value,
    placeholder="Search any stock (e.g., NVDA, AAPL, TSLA)",
    key="ticker_search",
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Analysis view
# ---------------------------------------------------------------------------
if ticker:
    ticker_clean = ticker.strip().upper()

    with st.spinner(f"Analyzing {ticker_clean} across 6 factors..."):
        results = analyze_stock(ticker_clean)

    # Price header
    render_price_header(
        results['ticker'],
        results['name'],
        results['price'],
        results['change_pct'],
    )

    # Price chart
    try:
        stock_data = get_stock_data(ticker_clean)
        if stock_data['history_dates']:
            render_simple_chart(stock_data['history_dates'], stock_data['history_close'])
    except Exception:
        pass

    st.markdown("---")

    # Two-column layout: weather + signal
    col_weather, col_signal = st.columns(2)

    with col_weather:
        render_risk_weather(results['composite_score'], results['factors'])

    with col_signal:
        render_signal(results['signal'], results['confidence'], results['reasoning'])

    st.markdown("---")

    # Factor cards
    st.markdown("### \U0001f4ca Factor Breakdown")
    render_all_factor_cards(results['factors'])

    # Alternatives
    if results['signal'] != 'BUY' and results['alternatives']:
        st.markdown("---")
        render_alternatives(ticker_clean, results['signal'], results['alternatives'])

else:
    # Empty / landing state
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 60px 20px;
            color: #9B9B9B;
        ">
            <div style="font-size: 48px; margin-bottom: 20px;">\U0001f50d</div>
            <div style="font-size: 20px; margin-bottom: 8px;">Enter a stock symbol above</div>
            <div style="font-size: 14px;">
                Get instant factor analysis with Buy/Hold/Sell signals
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Trending stocks
    st.markdown("### \U0001f525 Trending Analysis")
    trending = ['NVDA', 'AAPL', 'TSLA', 'MSFT', 'AMD']
    cols = st.columns(len(trending))
    for i, t in enumerate(trending):
        with cols[i]:
            st.button(
                t,
                key=f"trending_{t}",
                use_container_width=True,
                on_click=_select_trending,
                args=(t,),
            )

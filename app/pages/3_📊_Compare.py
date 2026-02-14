"""Compare page - Side-by-side stock comparison."""

import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(page_title="Compare | Factor Impact Intelligence", page_icon="\U0001f4ca", layout="wide")

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
from app.components.factor_cards import render_factor_card, FACTOR_CONFIG, get_traffic_light
from app.components.charts import render_price_header

st.title("\U0001f4ca Compare Stocks")
st.caption("See how two stocks stack up across all 6 factors")

col_left, col_right = st.columns(2)

with col_left:
    ticker_a = st.text_input("Stock A", placeholder="e.g., NVDA", key="compare_a")

with col_right:
    ticker_b = st.text_input("Stock B", placeholder="e.g., AMD", key="compare_b")

if ticker_a and ticker_b:
    ta = ticker_a.strip().upper()
    tb = ticker_b.strip().upper()

    with st.spinner(f"Comparing {ta} vs {tb}..."):
        results_a = analyze_stock(ta)
        results_b = analyze_stock(tb)

    # Side-by-side header
    col1, col2 = st.columns(2)

    with col1:
        render_price_header(results_a['ticker'], results_a['name'], results_a['price'], results_a['change_pct'])
        render_risk_weather(results_a['composite_score'], results_a['factors'])
        st.markdown("")
        render_signal(results_a['signal'], results_a['confidence'], results_a['reasoning'])

    with col2:
        render_price_header(results_b['ticker'], results_b['name'], results_b['price'], results_b['change_pct'])
        render_risk_weather(results_b['composite_score'], results_b['factors'])
        st.markdown("")
        render_signal(results_b['signal'], results_b['confidence'], results_b['reasoning'])

    st.markdown("---")

    # Factor-by-factor comparison
    st.markdown("### Factor-by-Factor Comparison")

    factor_keys = ['supply_chain', 'customers', 'geopolitical', 'monetary', 'correlation', 'performance']

    for key in factor_keys:
        config = FACTOR_CONFIG[key]
        fa = results_a['factors'][key]
        fb = results_b['factors'][key]

        light_a, status_a, color_a = get_traffic_light(fa['score'])
        light_b, status_b, color_b = get_traffic_light(fb['score'])

        st.markdown(
            f"""
            <div style="
                background: #2A2A2A;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 10px;
            ">
                <div style="text-align: center; font-size: 16px; font-weight: 600; color: #FFFFFF; margin-bottom: 12px;">
                    {config['icon']} {config['label']}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 18px; font-weight: 700; color: {color_a};">
                            {light_a} {status_a}
                        </div>
                        <div style="font-size: 13px; color: #9B9B9B; margin-top: 4px;">
                            {ta}: {fa['score']:+.1f}
                        </div>
                        <div style="font-size: 12px; color: #CCCCCC; margin-top: 4px;">
                            {fa['summary']}
                        </div>
                    </div>
                    <div style="width: 1px; height: 60px; background: #3A3A3A; margin: 0 16px;"></div>
                    <div style="text-align: center; flex: 1;">
                        <div style="font-size: 18px; font-weight: 700; color: {color_b};">
                            {light_b} {status_b}
                        </div>
                        <div style="font-size: 13px; color: #9B9B9B; margin-top: 4px;">
                            {tb}: {fb['score']:+.1f}
                        </div>
                        <div style="font-size: 12px; color: #CCCCCC; margin-top: 4px;">
                            {fb['summary']}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Winner summary
    st.markdown("---")
    winner = ta if results_a['composite_score'] >= results_b['composite_score'] else tb
    winner_score = max(results_a['composite_score'], results_b['composite_score'])
    st.markdown(
        f"""
        <div style="
            text-align: center;
            background: #00C80515;
            border: 1px solid #00C80544;
            border-radius: 16px;
            padding: 24px;
        ">
            <div style="font-size: 14px; color: #9B9B9B;">Based on 6-factor analysis</div>
            <div style="font-size: 28px; font-weight: 800; color: #00C805; margin-top: 8px;">
                {winner} scores higher ({winner_score:.1f}/10)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

elif ticker_a or ticker_b:
    st.info("Enter both tickers to compare them side by side.")
else:
    st.markdown(
        """
        <div style="text-align: center; padding: 80px 20px; color: #9B9B9B;">
            <div style="font-size: 48px; margin-bottom: 16px;">\U0001f4ca</div>
            <div style="font-size: 18px;">Enter two ticker symbols above to compare</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

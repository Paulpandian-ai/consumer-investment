"""Alternative stock suggestions component."""

import streamlit as st


def render_alternatives(current_ticker: str, signal: str, alternatives: list):
    """
    Show alternative stock suggestions when signal is HOLD or SELL.

    Args:
        current_ticker: The stock being analyzed.
        signal: Current signal ('BUY', 'HOLD', 'SELL').
        alternatives: List of dicts with ticker, name, score, reason.
    """
    if signal == 'BUY' or not alternatives:
        return

    st.markdown("### \U0001f4a1 Consider These Instead")

    for alt in alternatives[:3]:
        score_color = '#00C805' if alt['score'] >= 7 else '#FFB800'

        st.markdown(
            f"""
            <div style="
                background: #2A2A2A;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <div style="font-size: 18px; font-weight: 700; color: #FFFFFF;">
                        {alt['ticker']}
                    </div>
                    <div style="font-size: 13px; color: #9B9B9B; margin-top: 2px;">
                        {alt['name']}
                    </div>
                    <div style="font-size: 13px; color: #CCCCCC; margin-top: 6px;">
                        {alt['reason']}
                    </div>
                </div>
                <div style="
                    background: {score_color}22;
                    color: {score_color};
                    padding: 8px 16px;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 16px;
                    min-width: 50px;
                    text-align: center;
                    margin-left: 16px;
                    flex-shrink: 0;
                ">
                    {alt['score']:.1f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

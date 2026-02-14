"""Buy / Hold / Sell signal badge component."""

import streamlit as st


def render_signal(signal: str, confidence: float, reasoning: str):
    """
    Render the main Buy/Hold/Sell signal card.

    Args:
        signal: 'BUY', 'HOLD', or 'SELL'.
        confidence: 0-100 confidence percentage.
        reasoning: One-paragraph AI explanation.
    """
    config = {
        'BUY': {'color': '#00C805', 'icon': '\U0001f44d', 'bg': '#00C80515'},
        'HOLD': {'color': '#FFB800', 'icon': '\u270b', 'bg': '#FFB80015'},
        'SELL': {'color': '#FF5000', 'icon': '\U0001f44e', 'bg': '#FF500015'},
    }

    c = config.get(signal, config['HOLD'])

    st.markdown(
        f"""
        <div style="
            background: {c['bg']};
            border: 2px solid {c['color']};
            border-radius: 20px;
            padding: 32px;
            text-align: center;
            margin: 20px 0;
        ">
            <div style="font-size: 48px;">{c['icon']}</div>
            <div style="
                font-size: 36px;
                font-weight: 800;
                color: {c['color']};
                margin: 16px 0 8px;
            ">{signal}</div>
            <div style="
                font-size: 16px;
                color: #9B9B9B;
            ">{confidence:.0f}% confidence based on 6 factors</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Why this signal?"):
        st.write(reasoning)

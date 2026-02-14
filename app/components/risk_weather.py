"""Risk Weather dashboard component - translates market conditions into weather metaphors."""

import streamlit as st


def render_risk_weather(composite_score: float, factors: dict):
    """
    Render the Risk Weather widget.

    Args:
        composite_score: 1-10 overall score.
        factors: dict of factor dicts (each with 'score' and 'summary').
    """
    if composite_score >= 7:
        weather = "\u2600\ufe0f"
        label = "Sunny"
        color = "#00C805"
        description = "Clear skies ahead"
    elif composite_score >= 5:
        weather = "\u26c5"
        label = "Partly Cloudy"
        color = "#FFB800"
        description = "Some clouds on the horizon"
    elif composite_score >= 3:
        weather = "\U0001f327\ufe0f"
        label = "Rainy"
        color = "#FF8C00"
        description = "Bring an umbrella"
    else:
        weather = "\u26c8\ufe0f"
        label = "Stormy"
        color = "#FF5000"
        description = "Seek shelter"

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {color}22, {color}11);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            border: 1px solid {color}44;
            margin-bottom: 8px;
        ">
            <div style="font-size: 64px;">{weather}</div>
            <div style="font-size: 24px; font-weight: 700; color: {color}; margin-top: 4px;">
                {label}
            </div>
            <div style="font-size: 14px; color: #9B9B9B; margin-top: 8px;">
                {description}
            </div>
            <div style="
                font-size: 32px;
                font-weight: 800;
                color: {color};
                margin-top: 12px;
            ">
                {composite_score:.1f}<span style="font-size: 16px; color: #9B9B9B;">/10</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Mini factor bar below weather
    _render_factor_bar(factors)


def _render_factor_bar(factors: dict):
    """Render a compact horizontal bar of factor indicators."""
    factor_icons = {
        'supply_chain': '\U0001f517',
        'customers': '\U0001f6d2',
        'geopolitical': '\U0001f30d',
        'monetary': '\U0001f4b0',
        'correlation': '\U0001f4c8',
        'performance': '\U0001f4ca',
    }

    cols = st.columns(len(factors))
    for i, (key, data) in enumerate(factors.items()):
        score = data['score']
        if score >= 1:
            dot_color = '#00C805'
        elif score >= 0:
            dot_color = '#FFB800'
        elif score >= -1:
            dot_color = '#FF8C00'
        else:
            dot_color = '#FF5000'

        icon = factor_icons.get(key, '\U0001f4cb')
        with cols[i]:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px;">{icon}</div>
                    <div style="
                        width: 10px; height: 10px;
                        border-radius: 50%;
                        background: {dot_color};
                        margin: 4px auto 0;
                    "></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

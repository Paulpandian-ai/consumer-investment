"""Factor card components with traffic-light status indicators."""

import streamlit as st

FACTOR_CONFIG = {
    'supply_chain': {
        'icon': '\U0001f517',
        'label': 'Supply Chain',
        'color': '#00D4FF',
        'description': 'Supplier health and disruption risk',
    },
    'customers': {
        'icon': '\U0001f6d2',
        'label': 'Customer Demand',
        'color': '#FF6B6B',
        'description': 'Key customer spending trends',
    },
    'geopolitical': {
        'icon': '\U0001f30d',
        'label': 'Geopolitical',
        'color': '#FFE66D',
        'description': 'Trade policy and regional risks',
    },
    'monetary': {
        'icon': '\U0001f4b0',
        'label': 'Fed & Rates',
        'color': '#4ECDC4',
        'description': 'Interest rate sensitivity',
    },
    'correlation': {
        'icon': '\U0001f4c8',
        'label': 'Market Moves',
        'color': '#A06CD5',
        'description': 'Sector and peer correlation',
    },
    'performance': {
        'icon': '\U0001f4ca',
        'label': 'Fundamentals',
        'color': '#95E1D3',
        'description': 'Earnings and growth metrics',
    },
}


def get_traffic_light(score: float) -> tuple:
    """Convert a -2 to +2 score to a traffic-light tuple (icon, label, color)."""
    if score >= 1:
        return '\U0001f7e2', 'Good', '#00C805'
    elif score >= 0:
        return '\U0001f7e1', 'Watch', '#FFB800'
    elif score >= -1:
        return '\U0001f7e0', 'Caution', '#FF8C00'
    else:
        return '\U0001f534', 'Risk', '#FF5000'


def render_factor_card(factor_key: str, score: float, summary: str):
    """
    Render a single factor card with traffic-light status.

    Args:
        factor_key: Key from FACTOR_CONFIG.
        score: -2 to +2 score.
        summary: One-sentence AI summary.
    """
    config = FACTOR_CONFIG.get(factor_key, {
        'icon': '\U0001f4cb',
        'label': factor_key.replace('_', ' ').title(),
        'color': '#9B9B9B',
        'description': '',
    })
    light, status, status_color = get_traffic_light(score)

    st.markdown(
        f"""
        <div style="
            background: #2A2A2A;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 4px solid {config['color']};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 22px;">{config['icon']}</span>
                    <span style="font-size: 16px; font-weight: 600; color: #FFFFFF;">
                        {config['label']}
                    </span>
                </div>
                <div style="
                    background: {status_color}22;
                    color: {status_color};
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 600;
                ">
                    {light} {status}
                </div>
            </div>
            <div style="
                font-size: 14px;
                color: #CCCCCC;
                margin-top: 10px;
                line-height: 1.4;
            ">
                {summary}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Expandable details
    with st.expander("See details"):
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Score", f"{score:+.1f}", delta=None)
        with col_b:
            # Show a mini progress bar from -2 to +2
            normalized = (score + 2) / 4  # 0 to 1
            bar_color = status_color
            st.markdown(
                f"""
                <div style="margin-top: 14px;">
                    <div style="
                        background: #3A3A3A;
                        border-radius: 4px;
                        height: 8px;
                        width: 100%;
                    ">
                        <div style="
                            background: {bar_color};
                            border-radius: 4px;
                            height: 8px;
                            width: {normalized * 100:.0f}%;
                        "></div>
                    </div>
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        font-size: 11px;
                        color: #9B9B9B;
                        margin-top: 4px;
                    ">
                        <span>-2</span><span>0</span><span>+2</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.caption(config['description'])


def render_all_factor_cards(factors: dict):
    """Render all 6 factor cards in a 2-column grid."""
    factor_keys = ['supply_chain', 'customers', 'geopolitical', 'monetary', 'correlation', 'performance']
    col1, col2 = st.columns(2)

    for i, key in enumerate(factor_keys):
        if key not in factors:
            continue
        with col1 if i % 2 == 0 else col2:
            render_factor_card(key, factors[key]['score'], factors[key]['summary'])

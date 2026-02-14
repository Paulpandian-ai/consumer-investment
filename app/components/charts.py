"""Simplified chart components with Robinhood-style aesthetics."""

import streamlit as st
import plotly.graph_objects as go


def render_simple_chart(dates: list, values: list, height: int = 200):
    """
    Render a clean, minimal line chart (Robinhood-style).

    Args:
        dates: List of date strings or datetime objects.
        values: List of numeric values.
        height: Chart height in pixels.
    """
    if not dates or not values or len(dates) != len(values):
        st.caption("Chart data unavailable")
        return

    # Color based on overall trend
    color = '#00C805' if values[-1] >= values[0] else '#FF5000'

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'{color}15',
        hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>',
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=height,
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_price_header(ticker: str, name: str, price: float, change_pct: float):
    """
    Render price + change at the top of the analysis view.

    Args:
        ticker: Stock symbol.
        name: Company name.
        price: Current price.
        change_pct: Percentage change.
    """
    change_color = '#00C805' if change_pct >= 0 else '#FF5000'
    arrow = '\u25b2' if change_pct >= 0 else '\u25bc'

    st.markdown(
        f"""
        <div style="margin-bottom: 16px;">
            <div style="font-size: 14px; color: #9B9B9B;">{name}</div>
            <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 4px;">
                <span style="font-size: 32px; font-weight: 800; color: #FFFFFF;">
                    ${price:,.2f}
                </span>
                <span style="font-size: 16px; font-weight: 600; color: {change_color};">
                    {arrow} {abs(change_pct):.2f}%
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

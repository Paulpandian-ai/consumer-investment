"""Settings page - User preferences."""

import streamlit as st

st.set_page_config(page_title="Settings | Factor Impact Intelligence", page_icon="\u2699\ufe0f", layout="wide")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #1E1E1E; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("\u2699\ufe0f Settings")
st.caption("Customize your experience")

st.markdown("---")

# API keys status
st.markdown("### API Configuration")

has_anthropic = False
has_fred = False

try:
    anthropic_key = st.secrets.get('ANTHROPIC_API_KEY', '')
    has_anthropic = bool(anthropic_key and anthropic_key != 'sk-ant-...')
except Exception:
    pass

try:
    fred_key = st.secrets.get('FRED_API_KEY', '')
    has_fred = bool(fred_key and fred_key != 'your-fred-api-key')
except Exception:
    pass

col1, col2 = st.columns(2)
with col1:
    status = "\U0001f7e2 Connected" if has_anthropic else "\U0001f534 Not configured"
    st.markdown(f"**Claude API**: {status}")
    if not has_anthropic:
        st.caption("Add ANTHROPIC_API_KEY to .streamlit/secrets.toml for AI-powered explanations.")

with col2:
    status = "\U0001f7e2 Connected" if has_fred else "\U0001f534 Not configured"
    st.markdown(f"**FRED API**: {status}")
    if not has_fred:
        st.caption("Add FRED_API_KEY to .streamlit/secrets.toml for live macro data.")

st.markdown("---")

# Factor weights
st.markdown("### Factor Weights")
st.caption("Adjust how much each factor influences the overall score. Weights must sum to 100%.")

if 'custom_weights' not in st.session_state:
    st.session_state.custom_weights = {
        'supply_chain': 20,
        'customers': 20,
        'geopolitical': 15,
        'monetary': 15,
        'correlation': 15,
        'performance': 15,
    }

labels = {
    'supply_chain': '\U0001f517 Supply Chain',
    'customers': '\U0001f6d2 Customer Demand',
    'geopolitical': '\U0001f30d Geopolitical',
    'monetary': '\U0001f4b0 Fed & Rates',
    'correlation': '\U0001f4c8 Market Moves',
    'performance': '\U0001f4ca Fundamentals',
}

for key, label in labels.items():
    st.session_state.custom_weights[key] = st.slider(
        label,
        min_value=0,
        max_value=40,
        value=st.session_state.custom_weights[key],
        step=5,
        key=f"weight_{key}",
    )

total = sum(st.session_state.custom_weights.values())
if total != 100:
    st.warning(f"Weights sum to {total}%. Please adjust so they total 100%.")
else:
    st.success("Weights sum to 100% \u2714")

st.markdown("---")

# About
st.markdown("### About")
st.markdown(
    """
    **Factor Impact Intelligence** transforms sophisticated 6-factor stock analysis
    into easy-to-understand signals that anyone can use.

    **Factors analyzed:**
    1. **Supply Chain** - Supplier health and disruption risk
    2. **Customer Demand** - Key customer spending trends
    3. **Geopolitical** - Trade policy and regional risks
    4. **Fed & Rates** - Interest rate sensitivity
    5. **Market Moves** - Sector and peer correlation
    6. **Fundamentals** - Earnings and growth metrics

    *This tool is for educational purposes only and does not constitute financial advice.*
    """
)

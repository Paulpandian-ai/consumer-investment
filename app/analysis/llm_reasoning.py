"""Claude API integration for consumer-friendly AI explanations."""

import streamlit as st

_USE_LLM = None


def _is_llm_available() -> bool:
    """Check if the Anthropic API key is configured."""
    global _USE_LLM
    if _USE_LLM is not None:
        return _USE_LLM
    try:
        key = st.secrets.get('ANTHROPIC_API_KEY', '')
        _USE_LLM = bool(key and key != 'sk-ant-...')
        return _USE_LLM
    except Exception:
        _USE_LLM = False
        return False


def generate_factor_summary(ticker: str, factor: str, data: dict) -> str:
    """
    Generate a one-sentence consumer-friendly summary for a factor.

    Falls back to a template-based summary if Claude API is unavailable.
    """
    if not _is_llm_available():
        return _fallback_factor_summary(ticker, factor, data)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])

        prompt = f"""You are explaining stock analysis to a 25-year-old who just started investing.

Stock: {ticker}
Factor: {factor}
Data: {data}

Write ONE sentence (max 15 words) explaining this factor's impact.
- Use everyday language, no jargon
- Be specific about what's happening
- Sound like a smart friend, not a robot

Example good outputs:
- "TSMC is running smoothly, so chip supply looks solid"
- "Microsoft is spending big on AI, which means more orders"
- "New tariffs could raise costs by ~5%"

Your one-sentence summary:"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()
    except Exception:
        return _fallback_factor_summary(ticker, factor, data)


def generate_signal_reasoning(ticker: str, factors: dict, signal: str) -> str:
    """
    Generate the full reasoning paragraph for a Buy/Hold/Sell signal.

    Falls back to template-based reasoning if Claude API is unavailable.
    """
    if not _is_llm_available():
        return _fallback_signal_reasoning(ticker, factors, signal)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])

        factor_summary = "\n".join(
            f"  {k}: score={v['score']:+.1f}, summary={v['summary']}"
            for k, v in factors.items()
        )

        prompt = f"""You are explaining a stock recommendation to someone new to investing.

Stock: {ticker}
Signal: {signal}
Factor Scores (scale: -2 to +2):
{factor_summary}

Write 2-3 sentences explaining why this signal makes sense.
- Lead with the most important factor
- Use plain language (no "pursuant to" or "fundamentally")
- Be balanced - acknowledge both positives and negatives
- End with what to watch for

Example good output:
"NVIDIA looks solid because its biggest customers (Microsoft, Google, Meta) are all increasing AI spending. The main concern is China export restrictions, which could cut revenue by ~20%. Watch for any changes in US-China policy."

Your explanation:"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()
    except Exception:
        return _fallback_signal_reasoning(ticker, factors, signal)


def _fallback_factor_summary(ticker: str, factor: str, data: dict) -> str:
    """Template-based fallback when Claude API is unavailable."""
    templates = {
        'supply_chain': f"{ticker}'s supply chain looks {data.get('risk_level', 'stable')}",
        'customers': f"Customer demand for {ticker} appears {data.get('concentration', 'moderate')}",
        'geopolitical': f"Geopolitical risk for {ticker} is {data.get('risk_level', 'moderate')}",
        'monetary': f"{ticker} has {data.get('sensitivity', 'moderate')} rate sensitivity",
        'correlation': f"{ticker} is {data.get('correlation_level', 'moderately')} correlated with its sector",
        'performance': f"{ticker}'s fundamentals look {data.get('outlook', 'stable')}",
    }
    return templates.get(factor, f"Analysis for {ticker} is in progress")


def _fallback_signal_reasoning(ticker: str, factors: dict, signal: str) -> str:
    """Template-based fallback reasoning."""
    # Find strongest positive and negative factors
    sorted_factors = sorted(factors.items(), key=lambda x: x[1]['score'], reverse=True)
    best = sorted_factors[0]
    worst = sorted_factors[-1]

    if signal == 'BUY':
        return (
            f"{ticker} scores well across multiple factors. "
            f"The strongest signal comes from {best[0].replace('_', ' ')} ({best[1]['summary']}). "
            f"Keep an eye on {worst[0].replace('_', ' ')} which is the weakest area."
        )
    elif signal == 'HOLD':
        return (
            f"{ticker} shows mixed signals across the 6 factors. "
            f"On the positive side, {best[0].replace('_', ' ')} looks good ({best[1]['summary']}). "
            f"However, {worst[0].replace('_', ' ')} raises some concerns ({worst[1]['summary']}). "
            f"Wait for clearer signals before making a move."
        )
    else:
        return (
            f"{ticker} is showing caution signals across several factors. "
            f"The biggest concern is {worst[0].replace('_', ' ')} ({worst[1]['summary']}). "
            f"Consider looking at alternatives in the same sector that score better."
        )

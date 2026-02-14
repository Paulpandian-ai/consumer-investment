"""6-Factor scoring engine for stock analysis."""

import numpy as np
import streamlit as st

from app.analysis.data_fetcher import (
    fetch_stock_history,
    fetch_stock_info,
    fetch_peer_history,
    get_sector_etf,
    get_sector_peers,
)
from app.analysis.llm_reasoning import generate_factor_summary, generate_signal_reasoning
from app.utils.cache import get_macro_data

# Factor weights (must sum to 1.0)
FACTOR_WEIGHTS = {
    'supply_chain': 0.20,
    'customers': 0.20,
    'geopolitical': 0.15,
    'monetary': 0.15,
    'correlation': 0.15,
    'performance': 0.15,
}


def analyze_stock(ticker: str) -> dict:
    """
    Run full 6-factor analysis on a stock.

    Returns dict with:
        - ticker, name, composite_score (1-10)
        - signal (BUY/HOLD/SELL), confidence (50-90%)
        - reasoning (AI-generated paragraph)
        - factors (dict of factor dicts with score + summary)
        - alternatives (list of dicts for HOLD/SELL)
    """
    info = fetch_stock_info(ticker)
    if not info:
        return _empty_result(ticker)

    hist = fetch_stock_history(ticker)
    macro = get_macro_data()

    # Analyze each factor
    factors = {
        'supply_chain': analyze_supply_chain(ticker, info),
        'customers': analyze_customers(ticker, info),
        'geopolitical': analyze_geopolitical(ticker, info),
        'monetary': analyze_monetary(ticker, info, macro),
        'correlation': analyze_correlation(ticker, info),
        'performance': analyze_performance(ticker, info, hist),
    }

    # Composite score (1-10)
    weighted_sum = sum(
        (factors[f]['score'] + 2) / 4 * FACTOR_WEIGHTS[f]
        for f in factors
    )
    composite_score = round(weighted_sum * 9 + 1, 1)

    # Signal
    if composite_score >= 7:
        signal = 'BUY'
    elif composite_score >= 4:
        signal = 'HOLD'
    else:
        signal = 'SELL'

    # Confidence (based on factor agreement)
    scores = [factors[f]['score'] for f in factors]
    spread = max(scores) - min(scores) if scores else 4
    agreement = 1 - spread / 4
    confidence = round(50 + agreement * 40, 0)

    # AI reasoning
    reasoning = generate_signal_reasoning(ticker, factors, signal)

    # Alternatives for HOLD/SELL
    alternatives = []
    if signal != 'BUY':
        alternatives = find_alternatives(ticker, info.get('sector', ''))

    return {
        'ticker': ticker,
        'name': info.get('shortName', ticker),
        'composite_score': composite_score,
        'signal': signal,
        'confidence': confidence,
        'reasoning': reasoning,
        'factors': factors,
        'alternatives': alternatives,
        'price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
        'change_pct': info.get('regularMarketChangePercent', 0),
    }


# ---------------------------------------------------------------------------
# Individual factor analyzers
# ---------------------------------------------------------------------------

def analyze_supply_chain(ticker: str, info: dict) -> dict:
    """Analyze supplier concentration and disruption risk."""
    sector = info.get('sector', '')
    industry = info.get('industry', '').lower()

    # Heuristic scoring based on sector/industry
    if sector == 'Technology':
        if 'semiconductor' in industry:
            score = 0.5
            data = {'sector': sector, 'key_suppliers': ['TSMC', 'Samsung'], 'risk_level': 'moderate'}
        elif 'software' in industry:
            score = 1.5
            data = {'sector': sector, 'key_suppliers': ['Cloud providers'], 'risk_level': 'low'}
        else:
            score = 1.0
            data = {'sector': sector, 'key_suppliers': ['Various'], 'risk_level': 'low-moderate'}
    elif sector == 'Consumer Cyclical':
        score = 0.0
        data = {'sector': sector, 'key_suppliers': ['Global manufacturers'], 'risk_level': 'moderate'}
    elif sector == 'Energy':
        score = -0.5
        data = {'sector': sector, 'key_suppliers': ['OPEC-dependent'], 'risk_level': 'elevated'}
    elif sector == 'Healthcare':
        score = 0.5
        data = {'sector': sector, 'key_suppliers': ['Pharma supply chain'], 'risk_level': 'moderate'}
    else:
        score = 1.0
        data = {'sector': sector, 'key_suppliers': ['Diversified'], 'risk_level': 'low'}

    summary = generate_factor_summary(ticker, 'supply_chain', data)
    return {'score': _clamp(score), 'summary': summary}


def analyze_customers(ticker: str, info: dict) -> dict:
    """Analyze customer concentration and demand trends."""
    sector = info.get('sector', '')
    revenue_growth = info.get('revenueGrowth', 0) or 0

    if revenue_growth > 0.2:
        score = 1.5
        concentration = 'growing strongly'
    elif revenue_growth > 0.05:
        score = 0.5
        concentration = 'growing steadily'
    elif revenue_growth > -0.05:
        score = 0.0
        concentration = 'stable'
    else:
        score = -1.0
        concentration = 'declining'

    data = {'sector': sector, 'revenue_growth': f"{revenue_growth*100:.1f}%", 'concentration': concentration}
    summary = generate_factor_summary(ticker, 'customers', data)
    return {'score': _clamp(score), 'summary': summary}


def analyze_geopolitical(ticker: str, info: dict) -> dict:
    """Analyze geographic revenue exposure and policy risks."""
    country = info.get('country', 'United States')
    info_str = str(info).lower()

    # Check for international risk factors
    china_exposed = 'china' in info_str or 'chinese' in info_str
    emerging_market = country not in ('United States', 'United Kingdom', 'Canada', 'Germany', 'Japan', 'France')

    if china_exposed and emerging_market:
        score = -1.5
        risk_level = 'high'
    elif china_exposed:
        score = -0.5
        risk_level = 'elevated'
    elif emerging_market:
        score = -0.5
        risk_level = 'moderate'
    else:
        score = 1.0
        risk_level = 'low'

    data = {'country': country, 'china_exposure': china_exposed, 'risk_level': risk_level}
    summary = generate_factor_summary(ticker, 'geopolitical', data)
    return {'score': _clamp(score), 'summary': summary}


def analyze_monetary(ticker: str, info: dict, macro: dict) -> dict:
    """Analyze interest rate sensitivity."""
    beta = info.get('beta', 1.0) or 1.0
    sector = info.get('sector', '')
    pe = info.get('forwardPE') or info.get('trailingPE') or 20
    fed_rate = macro.get('fed_rate', 5.25)

    # High-growth/high-beta stocks are more rate-sensitive
    rate_sensitive_sectors = {'Technology', 'Real Estate', 'Consumer Cyclical'}
    is_rate_sensitive = sector in rate_sensitive_sectors or beta > 1.3 or pe > 30

    if is_rate_sensitive and fed_rate > 5:
        score = -1.0
        sensitivity = 'high'
    elif is_rate_sensitive:
        score = -0.5
        sensitivity = 'moderate-high'
    elif fed_rate > 5:
        score = 0.0
        sensitivity = 'moderate'
    else:
        score = 0.5
        sensitivity = 'low'

    data = {
        'beta': f"{beta:.2f}",
        'fed_rate': f"{fed_rate:.2f}%",
        'sensitivity': sensitivity,
        'sector': sector,
    }
    summary = generate_factor_summary(ticker, 'monetary', data)
    return {'score': _clamp(score), 'summary': summary}


def analyze_correlation(ticker: str, info: dict) -> dict:
    """Analyze sector peer correlation."""
    sector = info.get('sector', '')

    try:
        etf = get_sector_etf(sector)
        peers_data = fetch_peer_history([ticker, etf], period='6mo')

        if ticker in peers_data and etf in peers_data:
            stock_returns = peers_data[ticker].pct_change().dropna()
            etf_returns = peers_data[etf].pct_change().dropna()
            # Align on common dates
            common = stock_returns.index.intersection(etf_returns.index)
            if len(common) > 20:
                corr = np.corrcoef(
                    stock_returns.loc[common].values,
                    etf_returns.loc[common].values,
                )[0, 1]

                # Low correlation = more diversification benefit = slightly positive
                # High correlation = moves with market = neutral
                if corr > 0.85:
                    score = -0.5
                    correlation_level = 'highly'
                elif corr > 0.6:
                    score = 0.0
                    correlation_level = 'moderately'
                else:
                    score = 0.5
                    correlation_level = 'loosely'

                data = {'correlation': f"{corr:.2f}", 'etf': etf, 'correlation_level': correlation_level}
                summary = generate_factor_summary(ticker, 'correlation', data)
                return {'score': _clamp(score), 'summary': summary}
    except Exception:
        pass

    # Fallback
    data = {'correlation_level': 'moderately'}
    summary = generate_factor_summary(ticker, 'correlation', data)
    return {'score': 0.0, 'summary': summary}


def analyze_performance(ticker: str, info: dict, hist) -> dict:
    """Analyze earnings, growth, and valuation metrics."""
    pe = info.get('forwardPE') or info.get('trailingPE') or 0
    revenue_growth = info.get('revenueGrowth') or 0
    profit_margin = info.get('profitMargins') or 0
    roe = info.get('returnOnEquity') or 0

    score = 0.0

    # Revenue growth scoring
    if revenue_growth > 0.20:
        score += 0.8
    elif revenue_growth > 0.05:
        score += 0.3
    elif revenue_growth < -0.05:
        score -= 0.5

    # Valuation scoring
    if 0 < pe < 15:
        score += 0.5
    elif 15 <= pe <= 25:
        score += 0.2
    elif pe > 40:
        score -= 0.3

    # Profitability scoring
    if profit_margin > 0.20:
        score += 0.4
    elif profit_margin > 0.10:
        score += 0.2
    elif profit_margin < 0:
        score -= 0.5

    # ROE scoring
    if roe > 0.20:
        score += 0.3
    elif roe < 0:
        score -= 0.3

    data = {
        'pe': f"{pe:.1f}" if pe else 'N/A',
        'revenue_growth': f"{revenue_growth*100:.1f}%" if revenue_growth else 'N/A',
        'profit_margin': f"{profit_margin*100:.1f}%" if profit_margin else 'N/A',
        'outlook': 'strong' if score > 1 else 'stable' if score > 0 else 'weak',
    }
    summary = generate_factor_summary(ticker, 'performance', data)
    return {'score': _clamp(score), 'summary': summary}


# ---------------------------------------------------------------------------
# Alternatives
# ---------------------------------------------------------------------------

def find_alternatives(ticker: str, sector: str) -> list:
    """Find better-rated stocks in the same sector."""
    sector_alternatives = {
        'Technology': [
            {'ticker': 'MSFT', 'name': 'Microsoft', 'score': 7.5, 'reason': 'Diversified revenue, strong cloud growth, solid dividends'},
            {'ticker': 'AAPL', 'name': 'Apple', 'score': 7.2, 'reason': 'Massive cash flow, loyal customer base, services growth'},
            {'ticker': 'AVGO', 'name': 'Broadcom', 'score': 7.0, 'reason': 'Diversified chip portfolio, solid dividends'},
        ],
        'Healthcare': [
            {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'score': 7.3, 'reason': 'Defensive play, diversified healthcare, strong dividend'},
            {'ticker': 'UNH', 'name': 'UnitedHealth', 'score': 7.1, 'reason': 'Dominant insurer, growing Optum business'},
            {'ticker': 'LLY', 'name': 'Eli Lilly', 'score': 7.0, 'reason': 'Strong drug pipeline, Mounjaro/Zepbound growth'},
        ],
        'Financial Services': [
            {'ticker': 'JPM', 'name': 'JPMorgan Chase', 'score': 7.4, 'reason': 'Best-in-class bank, diversified revenue streams'},
            {'ticker': 'BLK', 'name': 'BlackRock', 'score': 7.1, 'reason': 'World\'s largest asset manager, ETF dominance'},
            {'ticker': 'V', 'name': 'Visa', 'score': 7.0, 'reason': 'Payment network duopoly, high margins'},
        ],
        'Consumer Cyclical': [
            {'ticker': 'AMZN', 'name': 'Amazon', 'score': 7.3, 'reason': 'E-commerce + AWS dominance, growing margins'},
            {'ticker': 'HD', 'name': 'Home Depot', 'score': 7.0, 'reason': 'Housing market leader, strong DIY demand'},
            {'ticker': 'COST', 'name': 'Costco', 'score': 6.9, 'reason': 'Membership model, recession-resistant'},
        ],
        'Energy': [
            {'ticker': 'XOM', 'name': 'ExxonMobil', 'score': 6.8, 'reason': 'Integrated major, strong dividend history'},
            {'ticker': 'CVX', 'name': 'Chevron', 'score': 6.7, 'reason': 'Lower debt than peers, solid balance sheet'},
            {'ticker': 'COP', 'name': 'ConocoPhillips', 'score': 6.5, 'reason': 'Pure-play E&P, low breakeven costs'},
        ],
    }

    alternatives = sector_alternatives.get(sector, [
        {'ticker': 'SPY', 'name': 'S&P 500 ETF', 'score': 6.5, 'reason': 'Broad market exposure, low fees, less risk'},
        {'ticker': 'QQQ', 'name': 'Nasdaq 100 ETF', 'score': 6.5, 'reason': 'Tech-heavy index, diversified growth'},
        {'ticker': 'VTI', 'name': 'Total Market ETF', 'score': 6.3, 'reason': 'Maximum diversification, lowest risk'},
    ])

    # Remove the current ticker from alternatives
    return [a for a in alternatives if a['ticker'] != ticker][:3]


def _clamp(score: float, lo: float = -2.0, hi: float = 2.0) -> float:
    """Clamp a score to the valid range."""
    return max(lo, min(hi, round(score, 1)))


def _empty_result(ticker: str) -> dict:
    """Return an empty result dict when data is unavailable."""
    empty_factor = {'score': 0.0, 'summary': 'Data unavailable'}
    return {
        'ticker': ticker,
        'name': ticker,
        'composite_score': 5.0,
        'signal': 'HOLD',
        'confidence': 50,
        'reasoning': f'Could not fetch sufficient data for {ticker}. Please check the ticker symbol.',
        'factors': {k: dict(empty_factor) for k in FACTOR_WEIGHTS},
        'alternatives': [],
        'price': 0,
        'change_pct': 0,
    }

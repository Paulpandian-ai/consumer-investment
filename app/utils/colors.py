"""Color scheme constants for the Factor Impact Intelligence app."""

COLORS = {
    # Signal colors
    'bullish': '#00C805',
    'bearish': '#FF5000',
    'neutral': '#FFB800',

    # Background
    'bg_dark': '#1E1E1E',
    'bg_light': '#FFFFFF',
    'card_bg': '#2A2A2A',

    # Text
    'text_primary': '#FFFFFF',
    'text_secondary': '#9B9B9B',

    # Factor accent colors
    'supply_chain': '#00D4FF',
    'customers': '#FF6B6B',
    'geopolitical': '#FFE66D',
    'monetary': '#4ECDC4',
    'correlation': '#A06CD5',
    'performance': '#95E1D3',
}

# Weather state mappings
WEATHER_STATES = {
    'sunny': {
        'icon': '\u2600\ufe0f',
        'label': 'Sunny',
        'color': '#00C805',
        'description': 'Clear skies ahead',
        'min_score': 7,
    },
    'partly_cloudy': {
        'icon': '\u26c5',
        'label': 'Partly Cloudy',
        'color': '#FFB800',
        'description': 'Some clouds on the horizon',
        'min_score': 5,
    },
    'rainy': {
        'icon': '\U0001f327\ufe0f',
        'label': 'Rainy',
        'color': '#FF8C00',
        'description': 'Bring an umbrella',
        'min_score': 3,
    },
    'stormy': {
        'icon': '\u26c8\ufe0f',
        'label': 'Stormy',
        'color': '#FF5000',
        'description': 'Seek shelter',
        'min_score': 0,
    },
}

# Traffic light mappings
TRAFFIC_LIGHTS = {
    'good': {'icon': '\U0001f7e2', 'label': 'Good', 'color': '#00C805', 'min_score': 1},
    'watch': {'icon': '\U0001f7e1', 'label': 'Watch', 'color': '#FFB800', 'min_score': 0},
    'caution': {'icon': '\U0001f7e0', 'label': 'Caution', 'color': '#FF8C00', 'min_score': -1},
    'risk': {'icon': '\U0001f534', 'label': 'Risk', 'color': '#FF5000', 'min_score': -2},
}

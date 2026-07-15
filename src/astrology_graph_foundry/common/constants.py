SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ASPECTS = {
    "conjunction": 0,
    "semisextile": 30,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "quincunx": 150,
    "opposition": 180,
}

MAJOR_ASPECTS = {"conjunction", "sextile", "square", "trine", "opposition"}

DEFAULT_ORBS = {
    "conjunction": 6.0,
    "semisextile": 2.0,
    "sextile": 4.5,
    "square": 5.5,
    "trine": 5.5,
    "quincunx": 2.5,
    "opposition": 6.0,
}

LUMINARIES = {"Sun", "Moon"}
ANGLES = {"ASC", "DSC", "MC", "IC"}
OUTER_PLANETS = {"Uranus", "Neptune", "Pluto"}
POINTS = {"True Node", "Mean Node", "Chiron", "Vertex", "Part of Fortune"}

SIGN_RULERS_TRADITIONAL = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

SIGN_RULERS_MODERN = {
    **SIGN_RULERS_TRADITIONAL,
    "Scorpio": "Pluto", "Aquarius": "Uranus", "Pisces": "Neptune",
}

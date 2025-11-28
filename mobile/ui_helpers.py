# ui_helpers.py
from flet import Colors

# Default palette (substitua pelos hex reais do seu desktop app)
THEME = {
    "primary": "#1E88E5",   # azul
    "accent": "#FFC107",
    "bg_dark": "#0B1220",#37474F
    "surface_dark": "#37474F",#0B1220
    "text_on_dark": "#FFFFFF",
    "bg_light": "#FFFFFF",
    "surface_light": "#F3F4F6",
    "text_on_light": "#0B1220",
    "success": "#43A047",
    "danger": "#EF5350",
    "text_secondary": "#888888",
}

# Touch target sizes
TOUCH = {
    "button_height": 56,
    "input_height": 48,
    "icon_size": 28,
}

def format_ts_iso(ts: str) -> str:
    # ts expected in ISO format -> return short friendly
    if not ts: return ""
    return ts.replace("T", " ")[:19]

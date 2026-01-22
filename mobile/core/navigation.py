# mobile/core/navigation.py

"""
Responsibilities:
- Core module for navigation.
- Provide shared application logic.
"""

ROUTES = {
    "login": "/login",
    "dashboard": "/",
    "inventory": "/inventory",
    "profile": "/profile",
    "settings": "/settings",
    "zone_details": "/zone_details",
    "counting": "/counting",
}

BOTTOM_NAV_ROUTES = [ROUTES["dashboard"], ROUTES["inventory"], ROUTES["settings"]]

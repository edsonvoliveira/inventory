# mobile/core/navigation.py

"""
Responsibilities:
- Core module for navigation.
- Provide shared application logic.
"""

ROUTES = {
    "login": "/login",
    "dashboard": "/dashboard",
    "profile": "/profile",
    "zone_details": "/zone_details",
    "counting": "/counting",
}

BOTTOM_NAV_ROUTES = [ROUTES["dashboard"], ROUTES["profile"]]

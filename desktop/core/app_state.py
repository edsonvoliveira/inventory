from dataclasses import dataclass


@dataclass
class AppState:
    is_authenticated: bool = False

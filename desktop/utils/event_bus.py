# desktop/utils/event_bus.py

"""
Responsibilities:
- Provide a simple in-process event bus for UI refresh signaling.
"""

from typing import Any, Callable, Dict


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, Dict[str, Callable[[Any], None]]] = {}
        self._dirty_routes: Dict[str, bool] = {}

    def subscribe(self, event: str, handler: Callable[[Any], None], *, key: str) -> None:
        handlers = self._subscribers.setdefault(event, {})
        handlers[key] = handler

    def unsubscribe(self, event: str, *, key: str) -> None:
        handlers = self._subscribers.get(event)
        if not handlers:
            return
        handlers.pop(key, None)
        if not handlers:
            self._subscribers.pop(event, None)

    def publish(self, event: str, payload: Any = None) -> None:
        handlers = self._subscribers.get(event, {})
        for handler in list(handlers.values()):
            handler(payload)

    def mark_dirty(self, route: str) -> None:
        self._dirty_routes[route] = True

    def consume_dirty(self, route: str) -> bool:
        return self._dirty_routes.pop(route, False)


event_bus = EventBus()

from collections.abc import Callable
from enum import Enum
from typing import List, Optional, Tuple, Any


class EventBus:
    """Singleton event bus for games to manage event listeners and notifications.

    - Call `subscribe(event, callback)` on a game instance to register callbacks.
    - If `event` is `None`, the callback will receive all events.
    - Callbacks are attempted to be invoked with the event as the first argument; if that fails,
      the event is not passed (keeps backward compatibility with zero-arg callbacks).
    """

    def __init__(self) -> None:
        self.listeners: List[Tuple[Optional[Enum], Callable[..., None]]] = []

    def subscribe(self, event: Optional[Enum], callback: Callable[[Any], None]) -> None:
        """Register `callback` for `event`. Use `event=None` to receive all events."""
        self.listeners.append((event, callback))

    def unsubscribe(
        self, event: Optional[Enum], callback: Callable[[Any], None]
    ) -> None:
        try:
            self.listeners.remove((event, callback))
        except ValueError:
            pass

    def notify(self, event: Enum, data: Any = None) -> None:
        """Notify matching listeners. Try passing the event as first arg; fall back if callback signature differs."""
        for registered_event, callback in list(self.listeners):
            if registered_event is None or registered_event == event:
                try:
                    callback(event, data)
                except TypeError:
                    callback(data)

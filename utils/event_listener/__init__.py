from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum


class EventListener(ABC):
    """
    Base class for event listeners in the casino games. This class provides a common interface for handling events
    and can be extended by specific game implementations to define their own event types and handling logic.
    """

    # List of event listeners, where each listener is a tuple of (event_type, callback_function).
    # The event_type is an Enum value that identifies the type of event, and the callback_function
    # is a function that will be called when that event occurs.
    listeners: list[tuple[Enum, Callable[..., None]]]

    def subscribe(self, event: Enum, callback: Callable[..., None]):
        """Registers a callback function to be called when a specific event occurs."""
        self.listeners.append((event, callback))

    def notify(self, event: Enum, *args, **kwargs):
        """Notifies all registered listeners of a specific event, passing any relevant arguments."""
        for registered_event, callback in self.listeners:
            if registered_event == event:
                callback(*args, **kwargs)

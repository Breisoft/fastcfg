"""
Event system for configuration change notifications.

This module provides the event classes and listener management for
configuration change events.
"""

from datetime import datetime
from typing import Any, Callable, List
from dataclasses import dataclass
from typing import TYPE_CHECKING
import traceback

if TYPE_CHECKING:
    from fastcfg.config.items import LiveConfigItem
else:
    LiveConfigItem = None

@dataclass
class ChangeEvent:
    """
    Event object that contains information about a configuration change.
    
    Attributes:
        item: The configuration item that changed
        old_value: The previous value
        new_value: The new value
        timestamp: When the change occurred
    """
    item: 'LiveConfigItem'
    old_value: Any
    new_value: Any
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventListenerMixin:
    """
    Manages event listeners for configuration items.
    """

    def __init__(self):
        self._event_listeners: List[Callable[[ChangeEvent], None]] = []

    def on_change(self, callback: Callable[[ChangeEvent], None] | None = None):
        """
        Register a change-event listener.

        Usage patterns supported:

            @item.on_change()
            def handler(event): ...

            item.on_change(handler)           # direct call

            item.on_change(handler).attr ...  # method-chaining
        """

        # Decorator form ─ caller used @item.on_change()
        if callback is None:

            def decorator(fn):
                self.on_change(fn)
                return fn

            return decorator

        # Direct call form
        if callback not in self._event_listeners:
            self._event_listeners.append(callback)

        return callback  # allow method chaining

    # Backwards-compatible aliases
    def remove_change_listener(self, callback: Callable[[ChangeEvent], None]):
        if callback in self._event_listeners:
            self._event_listeners.remove(callback)

    def notify_change(self, item: 'LiveConfigItem', old_value: Any, new_value: Any):
        """Notify all listeners of a change event."""

        def notify_parents(item: 'LiveConfigItem', old_value: Any, new_value: Any):
            # Propagate the change event to the parent config
            # Use is not None to avoid recursive calls to .value
            if self._parent is not None:
                self._parent.notify_change(item, old_value, new_value)

        # If there are no listeners, do nothing to save on overhead
        if len(self._event_listeners) == 0:

            # Even if there are no listeners, the parents might have listeners
            # so we need to notify them
            notify_parents(item, old_value, new_value)
            return

        event = ChangeEvent(
            item=item,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now()
        )

        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception as e:
                traceback.print_exc()
                # Log the error but don't let it break other listeners
                print(f"Error in event listener: {e}")

        # Recursively notify parents of the change upwards
        notify_parents(item, old_value, new_value)

    def clear_all_on_change(self):
        """Remove all listeners."""
        self._event_listeners.clear()
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


Listener = Callable[..., Any]


def is_same_listener(a: Any, b: Any) -> bool:
    """Treat bound methods with the same instance+function as the same listener."""
    if a is b:
        return True

    if a is None or b is None:
        return False

    a_func = getattr(a, "__func__", None)
    b_func = getattr(b, "__func__", None)
    a_self = getattr(a, "__self__", None)
    b_self = getattr(b, "__self__", None)

    # Bound methods are recreated on attribute access, so object identity is unstable.
    return (
        a_func is not None
        and b_func is not None
        and a_func is b_func
        and a_self is b_self
    )


class EventEmitter:
    def __init__(self) -> None:
        self.__events: dict[str, list[Listener]] = defaultdict(list)

    def on(self, event: str, listener: Listener) -> EventEmitter:
        self.__events[event].append(listener)
        return self

    def add_listener(self, event: str, listener: Listener) -> EventEmitter:
        return self.on(event, listener)

    def once(self, event: str, listener: Listener) -> EventEmitter:
        def wrapper(*args: Any, **kwargs: Any) -> None:
            self.off(event, wrapper)
            listener(*args, **kwargs)

        setattr(wrapper, "__original_listener__", listener)
        self.on(event, wrapper)
        return self

    def off(self, event: str, listener: Listener) -> EventEmitter:
        listeners = self.__events.get(event)
        if not listeners:
            return self

        kept: list[Listener] = []
        removed = False
        for current in listeners:
            original = getattr(current, "__original_listener__", None)
            if not removed and (
                is_same_listener(current, listener)
                or is_same_listener(original, listener)
            ):
                removed = True
                continue
            kept.append(current)

        if kept:
            self.__events[event] = kept
        else:
            self.__events.pop(event, None)

        return self

    def remove_listener(self, event: str, listener: Listener) -> EventEmitter:
        return self.off(event, listener)

    def remove_all_listeners(self, event: str | None = None) -> EventEmitter:
        if event is None:
            self.__events.clear()
        else:
            self.__events.pop(event, None)

        return self

    def listeners(self, event: str) -> list[Listener]:
        return list(self.__events.get(event, []))

    def listener_count(self, event: str) -> int:
        return len(self.__events.get(event, []))

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        listeners = list(self.__events.get(event, []))
        for listener in listeners:
            listener(*args, **kwargs)

        return bool(listeners)

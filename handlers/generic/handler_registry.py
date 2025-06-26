from __future__ import annotations

from typing import Dict, Any, Callable


class HandlerRegistry:
    __slots__ = ("_handler_registry",)

    def __init__(self) -> None:
        self._handler_registry: Dict[str, Dict[str, Any]] = {}

    def register(self, handler_alias: str, handler_type: str) -> Callable:
        def wrapper(func: Callable):
            if not isinstance(func, Callable):
                raise TypeError(
                    f"func should be an instance of 'Callable' not {type(func).__name__}"
                )
            self._handler_registry[handler_alias] = {
                "handler": func,
                "handler_type": handler_type,
            }

        return wrapper

    def get_handlers(self) -> Dict[str, Dict[str, Any]]:
        return self._handler_registry

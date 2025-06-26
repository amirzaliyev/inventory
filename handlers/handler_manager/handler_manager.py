from __future__ import annotations

import inspect
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from aiogram import Router

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import TelegramObject

    from handlers.generic import HandlerRegistry
    from utils.state_manager import StateManager


class HandlerManager:
    __slots__ = "_router", "_handler_registry"

    def __init__(
        self,
        router: Router,
    ) -> None:
        self._router = router
        self._handler_registry = {}

    def include_registry(self, handler_registry: HandlerRegistry):
        self._handler_registry.update(**handler_registry.get_handlers())

    def _create_handler(self, field_info: Dict[str, Any]) -> Callable:
        var_name = field_info["var_name"]
        next_state = field_info["next_state"]

        handler_name = field_info["handler"]
        handler_info = self._handler_registry[handler_name]
        handler = handler_info["handler"]

        @wraps(handler)
        async def new_handler(
            event: TelegramObject,
            state: FSMContext,
            state_mgr: StateManager,
            regex_res: Optional[Match] = None,
            callback_data=None,
        ):
            args = inspect.getfullargspec(handler).args
            kwargs = {
                "event": event,
                "state": state,
                "state_mgr": state_mgr,
                "callback_data": callback_data,
                "regex_res": regex_res,
            }
            kwargs.update()
            kwargs = {k: kwargs[k] for k in args if k in kwargs}

            return await handler(var_name=var_name, next_state=next_state, **kwargs)

        return new_handler

    def create_handler(self, field_info: Dict[str, Any]) -> None:
        filters = field_info["filters"]

        handler_name = field_info["handler"]
        handler_info = self._handler_registry[handler_name]
        handler_type = handler_info["handler_type"]

        handler = self._create_handler(field_info=field_info)

        event = getattr(self._router, handler_type)

        event.register(handler, *filters)

    def create_handlers(self, form: List[Dict[str, Any]]):
        for field_info in form:
            self.create_handler(field_info)

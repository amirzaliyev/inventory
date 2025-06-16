from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message


class Switch:
    def __init__(self, name: Optional[str] = None):
        if name:
            self.name = name
        self.handlers: Dict[str, Any] = {}

    def register(self, handler_key):
        """
        Registers query handlers.
        :param func: - valid function.
        """

        def wrapper(func: Callable):
            if not isinstance(func, Callable):
                raise TypeError(
                    f"func should be instance of 'Callable' not {type(func).__name__}"
                )
            self.handlers[handler_key] = func

        return wrapper


class StateManager(Switch):
    def __init__(self, **kwargs):
        """
        :param kwargs: dependencies for query handlers
        """
        super().__init__(name="State manager")
        self.kwargs = kwargs

    async def push_state_stack(self, state: FSMContext, next_state: State) -> None:
        """
        Registers new states and saves user state history

        Params
            state: FSMContext object
            next_state: State object, next state

        Returns
        """
        if not isinstance(state, FSMContext):
            raise TypeError(
                f"state should be instance of 'FSMContext' not {type(state).__name__}"
            )

        if not isinstance(next_state, State):
            raise TypeError(
                f"next_state should be an instance of 'State' not {type(next_state).__name__}"
            )

        stack = await state.get_value("state_stack", [])

        current_state = await state.get_state()

        if current_state:
            stack.append(current_state)

            await state.update_data(state_stack=stack)

        await state.set_state(next_state)

    async def _get_last_state(self, state: FSMContext) -> Optional[State]:
        """
        Retrieves the last state.

        Params
            state: FSMContext object

        Returns
            State object

        If there is no state, return None
        """
        stack = await state.get_value("state_stack", [])

        try:
            last_state = stack.pop()

            await state.update_data(state_stack=stack)
            return last_state

        except IndexError:
            return None

    async def cancel(self, message: Message, state: FSMContext) -> None:
        """Handles cancel event"""
        if not isinstance(state, FSMContext):
            raise TypeError(
                f"state should be an instance of 'FSMContext', got {type(state).__name__}"
            )

        if not isinstance(message, Message):
            raise TypeError(
                f"message should be an instance of 'Message', got {type(message).__name__}"
            )

        last_state = await self._get_last_state(state=state)

        await state.set_state(last_state)
        await self.dispatch_query(message=message, state=state)

    def include_switch(self, switch) -> None:
        """
        Registers switch to state manager
        """
        if not isinstance(switch, Switch):
            raise TypeError(
                f"switch should be instance of 'Switch' not {type(switch).__name__}"
            )
        self.handlers.update(**switch.handlers)

    async def dispatch_query(
        self,
        message: Message,
        state: FSMContext,
        edit_msg: bool = True,
    ) -> None:
        """
        whatever
        """
        if not isinstance(message, Message):
            raise TypeError(
                f"message should be an instance of 'Message' not {type(message).__name__}"
            )
        if not isinstance(state, FSMContext):
            raise TypeError(
                f"state should be an instance of 'FSMContext' not{type(state).__name__}"
            )

        current = await state.get_state()
        handler_key = "activity"
        if current is not None:
            handler_key = current.split(":")[-1]  # type: ignore

        handler = self.handlers[handler_key]
        args = inspect.getfullargspec(handler).args
        self.kwargs.update(state=state, message=message, edit_msg=edit_msg)
        params = {k: self.kwargs[k] for k in args if k in self.kwargs}

        text, reply_markup = await handler(**params)

        if edit_msg is True:
            try:
                await message.edit_text(text=text, reply_markup=reply_markup)
                return

            except TelegramBadRequest:
                pass

        await message.answer(text=text, reply_markup=reply_markup)

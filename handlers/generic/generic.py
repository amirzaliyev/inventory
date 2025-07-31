from __future__ import annotations

import asyncio
from datetime import date
from typing import TYPE_CHECKING

from aiogram_calendar import SimpleCalendar

from resources.string import CANT_SELECT_FUTURE_DATE

from .handler_registry import HandlerRegistry

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State
    from aiogram.types import CallbackQuery, Message
    from aiogram_calendar import SimpleCalendarCallback

    from utils.state_manager import StateManager

handler_registry = HandlerRegistry()


@handler_registry.register("int_regex_cb", "callback_query")
async def int_regex(
    event: CallbackQuery,
    state: FSMContext,
    regex_res: Match,
    state_mgr: StateManager,
    var_name: str,
    next_state: State,
) -> None:
    """
    Generic handler for receveiving user prompt.
    Saves the first match of regex result.

    Args:
        :param event: telegram event injected by dispatcher
        :param state: 'FSMContext' instance, injected by dispatcher
        :param regex_res: regex Match object, injected by dispatcher
        :param state_mgr: StateManager object, injected by dispatcher
        :param var_name: variable name to retrieve it later,
                injected by HandlerManager during registration
        :param next_state: next state to be set, injected by HandlerManager during registration
    """

    form_data = await state.get_value("form_data", {})
    form_data[var_name] = int(regex_res.group(1))
    await state.update_data(form_data=form_data)

    await state_mgr.push_state_stack(state, next_state)
    await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore


@handler_registry.register("int_regex_msg", "message")
async def int_regex_message(
    event: Message,
    state: FSMContext,
    regex_res: Match,
    state_mgr: StateManager,
    var_name: str,
    next_state: State,
) -> None:
    """
    Generic handler for receveiving user prompt.
    Saves the first match of regex result.

    Args:
        :param event: telegram event injected by dispatcher
        :param state: 'FSMContext' instance, injected by dispatcher
        :param regex_res: regex Match object, injected by dispatcher
        :param state_mgr: StateManager object, injected by dispatcher
        :param var_name: variable name to retrieve it later,
                injected by HandlerManager during registration
        :param next_state: next state to be set, injected by HandlerManager during registration
    """

    form_data = await state.get_value("form_data", {})
    form_data[var_name] = int(regex_res.group(1))
    await state.update_data(form_data=form_data)

    await state_mgr.push_state_stack(state, next_state)
    await state_mgr.dispatch_query(message=event, state=state)  # type: ignore


@handler_registry.register("str_regex_cb", "callback_query")
async def str_regex(
    event: CallbackQuery,
    state: FSMContext,
    regex_res: Match,
    state_mgr: StateManager,
    var_name: str,
    next_state: State,
) -> None:
    """
    Generic handler for receveiving user prompt.
    Saves the first match of regex result.

    Args:
        :param event: telegram event injected by dispatcher
        :param state: 'FSMContext' instance, injected by dispatcher
        :param regex_res: regex Match object, injected by dispatcher
        :param state_mgr: StateManager object, injected by dispatcher
        :param var_name: variable name to retrieve it later,
                injected by HandlerManager during registration
        :param next_state: next state to be set, injected by HandlerManager during registration
    """

    form_data = await state.get_value("form_data", {})
    form_data[var_name] = regex_res.group(1)
    await state.update_data(form_data=form_data)

    await state_mgr.push_state_stack(state, next_state)
    await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore


@handler_registry.register("date_picker", "callback_query")
async def process_date(
    event: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    state_mgr: StateManager,
    var_name: str,
    next_state: State,
) -> None:
    """
    Generic handler for receveiving user prompt.
    Saves the first match of regex result.

    Args:
        :param event: telegram event injected by dispatcher
        :param state: 'FSMContext' instance, injected by dispatcher
        :param callback_data: 'SimpleCalendarCallback' object, injected by dispatcher
        :param state_mgr: StateManager object, injected by dispatcher
        :param var_name: variable name to retrieve it later,
                injected by HandlerManager during registration
        :param next_state: next state to be set, injected by HandlerManager during registration
    """

    selected, date = await SimpleCalendar().process_selection(event, callback_data)

    if selected:
        form_data = await state.get_value("form_data", {})

        form_data[var_name] = date.strftime("%Y-%m-%d")
        await state.update_data(form_data=form_data)

        if date < date.today():
            await state_mgr.push_state_stack(state, next_state)

        else:
            if event.message:
                msg = await event.message.answer(text=CANT_SELECT_FUTURE_DATE)
                await asyncio.sleep(1)
                await msg.delete()

        await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore

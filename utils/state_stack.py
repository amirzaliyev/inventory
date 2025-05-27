from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State


async def push_state_stack(state: FSMContext, next_state: State) -> None:
    """
    Registers new states and saves user state history

    Params
        state: FSMContext object
        next_state: State object, next state

    Returns
    """
    stack = await state.get_value("state_stack", [])

    current_state = await state.get_state()

    if current_state:
        print(current_state)
        stack.append(current_state)

        await state.update_data(state_stack=stack)

    await state.set_state(next_state)


async def get_last_state(state: FSMContext) -> Optional[State]:
    """
    Returns last state.

    Params
        state: FSMContext object

    Raises
        IndexError if there is state available
    """
    stack = await state.get_value("state_stack", [])

    try:
        last_state = stack.pop()

        await state.update_data(state_stack=stack)
        return last_state

    except IndexError:
        return None

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.state import State


async def push_state_stack(state: FSMContext, next_state: State) -> None:
    stack = await state.get_value("state_stack", [])

    current_state = await state.get_state()

    if current_state:
        stack.append(current_state)

        await state.update_data(state_stack=stack)

    await state.set_state(next_state)

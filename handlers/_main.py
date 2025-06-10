from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, or_f

from handlers.forms import ProductionRecordForm, SalesOrderForm
from resources.string import BACK

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from utils.state_manager import StateManager

main_router = Router(name="main")


@main_router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, state_mgr: StateManager
) -> None:

    await state.set_state()
    await state.update_data(state_stack=[], new_order={})
    await state_mgr.dispatch_query(message=message, state=state)


@main_router.callback_query(F.data.regexp(r"activity_(\w+)").as_("activity_re"))
async def start_record_adding(
    callback: CallbackQuery,
    state: FSMContext,
    activity_re: Match,
    state_mgr: StateManager,
) -> None:
    activity = activity_re.group(1)
    next_state = SalesOrderForm.branch_id

    if activity == "production":
        next_state = ProductionRecordForm.branch_id

    await state_mgr.push_state_stack(state=state, next_state=next_state)

    await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@main_router.callback_query(or_f(F.data == BACK, Command("cancel")))
async def cancel(
    callback: CallbackQuery, state: FSMContext, state_mgr: StateManager
) -> None:
    await state_mgr.cancel(message=callback.message, state=state)  # type: ignore
    # last_state = await state_mgr._get_last_state(state=state)
    #
    # if last_state:
    #     await state.set_state(last_state)
    #     text, kb = await dispatch_state(
    #         state=state, branch_repo=branch_repo, emp_repo=emp_repo
    #     )
    #     await callback.message.edit_text(text=text, reply_markup=kb)  # type: ignore
    #
    # else:
    #     msg = await callback.message.edit_text(CANCELLED_BACK_TO_START)  # type: ignore
    #     await asyncio.sleep(0.75)
    #     await msg.delete()  # type: ignore
    #
    #     await cmd_start(message=callback.message, state=state, user_repo=user_repo)

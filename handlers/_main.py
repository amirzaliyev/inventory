from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, or_f

from handlers.forms import ProductionRecordForm, SalesOrderForm, dispatch_state
from keyboards import current_action_kb
from resources.string import BACK, CANCELLED_BACK_TO_START, WELCOME_TEXT
from utils.state_stack import push_state_stack

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from data.repositories import IBranchRepository, IEmployeeRepository

main_router = Router(name="main")


@main_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=current_action_kb())
    await state.clear()


@main_router.callback_query(F.data.regexp(r"activity_(\w+)").as_("activity_re"))
async def start_record_adding(
    callback: CallbackQuery,
    state: FSMContext,
    branch_repo: IBranchRepository,
    activity_re: Match,
) -> None:
    activity = activity_re.group(1)
    if activity == "sales":
        await push_state_stack(state=state, next_state=SalesOrderForm.branch_id)

    elif activity == "production":
        await push_state_stack(state=state, next_state=ProductionRecordForm.branch_id)

    text, reply_markup = await dispatch_state(state=state, branch_repo=branch_repo)

    await callback.message.edit_text(text=text, reply_markup=reply_markup)  # type: ignore


@main_router.callback_query(or_f(F.data == BACK, Command("cancel")))
@main_router.callback_query(F.data == "simple_calendar:cancel")
async def cancel(
    callback: CallbackQuery,
    state: FSMContext,
    branch_repo: IBranchRepository,
    emp_repo: IEmployeeRepository,
) -> None:
    stack = await state.get_value("state_stack", [])

    if stack:
        last_state = stack.pop()
        await push_state_stack(state=state, next_state=last_state)
        text, kb = await dispatch_state(
            state=state, branch_repo=branch_repo, emp_repo=emp_repo
        )
        await callback.message.edit_text(text=text, reply_markup=kb)  # type: ignore

    else:
        msg = await callback.message.edit_text(CANCELLED_BACK_TO_START)  # type: ignore
        await asyncio.sleep(0.75)
        await msg.delete()  # type: ignore

        await cmd_start(message=callback.message, state=state)

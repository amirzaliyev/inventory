from __future__ import annotations

import calendar
import datetime
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile

from resources.dicts import months
from resources.string import CALCULATING, NO_RECORDS
from utils.state_manager import StateManager
from utils.visualize import make_df, make_human_readable, to_pdf

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from core.accounting import Accounting

accounting_router = Router(name="accounting")


class AccountingForm(StatesGroup):
    branch_id = State()
    period = State()


@accounting_router.message(Command("oylik"))
async def select_branch(
    message: Message,
    state: FSMContext,
    state_mgr: StateManager,
) -> None:
    await state.update_data(state_stack=[], salary_form={})

    await state_mgr.push_state_stack(state, AccountingForm.branch_id)

    await state_mgr.dispatch_query(message=message, state=state)


@accounting_router.callback_query(
    AccountingForm.branch_id, F.data.regexp(r"branch_(\d+)").as_("branch_id_re")
)
async def select_month(
    callback: CallbackQuery,
    state: FSMContext,
    branch_id_re: Match,
    state_mgr: StateManager,
) -> None:
    await state_mgr.push_state_stack(state, AccountingForm.period)

    salary_form = {"branch_id": int(branch_id_re.group(1))}
    await state.update_data(salary_form=salary_form)

    await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@accounting_router.callback_query(
    AccountingForm.period, F.data.regexp(r"month_(\d{1,2})").as_("month_re")
)
async def calculate_salary(
    callback: CallbackQuery, state: FSMContext, month_re: Match, accounting: Accounting
) -> None:
    month = int(month_re.group(1))
    salary_form = await state.get_value("salary_form", {})
    branch_id = salary_form["branch_id"]
    last_day = calendar.monthrange(2025, month)[1]

    period = {
        "date_from": datetime.date(2025, month, 1),
        "date_to": datetime.date(2025, month, last_day),
    }
    msg = await callback.message.edit_text(text=CALCULATING.format(months[month]))  # type: ignore
    data = accounting.calculate_salary(branch_id=branch_id, period=period)

    details = data["details"]
    if not details:
        await callback.message.edit_text(text=NO_RECORDS)  # type: ignore
        return

    df = make_df(details)
    df = make_human_readable(df)
    file_path, thumbnail_path = to_pdf(
        title=f"Oylik {branch_id}-seh", df=df, period=period, figsize=(16, 10)
    )

    df_summary = make_df(
        [
            {"Name": key, "Salary": int(round(value, -3))}
            for key, value in data["summary"].items()
        ]
    )  # todo clean the mess
    df_summary_sorted = df_summary.sort_values(
        by="Salary", ascending=True
    )  # todo find better way to put 'Total' at end of the table :)
    df_summary_sorted = make_human_readable(df_summary_sorted)
    sum_file_path, sum_thumbnail_path = to_pdf(
        title=f"Oylik {branch_id}-seh (Qisqacha)", df=df_summary_sorted, period=period
    )

    file = FSInputFile(file_path)
    thumbnail = FSInputFile(thumbnail_path)

    sum_file = FSInputFile(sum_file_path)
    sum_thumbnail = FSInputFile(sum_thumbnail_path)

    await callback.message.answer_document(document=file, thumbnail=thumbnail)  # type: ignore
    await callback.message.answer_document(  # type: ignore
        document=sum_file, thumbnail=sum_thumbnail
    )
    await msg.delete()  # type: ignore
    await state.set_state()
    await state.update_data(salary_form={})

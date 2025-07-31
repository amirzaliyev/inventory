from __future__ import annotations

import calendar
import datetime
from typing import TYPE_CHECKING, Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile

from handlers.generic import handler_registry
from handlers.handler_manager.handler_manager import HandlerManager
from resources.dicts import months
from resources.string import CALCULATING_SALARY, NO_RECORDS, SALARY
from utils.visualize import make_df, make_human_readable, to_pdf

from .forms import AccountingForm, SalaryForm

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from core.accounting import Accounting
    from utils.state_manager import StateManager

salary_router = Router(name="salary")


SALARYFORM = [
    {
        "var_name": "branch_id",
        "next_state": SalaryForm.period,
        "handler": "int_regex_cb",
        "filters": (
            SalaryForm.branch_id,
            F.data.regexp(r"branch_(\d+)").as_("regex_res"),
        ),
    }
]

_handler_mgr = HandlerManager(router=salary_router)
_handler_mgr.include_registry(handler_registry)
_handler_mgr.create_handlers(SALARYFORM)


@salary_router.message(Command("oylik"))
@salary_router.callback_query(AccountingForm.accounting_menu, F.data == SALARY)
async def select_branch(
    event: Union[Message, CallbackQuery],
    state: FSMContext,
    state_mgr: StateManager,
) -> None:
    await state.update_data(state_stack=[], form_data={}, extras={})

    await state_mgr.push_state_stack(state, SalaryForm.branch_id)

    if isinstance(event, CallbackQuery):
        if event.message:
            await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore
            return

    await state_mgr.dispatch_query(message=event, state=state)  # type: ignore


@salary_router.callback_query(
    SalaryForm.period, F.data.regexp(r"month_(\d{1,2})").as_("month_re")
)
async def calculate_salary(
    callback: CallbackQuery, state: FSMContext, month_re: Match, accounting: Accounting
) -> None:
    month = int(month_re.group(1))
    form_data = await state.get_value("form_data", {})
    branch_id = form_data["branch_id"]
    last_day = calendar.monthrange(2025, month)[1]

    period = {
        "date_from": datetime.date(2025, month, 1),
        "date_to": datetime.date(2025, month, last_day),
    }
    msg = await callback.message.edit_text(  # type: ignore
        text=CALCULATING_SALARY.format(months[month])
    )
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
    await state.update_data(form_data={})

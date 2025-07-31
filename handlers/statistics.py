from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from handlers.generic import handler_registry
from handlers.handler_manager.handler_manager import HandlerManager
from resources.string import PREPARING_REPORT, REPORT_READY, TOTAL
from utils.state_manager import StateManager
from utils.stats import get_period
from utils.visualize import make_df, make_human_readable, to_pdf

from .forms import StatisticsForm

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from data.repositories import IOrderRepository, IProductionRecordRepository

stat_router = Router(name="statistics")

STATISTICSFORM = [
    {
        "var_name": "activity",
        "handler": "str_regex_cb",
        "next_state": StatisticsForm.stat_period,
        "filters": (
            StatisticsForm.activity,
            F.data.regexp(r"activity_(\w+)").as_("regex_res"),
        ),
    }
]

_handler_mgr = HandlerManager(router=stat_router)
_handler_mgr.include_registry(handler_registry)
_handler_mgr.create_handlers(STATISTICSFORM)



@stat_router.message(Command("stats"))
async def select_activity(
    message: Message,
    state: FSMContext,
    state_mgr: StateManager,
) -> None:
    await state.update_data(state_stack=[], form_data={}, extras={})
    await state_mgr.push_state_stack(state, StatisticsForm.activity)
    await state_mgr.dispatch_query(message=message, state=state)


@stat_router.callback_query(
    StatisticsForm.stat_period, F.data.regexp(r"period_(\w+)").as_("period_re")
)
async def show_report(
    callback: CallbackQuery,
    state: FSMContext,
    prod_record_repo: IProductionRecordRepository,
    order_repo: IOrderRepository,
    period_re: Match,
) -> None:
    period_title = period_re.group(1)
    period = get_period(period_title=period_title)

    form_data = await state.get_value("form_data", {})
    activity = form_data.get("activity", "")
    title = "Ishlab chiqarish"
    headers = ["Nomi", "Soni"]
    col_order = ["name", "total_count"]
    result = []

    if activity == "production":

        result = prod_record_repo.stat(**period)
        headers.append("Ishlatilgan sement")
        col_order.append("used_cement_amount")

    elif activity == "sales":
        title = "Sotuv"
        result = order_repo.filter(**period)
        col_order.append("total_amount")
        headers.append("Summa")

    df = make_df(data=result, col_order=col_order, column_names=headers, sort_by="Soni")

    if activity == "sales":

        total_row = make_df(
            data=[{"Nomi": TOTAL, "Soni": "", "Summa": df["Summa"].sum()}]
        )
        df = pd.concat([df, total_row])

    df = make_human_readable(df=df)
    report_pdf_path, thumbnail_path = to_pdf(
        df=df, title=title, period=period, figsize=(12, 4)
    )

    file = FSInputFile(report_pdf_path)
    thumbnail = FSInputFile(thumbnail_path)

    msg = await callback.message.edit_text(text=PREPARING_REPORT)  # type: ignore
    await callback.message.answer_document(file, thumbnail=thumbnail)  # type: ignore
    await msg.delete()  # type: ignore
    await callback.message.answer(text=REPORT_READY)  # type: ignore

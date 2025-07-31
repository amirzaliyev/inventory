from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from aiogram import F, Router
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import settings
from data.models import Attendance, ProductionRecord
from handlers.forms import ProductionRecordForm
from handlers.generic import handler_registry
from handlers.handler_manager import HandlerManager
from keyboards import save_kb
from resources.string import READY, SAVE, SUCCESSFULLY_SAVED

if TYPE_CHECKING:
    from re import Match

    from aiogram import Bot
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery

    from data.repositories import (
        IBranchRepository,
        IProductionRecordRepository,
        IProductRepository,
    )
    from utils.state_manager import StateManager


production_router = Router(name="production")


PRODUCTIONRECORDFORM = [
    {
        "var_name": "branch_id",
        "handler": "int_regex_cb",
        "next_state": ProductionRecordForm.date,
        "filters": (
            ProductionRecordForm.branch_id,
            F.data.regexp(r"branch_(\d+)").as_("regex_res"),
        ),
    },
    {
        "var_name": "date",
        "handler": "date_picker",
        "next_state": ProductionRecordForm.product_id,
        "filters": (ProductionRecordForm.date, SimpleCalendarCallback.filter()),
    },
    {
        "var_name": "product_id",
        "handler": "int_regex_cb",
        "next_state": ProductionRecordForm.quantity,
        "filters": (
            ProductionRecordForm.product_id,
            F.data.regexp(r"product_(\d+)").as_("regex_res"),
        ),
    },
    {
        "var_name": "quantity",
        "handler": "int_regex_msg",
        "next_state": ProductionRecordForm.used_cement_amount,
        "filters": (
            ProductionRecordForm.quantity,
            F.text.regexp(r"^(\d+)$").as_("regex_res"),
        ),
    },
    {
        "var_name": "used_cement_amount",
        "handler": "int_regex_msg",
        "next_state": ProductionRecordForm.workers,
        "filters": (
            ProductionRecordForm.used_cement_amount,
            F.text.regexp(r"^(\d+)$").as_("regex_res"),
        ),
    },
]

_handler_mgr = HandlerManager(router=production_router)
_handler_mgr.include_registry(handler_registry)
_handler_mgr.create_handlers(form=PRODUCTIONRECORDFORM)


async def process_date(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    state_mgr: StateManager,
) -> None:
    """Processes  the selected date"""
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        form_data = await state.get_value("form_data", {})

        form_data["date"] = date.strftime("%Y-%m-%d")
        await state.update_data(form_data=form_data)

        await state_mgr.push_state_stack(state, ProductionRecordForm.product_id)
        await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@production_router.callback_query(
    ProductionRecordForm.workers,
    F.data.regexp(r"^worker_(\d+)$").as_("worker_id_re"),
)
async def process_workers(
    callback: CallbackQuery,
    state: FSMContext,
    worker_id_re: Match,
    state_mgr: StateManager,
) -> None:
    """Processes the workers on duty"""
    worker_id = int(worker_id_re.group(1))

    present_employees = await state.get_value("present_employees", set())

    if worker_id in present_employees:
        present_employees.remove(worker_id)

    else:
        present_employees.add(worker_id)

    await state.update_data(present_employees=present_employees)

    await state_mgr.dispatch_query(
        message=callback.message,  # type: ignore
        state=state,
    )


@production_router.callback_query(ProductionRecordForm.workers, F.data == READY)
async def show_summary(
    callback: CallbackQuery,
    state: FSMContext,
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
    state_mgr: StateManager,
) -> None:
    """
    Shows the summary of new record.
    Asks permission to further proceed (save to db) or
    to cancel the transaction.
    """
    data = await state.get_data()
    await state_mgr.push_state_stack(state, ProductionRecordForm.save)

    form_data = data.get("form_data", {})
    extras = data.get("extras", {})
    present_employees = extras.get("present_employees", set())

    message = summary_message(
        data=form_data,
        branch_repo=branch_repo,
        product_repo=product_repo,
        present_employees=present_employees,
    )
    extras.update(message=message)
    await state.update_data(extras=extras)

    await callback.message.edit_text(text=message, reply_markup=save_kb())  # type: ignore


@production_router.callback_query(ProductionRecordForm.save, F.data == SAVE)
async def save_to_db(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    prod_record_repo: IProductionRecordRepository,
):
    data = await state.get_data()
    await state.update_data(form_data={}, state_stack=[])
    await state.set_state()

    form_data = data["form_data"]
    present_employees = data["extras"]["present_employees"]
    message = data["extras"]["message"]
    _save_to_db(
        repository=prod_record_repo,
        form_data=form_data,
        workers=present_employees,
    )
    await bot.send_message(settings.SUPER_ADMIN, text=message)
    await callback.message.edit_text(text=message)  # type: ignore
    await callback.message.answer(text=SUCCESSFULLY_SAVED)  # type: ignore


def summary_message(
    data: Dict[str, Any],
    present_employees: List[int],
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
):
    message = "<b>Ishlab chiqarish</b>\n\n"
    branch = branch_repo.get_by_id(data["branch_id"])
    product = product_repo.get_by_id(data["product_id"])
    date = datetime.strptime(data["date"], "%Y-%m-%d").strftime("%d.%m.%Y")

    message += f"Bo'lim nomi: <blockquote>{branch.name}</blockquote>\n"
    message += f"Sana: <blockquote>{date}</blockquote>\n"
    message += f"Mahsulot nomi: <blockquote>{product.name}</blockquote>\n"
    message += f"Soni: <blockquote>{data['quantity']}</blockquote>\n"
    message += f"Ishlatilgan sement: <blockquote>{data['used_cement_amount']} kg</blockquote>\n"
    message += f"Ishchilar soni: <blockquote>{len(present_employees)}</blockquote>"

    return message


def _save_to_db(
    repository: IProductionRecordRepository,
    form_data: Dict[str, Any],
    workers: List[int],
) -> None:
    new_record_obj = ProductionRecord(**form_data)

    new_inserted_record = repository.create_record(new_record=new_record_obj)

    attendance_records = []
    for worker in workers:
        attendance_records.append(
            Attendance(employee_id=worker, production_record_id=new_inserted_record.id)
        )

        repository.create_attendance_record(new_records=attendance_records)

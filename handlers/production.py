from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from aiogram import F, Router
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import settings
from data.models import Attendance, ProductionRecord
from handlers.forms import ProductionRecordForm
from keyboards import (back_kb, products_kb, save_kb, select_date_kb,
                       workers_on_duty_kb)
from resources.string import (ATTENDANCE, MANUFACTURED_PRODUCT_QUANTITY, READY,
                              SAVE, SELECT_DATE, SELECT_PRODUCT,
                              SUCCESSFULLY_SAVED, USED_CEMENT_AMOUNT)
from utils.state_stack import push_state_stack

if TYPE_CHECKING:
    from re import Match

    from aiogram import Bot
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from data.repositories import (IBranchRepository, IEmployeeRepository,
                                   IProductionRecordRepository,
                                   IProductRepository)


production_router = Router(name="production")


@production_router.callback_query(
    ProductionRecordForm.branch_id, F.data.regexp(r"branch_(\d+)").as_("digits")
)
async def select_branch(
    callback: CallbackQuery, state: FSMContext, digits: Match
) -> None:
    """Processes the selected branch and shows its production line"""

    new_record = {"branch_id": int(digits.group(1))}
    await state.update_data(new_record=new_record)

    await push_state_stack(state, ProductionRecordForm.date)

    await callback.message.edit_text(  # type: ignore
        text=SELECT_DATE, reply_markup=await select_date_kb()
    )


@production_router.callback_query(
    ProductionRecordForm.date, SimpleCalendarCallback.filter()
)
async def process_date(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    branch_repo: IBranchRepository,
) -> None:
    """Processes  the selected date"""
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        new_record = await state.get_value("new_record", {})

        new_record["date"] = date.strftime("%Y-%m-%d")
        await state.update_data(new_record=new_record)

        await push_state_stack(state, ProductionRecordForm.product_id)
        branch_id = new_record["branch_id"]

        # load product from database
        products = branch_repo.get_branch_products(branch_id=branch_id)

        await callback.message.edit_text(  # type: ignore
            text=SELECT_PRODUCT, reply_markup=products_kb(products=products)
        )


@production_router.callback_query(
    ProductionRecordForm.product_id,
    F.data.regexp(r"product_(\d+)").as_("product_id_re"),
)
async def process_product(
    callback: CallbackQuery,
    state: FSMContext,
    product_id_re: Match,
    product_repo: IProductRepository,
) -> None:
    """Processes the selected product"""
    new_record = await state.get_value("new_record", {})
    product_id = int(product_id_re.group(1))

    product_name = product_repo.get_by_id(product_id=product_id).name
    new_record["product_id"] = product_id

    await state.update_data(new_record=new_record, product_name=product_name)

    await push_state_stack(state, ProductionRecordForm.quantity)

    await callback.message.edit_text(  # type: ignore
        text=MANUFACTURED_PRODUCT_QUANTITY.format(product_name), reply_markup=back_kb()
    )


@production_router.message(
    ProductionRecordForm.quantity, F.text.regexp(r"^(\d+)$").as_("quantity_re")
)
async def process_quantity(message: Message, state: FSMContext, quantity_re: Match):
    """Processes the quantity of manufactured goods"""
    data = await state.get_data()
    new_record = data.get("new_record", {})
    product_name = data.get("product_name", "")

    new_record["quantity"] = int(quantity_re.group(1))
    await state.update_data(new_record=new_record)

    await push_state_stack(state, ProductionRecordForm.used_cement_amount)

    await message.answer(
        text=USED_CEMENT_AMOUNT.format(product_name), reply_markup=back_kb()
    )


@production_router.message(
    ProductionRecordForm.used_cement_amount,
    F.text.regexp(r"^(\d+)$").as_("used_cement_amount_re"),
)
async def process_cement_amount(
    message: Message,
    state: FSMContext,
    used_cement_amount_re: Match,
    emp_repo: IEmployeeRepository,
) -> None:
    """Processes the used cement for the production"""
    await push_state_stack(state, ProductionRecordForm.workers)

    new_record = await state.get_value("new_record", {})

    new_record["used_cement_amount"] = int(used_cement_amount_re.group(1))
    branch_id = new_record["branch_id"]

    # set present employees
    workers = emp_repo.all(branch_id=branch_id)
    present_employees = set(worker.id for worker in workers)

    await state.update_data(
        workers=workers,
        present_employees=present_employees,
        new_record=new_record,
    )

    await message.answer(
        text=ATTENDANCE,
        reply_markup=workers_on_duty_kb(
            workers=workers, present_employees=present_employees
        ),
    )


@production_router.callback_query(
    ProductionRecordForm.workers,
    F.data.regexp(r"^worker_(\d+)$").as_("worker_id_re"),
)
async def process_workers(
    callback: CallbackQuery, state: FSMContext, worker_id_re: Match
) -> None:
    """Processes the workers on duty"""
    await push_state_stack(state, ProductionRecordForm.workers)
    worker_id = int(worker_id_re.group(1))

    data = await state.get_data()
    present_employees = data.get("present_employees", set())
    workers = data.get("workers", [])

    if worker_id in present_employees:
        present_employees.remove(worker_id)

    else:
        present_employees.add(worker_id)

    await state.update_data(present_employees=present_employees)

    await callback.message.edit_text(  # type: ignore
        text=ATTENDANCE,
        reply_markup=workers_on_duty_kb(
            workers=workers, present_employees=present_employees
        ),
    )


@production_router.callback_query(ProductionRecordForm.workers, F.data == READY)
async def show_summary(
    callback: CallbackQuery,
    state: FSMContext,
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
) -> None:
    """
    Shows the summary of new record.
    Asks permission to further proceed (save to db) or
    to cancel the transaction.
    """
    data = await state.get_data()
    await push_state_stack(state, ProductionRecordForm.save)

    new_record = data["new_record"]
    present_employees = data["present_employees"]

    message = summary_message(
        data=new_record,
        branch_repo=branch_repo,
        product_repo=product_repo,
        present_employees=present_employees,
    )
    await state.update_data(message=message)

    await callback.message.edit_text(text=message, reply_markup=save_kb())  # type: ignore


@production_router.callback_query(ProductionRecordForm.save, F.data == SAVE)
async def save_to_db(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    prod_record_repo: IProductionRecordRepository,
):
    data = await state.get_data()
    await state.update_data(new_record={}, state_stack=[])
    await state.set_state()

    new_record = data["new_record"]
    present_employees = data["present_employees"]
    message = data["message"]
    _save_to_db(
        repository=prod_record_repo,
        new_record=new_record,
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
    new_record: Dict[str, Any],
    workers: List[int],
) -> None:
    new_record_obj = ProductionRecord(**new_record)

    new_inserted_record = repository.create_record(new_record=new_record_obj)

    attendance_records = []
    for worker in workers:
        attendance_records.append(
            Attendance(employee_id=worker, production_record_id=new_inserted_record.id)
        )

        repository.create_attendance_record(new_records=attendance_records)

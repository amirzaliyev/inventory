from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from handlers.forms import ProductionRecordForm, SalesOrderForm
from keyboards import back_kb, products_kb, select_date_kb
from resources.string import SELECT_DATE, SELECT_PRODUCT, SOLD_PRODUCT_QUANTITY
from utils import push_state_stack

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery

    from data.repositories import IBranchRepository, IProductRepository


async def select_date(callback: CallbackQuery, state: FSMContext, branch_id_re: Match):
    """Processes the selected branch and shows its product line"""

    await push_state_stack(state, ProductionRecordForm.date)
    await push_state_stack(state, SalesOrderForm.date)

    new_record = {"branch_id": int(branch_id_re.group(1))}
    await state.update_data(new_record=new_record)

    await callback.message.edit_text(  # type: ignore
        text=SELECT_DATE, reply_markup=await select_date_kb()
    )


async def select_branch(
    callback: CallbackQuery, state: FSMContext, digits: Match
) -> None:
    """Processes the selected branch and shows its product line"""

    new_record = {"branch_id": int(digits.group(1))}
    await state.update_data(new_record=new_record)

    await push_state_stack(state, ProductionRecordForm.date)

    await callback.message.edit_text(  # type: ignore
        text=SELECT_DATE, reply_markup=await select_date_kb()
    )


async def show_products(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    branch_repo: IBranchRepository,
):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        new_record = await state.get_value("new_record", {})
        new_record["date"] = date.strftime("%Y-%m-%d")
        await state.update_data(new_record=new_record)

        await push_state_stack(state, SalesOrderForm.product_id)

        branch_id = new_record["branch_id"]

        # load product from database
        products = branch_repo.get_branch_products(branch_id=branch_id)

        await callback.message.edit_text(  # type: ignore
            text=SELECT_PRODUCT, reply_markup=products_kb(products=products)
        )


async def get_quantity(
    callback: CallbackQuery,
    state: FSMContext,
    product_id_re: Match,
    product_repo: IProductRepository,
):
    await push_state_stack(state, SalesOrderForm.quantity)

    new_record = await state.get_value("new_record", {})
    product_id = int(product_id_re.group(1))
    product_name = product_repo.get_by_id(product_id=product_id).name

    new_record["product_id"] = product_id
    await state.update_data(new_record=new_record, product_name=product_name)

    await callback.message.edit_text(  # type: ignore
        text=SOLD_PRODUCT_QUANTITY.format(product_name), reply_markup=back_kb()
    )

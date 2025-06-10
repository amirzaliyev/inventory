from __future__ import annotations

from datetime import datetime
from re import Match
from typing import TYPE_CHECKING, Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import callback_query
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from data.models import Order
from handlers import dispatch_state
from handlers.forms import SalesOrderForm
from handlers.notifications import send_message_to_admin
from keyboards import back_kb, save_kb
from resources.string import SAVE, SOLD_PRODUCT_PRICE, SUCCESSFULLY_SAVED
from utils import push_state_stack
from utils.state_manager import StateManager

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery, Message

    from data.repositories import (IBranchRepository, IOrderRepository,
                                   IProductRepository)


sales_router = Router(name="sales")


@sales_router.callback_query(
    SalesOrderForm.branch_id, F.data.regexp(r"^branch_(\d+)$").as_("branch_id_re")
)
async def select_date(
    callback: CallbackQuery,
    state: FSMContext,
    branch_id_re: Match,
    state_mgr: StateManager,
):
    await state_mgr.push_state_stack(state, SalesOrderForm.date)
    new_record = {"branch_id": int(branch_id_re.group(1))}

    await state.update_data(new_record=new_record)

    await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@sales_router.callback_query(SalesOrderForm.date, SimpleCalendarCallback.filter())
async def show_products(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    branch_repo: IBranchRepository,
    state_mgr: StateManager,
):

    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        new_record = await state.get_value("new_record", {})
        new_record["date"] = date.strftime("%Y-%m-%d")
        await state.update_data(new_record=new_record)

        await state_mgr.push_state_stack(state, SalesOrderForm.product_id)

        await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@sales_router.callback_query(
    SalesOrderForm.product_id, F.data.regexp(r"^product_(\d+)$").as_("product_id_re")
)
async def get_quantity(
    callback: CallbackQuery,
    state: FSMContext,
    product_id_re: Match,
    product_repo: IProductRepository,
    state_mgr: StateManager,
) -> None:

    new_record = await state.get_value("new_record", {})
    product_id = int(product_id_re.group(1))
    product_name = product_repo.get_by_id(product_id=product_id).name

    new_record["product_id"] = product_id

    await state.update_data(new_record=new_record, product_name=product_name)

    await state_mgr.push_state_stack(state, SalesOrderForm.quantity)

    await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


@sales_router.message(
    SalesOrderForm.quantity, F.text.regexp(r"^(\d+)$").as_("quantity_re")
)
async def get_price(
    message: Message, state: FSMContext, quantity_re: Match, state_mgr: StateManager
) -> None:

    data = await state.get_data()
    new_record = data["new_record"]
    product_name = data["product_name"]

    new_record["quantity"] = int(quantity_re.group(1))

    await state.update_data(new_record=new_record)
    await state_mgr.push_state_stack(state, SalesOrderForm.price)

    # await state_mgr.dispatch_query(message=message, state=state)  # type: ignore
    await message.answer(
        text=SOLD_PRODUCT_PRICE.format(product_name), reply_markup=back_kb()
    )


@sales_router.message(SalesOrderForm.price, F.text.regexp(r"^(\d+)$").as_("price_re"))
async def show_summary(
    message: Message,
    state: FSMContext,
    price_re: Match,
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
    state_mgr: StateManager,
) -> None:
    await state_mgr.push_state_stack(state, SalesOrderForm.save)

    new_record = await state.get_value("new_record", {})

    price = int(price_re.group(1))
    new_record["price"] = price
    new_record["total_amount"] = price * new_record["quantity"]

    summary_msg = new_record_details(
        new_record=new_record, branch_repo=branch_repo, product_repo=product_repo
    )
    await state.update_data(new_record=new_record, message=summary_msg)

    await message.answer(summary_msg, reply_markup=save_kb())


@sales_router.callback_query(SalesOrderForm.save, F.data == SAVE)
async def save_to_db(
    callback: CallbackQuery, bot: Bot, state: FSMContext, order_repo: IOrderRepository
) -> None:
    new_record = await state.get_value("new_record", {})
    message = await state.get_value("message", "")
    await state.update_data(new_record={}, state_stack=[])
    await state.set_state()

    # Save to db
    _save_to_db(new_record=new_record, order_repo=order_repo)
    await send_message_to_admin(bot=bot, context=message)

    await callback.message.edit_text(text=message)  # type: ignore
    await callback.message.answer(text=SUCCESSFULLY_SAVED)  # type: ignore


def _save_to_db(new_record: Dict[str, Any], order_repo: IOrderRepository) -> None:
    new_order = Order(**new_record)

    order_repo.create_new(new_order)


def new_record_details(
    new_record: Dict[str, Any],
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
) -> str:
    msg = "<b>Sotuv</b>\n\n"
    branch = branch_repo.get_by_id(branch_id=new_record["branch_id"])
    product = product_repo.get_by_id(product_id=new_record["product_id"])
    date = datetime.strptime(new_record["date"], "%Y-%m-%d").strftime("%d.%m.%Y")

    msg += f"Bo'lim: <blockquote>{branch.name}</blockquote>\n"
    msg += f"Sana: <blockquote>{date}</blockquote>\n"
    msg += f"Mahsulot nomi: <blockquote>{product.name}</blockquote>\n"
    msg += f"Mahsulot soni: <blockquote>{new_record['quantity']}</blockquote>\n"
    msg += f"Mahsulot narxi: <blockquote>{new_record['price']} so'm</blockquote>\n"
    msg += f"Jami summa: <blockquote>{new_record['total_amount']:,} so'm</blockquote>\n"

    return msg

from __future__ import annotations

from datetime import datetime
from re import Match
from typing import TYPE_CHECKING, Any, Dict

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from data.models import Order
from handlers.forms import SalesOrderForm
from handlers.generic import handler_registry
from handlers.handler_manager.handler_manager import HandlerManager
from handlers.notifications import send_message_to_admin
from keyboards import save_kb
from resources.string import ADD_PRODUCT, SAVE, SUCCESSFULLY_SAVED
from utils.state_manager import StateManager

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import CallbackQuery, Message

    from data.repositories import (IBranchRepository, IOrderRepository,
                                   IProductRepository)


sales_router = Router(name="sales")

SALESORDERFORM = [
    {
        "var_name": "branch_id",
        "handler": "int_regex_cb",
        "next_state": SalesOrderForm.date,
        "filters": (
            SalesOrderForm.branch_id,
            F.data.regexp(r"branch_(\d+)").as_("regex_res"),
        ),
    },
    {
        "var_name": "date",
        "handler": "date_picker",
        "next_state": SalesOrderForm.product_id,
        "filters": (SalesOrderForm.date, SimpleCalendarCallback.filter()),
    },
    {
        "var_name": "product_id",
        "handler": "int_regex_cb",
        "next_state": SalesOrderForm.quantity,
        "filters": (
            SalesOrderForm.product_id,
            F.data.regexp(r"product_(\d+)").as_("regex_res"),
        ),
    },
    {
        "var_name": "quantity",
        "handler": "int_regex_msg",
        "next_state": SalesOrderForm.price,
        "filters": (
            SalesOrderForm.quantity,
            F.text.regexp(r"^(\d+)$").as_("regex_res"),
        ),
    },
]

_handler_mgr = HandlerManager(router=sales_router)
_handler_mgr.include_registry(handler_registry)
_handler_mgr.create_handlers(form=SALESORDERFORM)


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

    form_data = await state.get_value("form_data", {})

    price = int(price_re.group(1))
    form_data["price"] = price
    form_data["total_amount"] = price * form_data["quantity"]

    summary_msg = new_record_details(
        new_record=form_data, branch_repo=branch_repo, product_repo=product_repo
    )
    await state.update_data(form_data=form_data, message=summary_msg)

    await message.answer(summary_msg, reply_markup=save_kb(add_extra=True))


@sales_router.callback_query(SalesOrderForm.save, F.data == SAVE)
async def save_to_db(
    callback: CallbackQuery, bot: Bot, state: FSMContext, order_repo: IOrderRepository
) -> None:
    data = await state.get_data()
    form_data = data.get("form_data", {})
    orders = data.get("orders", [])
    message = await state.get_value("message", "")
    await state.update_data(form_data={}, state_stack=[], orders=[])
    await state.set_state()

    # Save to db
    if orders:
        for order in orders:
            _save_to_db(new_record=order, order_repo=order_repo)
            await send_message_to_admin(bot=bot, context=message)

    _save_to_db(new_record=form_data, order_repo=order_repo)
    await send_message_to_admin(bot=bot, context=message)

    await callback.message.edit_text(text=message)  # type: ignore
    await callback.message.answer(text=SUCCESSFULLY_SAVED)  # type: ignore


def _save_to_db(new_record: Dict[str, Any], order_repo: IOrderRepository) -> None:
    new_order = Order(**new_record)

    order_repo.create_new(new_order)


@sales_router.callback_query(SalesOrderForm.save, F.data == ADD_PRODUCT)
async def add_more(
    callback: CallbackQuery, state: FSMContext, state_mgr: StateManager
) -> None:
    data = await state.get_data()
    orders = data.get("orders", [])
    new_record = data.get("form_data", {})
    orders.append(new_record)

    await state.update_data(orders=orders)
    await state_mgr.push_state_stack(state, SalesOrderForm.product_id)
    await state_mgr.dispatch_query(message=callback.message, state=state)  # type: ignore


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

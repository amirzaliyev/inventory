from datetime import datetime
from re import Match
from typing import Any, Dict

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from data.models import Order
from data.repositories import (IBranchRepository, IOrderRepository,
                               IProductRepository)
from handlers.forms import SalesOrderForm
from handlers.notifications import send_message_to_admin
from keyboards import back_kb, products_kb, save_kb, select_date_kb
from resources.string import (SAVE, SELECT_DATE, SELECT_PRODUCT,
                              SOLD_PRODUCT_PRICE, SOLD_PRODUCT_QUANTITY,
                              SUCCESSFULLY_SAVED)
from utils import push_state_stack

sales_router = Router(name="sales")


@sales_router.callback_query(
    SalesOrderForm.branch_id, F.data.regexp(r"^branch_(\d+)$").as_("branch_id_re")
)
async def select_date(callback: CallbackQuery, state: FSMContext, branch_id_re: Match):
    await push_state_stack(state, SalesOrderForm.date)
    order = {"branch_id": int(branch_id_re.group(1))}

    await state.update_data(order=order)

    await callback.message.edit_text(  # type: ignore
        text=SELECT_DATE, reply_markup=await select_date_kb()
    )


@sales_router.callback_query(SalesOrderForm.date, SimpleCalendarCallback.filter())
async def show_products(
    callback: CallbackQuery,
    state: FSMContext,
    callback_data: SimpleCalendarCallback,
    branch_repo: IBranchRepository,
):

    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        order = await state.get_value("order", {})
        order["date"] = date.strftime("%Y-%m-%d")
        await state.update_data(order=order)

        await push_state_stack(state, SalesOrderForm.product_id)

        branch_id = order["branch_id"]

        # load product from database
        products = branch_repo.get_branch_products(branch_id=branch_id)

        await callback.message.edit_text(  # type: ignore
            text=SELECT_PRODUCT, reply_markup=products_kb(products=products)
        )


@sales_router.callback_query(
    SalesOrderForm.product_id, F.data.regexp(r"^product_(\d+)$").as_("product_id_re")
)
async def get_quantity(
    callback: CallbackQuery, state: FSMContext, product_id_re: Match
):
    await push_state_stack(state, SalesOrderForm.quantity)

    order = await state.get_value("order", {})

    order["product_id"] = int(product_id_re.group(1))
    await state.update_data(order=order)

    await callback.message.edit_text(  # type: ignore
        text=SOLD_PRODUCT_QUANTITY, reply_markup=back_kb()
    )


@sales_router.message(
    SalesOrderForm.quantity, F.text.regexp(r"^(\d+)$").as_("quantity_re")
)
async def get_price(message: Message, state: FSMContext, quantity_re: Match):
    await push_state_stack(state, SalesOrderForm.price)

    order = await state.get_value("order", {})

    order["quantity"] = int(quantity_re.group(1))
    await state.update_data(order=order)

    await message.answer(text=SOLD_PRODUCT_PRICE, reply_markup=back_kb())


@sales_router.message(SalesOrderForm.price, F.text.regexp(r"^(\d+)$").as_("price_re"))
async def show_summary(
    message: Message,
    state: FSMContext,
    price_re: Match,
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
):
    await push_state_stack(state, SalesOrderForm.save)

    order = await state.get_value("order", {})

    price = int(price_re.group(1))
    order["price"] = price
    order["total_amount"] = price * order["quantity"]

    summary_msg = order_details(
        order=order, branch_repo=branch_repo, product_repo=product_repo
    )
    await state.update_data(order=order, message=summary_msg)

    await message.answer(summary_msg, reply_markup=save_kb())


@sales_router.callback_query(SalesOrderForm.save, F.data == SAVE)
async def save_to_db(
    callback: CallbackQuery, bot: Bot, state: FSMContext, order_repo: IOrderRepository
):
    order = await state.get_value("order", {})
    message = await state.get_value("message", "")
    await state.clear()

    # Save to db
    _save_to_db(order=order, order_repo=order_repo)
    await send_message_to_admin(bot=bot, context=message)

    await callback.message.edit_text(text=message)  # type: ignore
    await callback.message.answer(text=SUCCESSFULLY_SAVED)  # type: ignore


def _save_to_db(order: Dict[str, Any], order_repo: IOrderRepository):
    new_order = Order(**order)

    order_repo.create_new(new_order)


def order_details(
    order: Dict[str, Any],
    branch_repo: IBranchRepository,
    product_repo: IProductRepository,
) -> str:
    msg = "<b>Sotuv</b>\n\n"
    branch = branch_repo.get_by_id(branch_id=order["branch_id"])
    product = product_repo.get_by_id(product_id=order["product_id"])
    date = datetime.strptime(order["date"], "%Y-%m-%d").strftime("%d.%m.%Y")

    msg += f"Bo'lim: <blockquote>{branch.name}</blockquote>\n"
    msg += f"Sana: <blockquote>{date}</blockquote>\n"
    msg += f"Mahsulot nomi: <blockquote>{product.name}</blockquote>\n"
    msg += f"Mahsulot soni: <blockquote>{order['quantity']}</blockquote>\n"
    msg += f"Mahsulot narxi: <blockquote>{order['price']} so'm</blockquote>\n"
    msg += f"Jami summa: <blockquote>{order['total_amount']:,} so'm</blockquote>\n"

    return msg

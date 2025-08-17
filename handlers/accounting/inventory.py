from __future__ import annotations

from typing import TYPE_CHECKING, Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from resources.string import CALCULATING, INVENTORY

from .forms import AccountingForm, InventoryForm

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from data.repositories import IOrderRepository, IProductionRecordRepository
    from utils import StateManager


inventory_router = Router(name="inventory")


# @inventory_router.callback_query(AccountingForm.accounting_menu, F.data == INVENTORY)
@inventory_router.message(Command("inventory"))
async def calculate_stock_balance(
    event: Union[Message, CallbackQuery], state: FSMContext, state_mgr: StateManager
):
    await state.update_data(state_stack=[], form_data={})

    await state_mgr.push_state_stack(state=state, next_state=InventoryForm.results)

    if isinstance(event, CallbackQuery):
        await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore
        return

    await state_mgr.dispatch_query(message=event, state=state)  # type: ignore


@inventory_router.callback_query(AccountingForm.accounting_menu, F.data == INVENTORY)
async def show_balance(
    callback: CallbackQuery,
    state: FSMContext,
    state_mgr: StateManager,
    order_repo: IOrderRepository,
    prod_record_repo: IProductionRecordRepository,
):
    await callback.message.edit_text(CALCULATING)  # type: ignore

    sold_products = order_repo.filter()
    manufactured_products = prod_record_repo.stat()

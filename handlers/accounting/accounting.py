from __future__ import annotations

from typing import TYPE_CHECKING, Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from resources.string import ACCOUNTING_MENU

from .forms import AccountingForm
from .inventory import inventory_router
from .salary import salary_router
from .transactions import transactions_router

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from utils.state_manager import StateManager

accounting_router = Router(name="accounting_main")
accounting_router.include_routers(
    *(salary_router, inventory_router, transactions_router),
)


@accounting_router.callback_query(F.data == ACCOUNTING_MENU)
@accounting_router.message(Command("accounting"))
async def accounting(
    event: Union[Message, CallbackQuery], state: FSMContext, state_mgr: StateManager
):
    await state_mgr.push_state_stack(
        state=state, next_state=AccountingForm.accounting_menu
    )
    if isinstance(event, CallbackQuery):
        if event.message:
            await state_mgr.dispatch_query(message=event.message, state=state)  # type: ignore
            return

    await state_mgr.dispatch_query(message=event, state=state)  # type: ignore

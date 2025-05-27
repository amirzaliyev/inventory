from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Sequence, Set

from aiogram_calendar import SimpleCalendar

from keyboards.common import back_kb
from resources.string import CALLBACK_DATA, READY, SAVE, TEXT
from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

    from data.models import Employee


def branches_kb(branches: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Available branches"""
    # static data only for now
    buttons = []
    for branch in branches:
        button = {}
        button[TEXT] = branch["name"]  # type: ignore
        button[CALLBACK_DATA] = f"branch_{branch["id"]}"  # type: ignore

        buttons.append(button)

    return make_inline_kb(buttons, back_btn=True, resize=True)


async def select_date_kb() -> InlineKeyboardMarkup:
    """Calendar keyboard for easy date selection"""
    calendar = await SimpleCalendar().start_calendar()

    calendar.inline_keyboard += back_kb().inline_keyboard
    return calendar


def products_kb(products: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Shows available products to the selected branch"""
    # static data only for now
    buttons = []
    for product in products:
        btn = {}
        btn[TEXT] = product["name"]
        btn[CALLBACK_DATA] = f"product_{product["id"]}"
        buttons.append(btn)

    return make_inline_kb(buttons, back_btn=True, resize=True)


def workers_on_duty_kb(
    workers: Sequence[Employee], present_employees: Set[int]
) -> InlineKeyboardMarkup:
    """Shows selected branch workers"""

    buttons = []
    for worker in workers:
        btn = {}
        worker_id = worker.id
        if worker_id in present_employees:
            btn[TEXT] = f"✅ {worker.first_name}"
        else:
            btn[TEXT] = f"❌ {worker.first_name}"

        btn[CALLBACK_DATA] = f"worker_{worker_id}"
        buttons.append(btn)

    ready_btn = {TEXT: READY, CALLBACK_DATA: READY}
    buttons.append(ready_btn)

    return make_inline_kb(buttons=buttons, size=[2], back_btn=True)


def save_kb() -> InlineKeyboardMarkup:
    buttons = [
        {
            TEXT: SAVE,
            CALLBACK_DATA: SAVE,
        }
    ]

    return make_inline_kb(buttons=buttons, back_btn=True)

from __future__ import annotations

from typing import TYPE_CHECKING

from resources.string import CALLBACK_DATA, INVENTORY, SALARY, TEXT, TRANSACTIONS
from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def accounting_menu_kb() -> InlineKeyboardMarkup:
    buttons = [
        {
            TEXT: TRANSACTIONS,
            CALLBACK_DATA: TRANSACTIONS,
        },
        {
            TEXT: SALARY,
            CALLBACK_DATA: SALARY,
        },
        {
            TEXT: INVENTORY,
            CALLBACK_DATA: INVENTORY,
        },
    ]

    return make_inline_kb(buttons=buttons, size=[3])

from __future__ import annotations

from typing import TYPE_CHECKING

from resources.string import CALLBACK_DATA, PRODUCTION, SALES, TEXT
from utils import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def current_action_kb() -> InlineKeyboardMarkup:
    """Returns the several options that is available to user"""

    buttons = []

    production = {TEXT: PRODUCTION, CALLBACK_DATA: "activity_production"}
    sales = {TEXT: SALES, CALLBACK_DATA: "activity_sales"}
    buttons.append(production)
    buttons.append(sales)

    return make_inline_kb(buttons)

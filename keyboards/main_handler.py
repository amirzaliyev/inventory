from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup

from resources.string import TEXT, CALLBACK_DATA, PRODUCTION, SALES
from utils import make_inline_kb


def current_action_kb() -> InlineKeyboardMarkup:
    """Returns the several options that is available to user"""

    buttons = []

    production = {TEXT: PRODUCTION, CALLBACK_DATA: PRODUCTION}
    sales = {TEXT: SALES, CALLBACK_DATA: SALES}
    buttons.append(production)
    buttons.append(sales)

    return make_inline_kb(buttons)

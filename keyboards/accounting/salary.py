from __future__ import annotations

from typing import TYPE_CHECKING

from resources.dicts import months
from resources.string import CALLBACK_DATA, TEXT
from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def months_kb() -> InlineKeyboardMarkup:
    buttons = []
    for sequal, month in months.items():
        btn = {}

        btn[TEXT] = month
        btn[CALLBACK_DATA] = f"month_{sequal}"

        buttons.append(btn)

    return make_inline_kb(buttons=buttons, resize=True, back_btn=True)

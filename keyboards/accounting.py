from __future__ import annotations

from typing import TYPE_CHECKING

from resources.string import (APRIL, AUGUST, CALLBACK_DATA, DECEMBER, FEBRUARY,
                              JANUARY, JULY, JUNE, MARCH, MAY, NOVEMBER,
                              OCTOBER, SEPTEMBER, TEXT)
from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def months_kb() -> InlineKeyboardMarkup:
    buttons = []
    texts = [
        JANUARY,
        FEBRUARY,
        MARCH,
        APRIL,
        MAY,
        JUNE,
        JULY,
        AUGUST,
        SEPTEMBER,
        OCTOBER,
        NOVEMBER,
        DECEMBER,
    ]

    for i, text in enumerate(texts, start=1):
        btn = {}
        btn[TEXT] = text
        btn[CALLBACK_DATA] = f"month_{i}"
        buttons.append(btn)

    return make_inline_kb(buttons=buttons, resize=True, back_btn=True)

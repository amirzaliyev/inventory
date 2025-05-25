from __future__ import annotations

from typing import TYPE_CHECKING

from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

def back_kb() -> InlineKeyboardMarkup:
    return make_inline_kb(buttons=[], back_btn=True)

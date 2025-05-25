from __future__ import annotations

from typing import Dict, List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from resources.string import BACK


def make_inline_kb(
    buttons: List[Dict],
    size: Optional[List[int]] = None,
    back_btn: bool = False,
    **kwargs,
) -> InlineKeyboardMarkup:
    """
    Creates inline keyboards using 'InlineKeyboardBuilder'
    Args:
        buttons - required, list of inline button parameters
        size - optional, keyboard size
        back_btn - optional, if true back button will be added
        **kwargs - parameters for 'InlineKeyboardMarkup'
    """
    ikb = InlineKeyboardBuilder()

    for btn in buttons:
        ikb.button(**btn)

    if size is None:
        size = [3]

    ikb.adjust(*size)

    if back_btn is True:
        ikb.row(InlineKeyboardButton(text=BACK, callback_data=BACK), width=1)

    return ikb.as_markup(**kwargs)

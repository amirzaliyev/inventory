from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from keyboards.accounting.accounting import accounting_menu_kb
from resources.string import WELCOME_TEXT
from utils.state_manager import Switch

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


accounting_switch = Switch(name="accounting")


@accounting_switch.register("accounting_menu")
async def main_menu() -> Tuple[str, Optional[InlineKeyboardMarkup]]:

    return (
        WELCOME_TEXT.format("<blockquote>Accounting page</blockquote>"),
        accounting_menu_kb(),
    )

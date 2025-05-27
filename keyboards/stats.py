from __future__ import annotations

from typing import TYPE_CHECKING

from resources.string import ALL_TIME, CALLBACK_DATA, MONTHLY, TEXT, WEEKLY
from utils.keyboard import make_inline_kb

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup


def stat_period_kb() -> InlineKeyboardMarkup:
    buttons = []

    weekly = {TEXT: WEEKLY, CALLBACK_DATA: "period_weekly"}
    monthly = {TEXT: MONTHLY, CALLBACK_DATA: "period_monthly"}
    all_time = {TEXT: ALL_TIME, CALLBACK_DATA: "period_all_time"}
    buttons.append(weekly)
    buttons.append(monthly)
    buttons.append(all_time)

    return make_inline_kb(buttons=buttons, resize=True, back_btn=True, size=[1])

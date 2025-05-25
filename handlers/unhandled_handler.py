from __future__ import annotations

import time
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.fsm.context import FSMContext

if TYPE_CHECKING:
    from aiogram.types import CallbackQuery, Message


unhandled_router = Router(name="unhandled")


@unhandled_router.message()
async def handle_unhanled(message: Message, state: FSMContext) -> None:
    msg = await message.answer("hello you creepy")
    await message.delete()
    time.sleep(1)
    await msg.delete()


@unhandled_router.callback_query()
async def handle_unhandled_cb(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    msg = await callback.message.answer("hello, you creepy. I got you")  # type: ignore
    time.sleep(1)
    await msg.delete()

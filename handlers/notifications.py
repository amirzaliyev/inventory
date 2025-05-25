# from aiogram import Router
from __future__ import annotations

from typing import TYPE_CHECKING

from config import settings

if TYPE_CHECKING:
    from aiogram import Bot


# notifications_router = Router(name="notifications")


async def send_message_to_admin(bot: Bot, context: str):
    await bot.send_message(settings.SUPER_ADMIN, context)

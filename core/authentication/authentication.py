from __future__ import annotations

from typing import TYPE_CHECKING

from data.exceptions import RecordNotFound

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

    from data.repositories import IUserRepository


async def login(user_id: int, state: FSMContext, user_repo: IUserRepository) -> bool:
    session = await state.get_value("session", {"user": None})
    user = session["user"]

    if user is None:
        try:
            user = user_repo.get_by_id(user_id=user_id)
            session["user"] = user
            await state.update_data(session=session)
            return True

        except RecordNotFound:
            return False

    return True

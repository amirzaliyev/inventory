from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from data.exceptions import RecordNotFound

if TYPE_CHECKING:
    from data.models import User


class IUserRepository(ABC):
    def __init__(self, session, model):
        self._session = session
        self._model = model

    @abstractmethod
    def create(self, new_user: User) -> User:
        """
        Creates new user from given 'User' object.

        Params
            new_user: User - 'User' object

        Returns
            User - newly created user
        """

    @abstractmethod
    def get_by_id(self, user_id: int) -> User:
        """
        Retrieves user by id.

        Params
            user_id: int - User id

        Returns
            User - if available with user_id

        Raises
            RecordNotFound - if there is no record with given id

        """


class UserRepository(IUserRepository):

    def create(self, new_user: User) -> User:
        with self._session() as session:
            session.add(new_user)
            session.commit()

            session.refresh(new_user)

        return new_user

    def get_by_id(self, user_id: int) -> User:
        with self._session() as session:
            user = session.get(self._model, user_id)

            if not user:
                raise RecordNotFound(f'There is no user with id {user_id}')

            return user

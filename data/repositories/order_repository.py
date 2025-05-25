from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type

from data.models import Order

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker


class IOrderRepository(ABC):

    def __init__(self, session: "sessionmaker[Session]", model: Type[Order]) -> None:
        self._session = session
        self._model = model

    @abstractmethod
    def create_new(self, new_order: Order) -> Order:
        """
        Creates new sales order

        Param
            new_order: Order id

        Returns
            Order object
        """


class OrderRepository(IOrderRepository):

    def __init__(self, session: "sessionmaker[Session]", model: Type[Order]) -> None:
        super().__init__(session=session, model=model)

    def create_new(self, new_order: Order) -> Order:
        with self._session() as session:
            session.add(new_order)
            session.commit()
            session.refresh(new_order)

            return new_order

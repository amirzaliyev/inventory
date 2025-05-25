from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence, Type

from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from data.models import Employee


class IEmployeeRepository(ABC):
    def __init__(self, session: "sessionmaker[Session]", model: Type[Employee]) -> None:
        self._session = session
        self._model = model

    @abstractmethod
    def all(self, branch_id: int) -> Sequence[Employee]:
        """
        Retrieves all employees available to the branch

        Params
            branch_id: Branch

        Returns
            Query[Employee] - list of employees
        """
        pass


class EmployeeRepository(IEmployeeRepository):

    def __init__(self, session: "sessionmaker[Session]", model: Type[Employee]) -> None:
        super().__init__(session=session, model=model)

    def all(self, branch_id: int) -> Sequence[Employee]:

        with self._session() as session:
            stmt = select(self._model).where(self._model.branch_id == branch_id)
            res = session.execute(stmt).scalars().all()

            return res

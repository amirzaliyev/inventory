from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List, Sequence, Type, Union

from sqlalchemy import select

from data.exceptions import RecordNotFound

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from data.models import Branch


class IBranchRepository(ABC):
    """Repository for handling database transactions against 'Branch' model"""

    def __init__(self, session, model) -> None:
        self._session = session
        self._model = model

    @abstractmethod
    def all(self, as_dict: bool = False) -> Union[Sequence[Branch], Dict[str, Any]]:
        """
        Retrieves all branches

        Params
        Returns
            Query[Branch] - iterable result of query
        """
        pass

    @abstractmethod
    def get_by_id(self, branch_id: int) -> Branch:
        """
        Retrieves one branch

        Params
            branch_id: Branch id

        Returns
            Branch object

        Raises
            RecordNotFound
        """

    @abstractmethod
    def get_branch_products(self, branch_id: int) -> List[Dict[str, Any]]:
        """
        Returns branch products

        Param
            branch_id: Branch id

        Raises
            RecordNotFound
        """


class BranchRepository(IBranchRepository):

    def __init__(self, session: "sessionmaker[Session]", model: Type[Branch]) -> None:
        super().__init__(session=session, model=model)

    def all(self, as_dict: bool = False) -> Union[Sequence[Branch], Dict[str, Any]]:
        with self._session() as session:
            stmt = select(self._model.id, self._model.name)
            results = session.execute(stmt)

            if as_dict is True:
                return results.mappings().all()

            return results.scalars().all()

    def get_by_id(self, branch_id: int) -> Branch:
        with self._session() as session:
            result = session.get(self._model, branch_id)

            if not result:
                raise RecordNotFound(f"There is no branch with id {branch_id}")

            return result

    def get_branch_products(self, branch_id: int) -> List[Dict[str, Any]]:
        with self._session() as session:
            result = session.get(self._model, branch_id)

            if not result:
                raise RecordNotFound(f"There is no branch with id {branch_id}")

            products = []
            for res in result.branch_products:

                products.append(res.product.__dict__)

        return products

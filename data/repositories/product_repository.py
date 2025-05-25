from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence, Type

from sqlalchemy import select

from data.exceptions import RecordNotFound

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from data.models import Product


class IProductRepository(ABC):
    """Repository interface for handling database transactions against 'Product' model"""

    def __init__(self, session: "sessionmaker[Session]", model: Type[Product]) -> None:
        self._session = session
        self._model = model

    @abstractmethod
    def all(self) -> Sequence[Product]:
        """
        Retrieves all products available to the branch

        Params
            branch_id - Branch id

        Returns
            Query[Product] - query result
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product:
        """
        Returns the with product with specified id

        Param
            product_id: Product id

        Raises
            RecordNotFound - if there is no record with specified id
        """
        pass


class ProductRepository(IProductRepository):

    def __init__(self, session: "sessionmaker[Session]", model: Type[Product]) -> None:
        super().__init__(session=session, model=model)

    def all(self) -> Sequence[Product]:
        with self._session() as session:
            stmt = select(self._model)
            results = session.execute(stmt).scalars().all()

            return results

    def get_by_id(self, product_id: int) -> Product:
        with self._session() as session:
            result = session.get(self._model, product_id)

            if not result:
                raise RecordNotFound(f"There is no record with id {product_id}")


            return result

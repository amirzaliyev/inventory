from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from sqlalchemy import func, select

from data.models import Product

if TYPE_CHECKING:
    from datetime import date

    from sqlalchemy.orm import Session, sessionmaker

    from data.models import Attendance, ProductionRecord


class IProductionRecordRepository(ABC):

    def __init__(
        self, session: "sessionmaker[Session]", model: Type[ProductionRecord]
    ) -> None:
        self._session = session
        self._model = model

    @abstractmethod
    def create_record(self, new_record: ProductionRecord) -> ProductionRecord:
        """
        Creates new production record.

        Params:
            new_record: new production record

        Returns:
            Newly created record
        """
        pass

    @abstractmethod
    def create_attendance_record(self, new_records: List[Attendance]) -> None:
        """
        Creates new attendance record.

        Params
            new_record: Attendance object

        Returns
        """

    @abstractmethod
    def filter(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filters the records.

        Params
            date_from: Start of the period, if none default is '2000-01-01'
            date_to: End of the period, if none default is 'datetime.now().date()'

        Returns
            List[Dict[str, Any]]
        """


class ProductionRecordRepository(IProductionRecordRepository):
    def __init__(
        self, session: "sessionmaker[Session]", model: Type[ProductionRecord]
    ) -> None:
        super().__init__(session=session, model=model)

    def create_record(self, new_record: ProductionRecord) -> ProductionRecord:
        with self._session() as session:
            session.add(new_record)
            session.commit()
            session.refresh(new_record)

        return new_record

    def create_attendance_record(self, new_records: List[Attendance]) -> None:
        with self._session() as session:
            session.add_all(new_records)

            session.commit()

    def filter(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:

        if date_to is None:
            date_to = datetime.now().date()

        if date_from is None:
            date_from = datetime.strptime("2000-01-01", "%Y-%m-%d")

        with self._session() as session:
            select_stmt = (
                select(
                    Product.name,
                    func.sum(self._model.quantity).label("total_count"),
                    func.sum(self._model.used_cement_amount).label(
                        "used_cement_amount"
                    ),
                )
                .where(
                    self._model.date >= date_from,
                    self._model.date <= date_to,
                )
                .join(Product)
                .group_by(self._model.product_id, Product.name)
            )
            res = session.execute(select_stmt).mappings().all()

            return res  # type: ignore

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from data.models import Attendance, Product

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from data.models import ProductionRecord


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
    def stat(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Calculates total production work for given period.

        Params
            date_from: Start of the period, if none default is '2000-01-01'
            date_to: End of the period, if none default is 'datetime.now().date()'

        Returns
            List[Dict[str, Any]]
        """

    @abstractmethod
    def filter_by_period(
        self, date_from: date, date_to: date
    ) -> List[ProductionRecord]:
        """
        Filters the 'ProductionRecord' by given period

        Params:
            date_from: date obj - start of the period (included)
            date_to: date obj - end of the period (included)
            branch_id: Optional[int] - 'Branch' id.
                if None all branch records will be retrieved

        Returns:
            List[ProductionRecord] - result of select query
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

    def stat(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> List[Dict[str, Any]]:

        if date_to is None:
            date_to = date.today()

        if date_from is None:
            date_from = date(2000, 1, 1)

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

    def filter_by_period(
        self, date_from: date, date_to: date, branch_id: Optional[int] = None
    ) -> List[ProductionRecord]:
        with self._session() as session:
            stmt = select(self._model)
            if branch_id:
                stmt = stmt.where(
                    self._model.date >= date_from,
                    self._model.date <= date_to,
                    self._model.branch_id == branch_id,
                )

            else:
                stmt = stmt.where(
                    self._model.date >= date_from, self._model.date <= date_to
                )

            stmt = stmt.options(
                selectinload(self._model.employees).selectinload(Attendance.employee),
                selectinload(self._model.product),
            ).order_by(
                self._model.date
            )  # todo fix tight coupling problem

            results = session.execute(stmt).scalars().all()

        return results  # type: ignore todo check what's wrong with this return type

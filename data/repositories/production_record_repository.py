from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:
    from sqlalchemy.orm import Session, sessionmaker

    from data.models import Attendance, ProductionRecord


class IProductionRecordRepository(ABC):

    def __init__(
        self, session: "sessionmaker[Session]", record_type: Type[ProductionRecord]
    ) -> None:
        self._session = session
        self._record_type = record_type

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


class ProductionRecordRepository(IProductionRecordRepository):
    def __init__(
        self, session: "sessionmaker[Session]", record_type: Type[ProductionRecord]
    ) -> None:
        super().__init__(session=session, record_type=record_type)

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

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from data.models import Attendance


class IAttendanceRepository(ABC):
    def __init__(self, session, model):
        self._session = session
        self._model = model

    @abstractmethod
    def filter_by(self, **kwargs) -> List[Attendance]:
        """
        Filters all attendance records by given parameters

        Params
            **kwargs: 'Attendance' valid attributes

        Returns
            List['Attendance'] - result of select query
        """
        pass


class AttendanceRepository(IAttendanceRepository):

    def filter_by(self, **kwargs) -> List[Attendance]:
        with self._session() as session:
            stmt = (
                select(self._model)
                .filter_by(**kwargs)
                .options(
                    selectinload(self._model.employee),
                    selectinload(self._model.production_record),
                )
            )

            results = session.execute(stmt).scalars().all()

        return results

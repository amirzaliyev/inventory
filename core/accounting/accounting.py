from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from data.repositories import (
    IBranchRepository,
    IOrderRepository,
    IProductionRecordRepository,
)

if TYPE_CHECKING:
    from datetime import date


class Accounting:

    def __init__(
        self,
        branch_repo: IBranchRepository,
        prod_record_repo: IProductionRecordRepository,
        order_repo: IOrderRepository,
    ) -> None:
        self._prod_repo = prod_record_repo
        self._order_repo = order_repo
        self._branch_repo = branch_repo

    def statistic(self):
        pass

    # def calculate_salary_all(
    #     self, period: Dict[str, date], branch_id: Optional[int] = None
    # ):
    #     """
    #     Calculates salary for given branch and period.
    #
    #     Params:
    #         period: - Dict[str, date]. Example {'date_from': date obj, 'date_to': date obj}
    #         branch_id: - Optional[int], can be None
    #             if so it will calculate salary for all branch employees for given period
    #
    #     Returns:
    #
    #     """
    #     result = {}
    #
    #     if branch_id is not None:
    #
    #         branch = self._branch_repo.get_by_id(branch_id=branch_id)
    #         return
    #
    #     branch = self._branch_repo.all()
    #
    #     return

    def calculate_salary(
        self, period: Dict[str, date], branch_id: int
    ) -> Dict[str, Any]:
        """
        Calculates salary for given branch and period.

        Params:
            period: - Dict[str, date]. Example {'date_from': date obj, 'date_to': date obj}
                period should have 'date_from' and 'date_to' keywords!
            branch_id: - int

        Returns:
            Dict[str, Any]
        """
        if "date_from" not in period or "date_to" not in period:
            raise KeyError("'date_from' or 'date_to' should be in period dictionary")

        records = self._prod_repo.filter_by_period(branch_id=branch_id, **period)  # type: ignore

        all_records = {"details": [], "summary": {}}

        for record in records:
            if record.employees:
                rate = float(record.product.rates[0].payment_rate)  # parse to float

                total_employees = len(record.employees)
                employee_share = rate * record.quantity / total_employees
                data = {
                    "date": record.date,
                    "product_name": record.product.name,
                    "quantity": record.quantity,
                    "rate": rate,
                    "emp_share": employee_share,
                }

                summary = all_records["summary"]
                for emp in record.employees:
                    emp_first_name = emp.employee.first_name

                    data[emp_first_name] = "+"
                    summary[emp_first_name] = (
                        summary.get(emp_first_name, 0) + employee_share
                    )
                    summary["Total"] = summary.get("Total", 0) + employee_share

                all_records["details"].append(data)

        return all_records

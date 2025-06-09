from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from aiogram.fsm.state import State, StatesGroup

from keyboards import (back_kb, branches_kb, current_action_kb, products_kb,
                       select_date_kb, workers_on_duty_kb)
from resources.string import (ATTENDANCE, SELECT_BRANCH, SELECT_DATE,
                              SELECT_PRODUCT, SOLD_PRODUCT_PRICE,
                              SOLD_PRODUCT_QUANTITY, USED_CEMENT_AMOUNT,
                              WELCOME_TEXT)

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

    from data.repositories import IBranchRepository, IEmployeeRepository


class ProductionRecordForm(StatesGroup):
    branch_id = State()
    date = State()
    product_id = State()
    quantity = State()
    used_cement_amount = State()
    workers = State()
    save = State()


class SalesOrderForm(StatesGroup):
    branch_id = State()
    date = State()
    product_id = State()
    quantity = State()
    price = State()
    save = State()


class StatisticsForm(StatesGroup):
    activity = State()
    branch_id = State()
    period = State()


async def dispatch_state(
    state: FSMContext,
    branch_repo: Optional[IBranchRepository] = None,
    emp_repo: Optional[IEmployeeRepository] = None,
):
    current = await state.get_state()
    if current:
        match current.split(":")[-1]:
            case "branch_id":
                branches: List[Dict[str, Any]] = branch_repo.all(as_dict=True)  # type: ignore

                return SELECT_BRANCH, branches_kb(branches=branches)

            case "date":
                return SELECT_DATE, await select_date_kb()

            case "product_id":
                order = await state.get_value("new_record", {})
                branch_id = order["branch_id"]

                if branch_repo is not None:
                    products = branch_repo.get_branch_products(branch_id=branch_id)

                    return SELECT_PRODUCT, products_kb(products=products)

            case "quantity":
                product_name = await state.get_value("product_name", "")

                return SOLD_PRODUCT_QUANTITY.format(product_name), back_kb()

            case "price":
                product_name = await state.get_value("product_name", "")

                return SOLD_PRODUCT_PRICE.format(product_name), back_kb()
            case "used_cement_amount":
                product_name = await state.get_value("product_name", "")

                return USED_CEMENT_AMOUNT.format(product_name), back_kb()

            case "workers":
                new_record = await state.get_value("new_record", {})
                present_employees = await state.get_value("present_employees", {})
                branch_id = new_record["branch_id"]

                if emp_repo:
                    workers = emp_repo.all(branch_id=branch_id)

                    return ATTENDANCE, workers_on_duty_kb(
                        workers=workers, present_employees=present_employees
                    )

            case "activity":
                return WELCOME_TEXT, current_action_kb()

    raise ValueError("Come on")

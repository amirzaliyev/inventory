from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from core.authentication import login
from data.exceptions import RecordNotFound
from keyboards import (
    back_kb,
    branches_kb,
    current_action_kb,
    months_kb,
    products_kb,
    select_date_kb,
    stat_period_kb,
    workers_on_duty_kb,
)
from resources.string import (
    ATTENDANCE,
    NO_PERMISSION,
    PRODUCT_QUANTITY,
    SELECT_BRANCH,
    SELECT_DATE,
    SELECT_MONTH,
    SELECT_PERIOD,
    SELECT_PRODUCT,
    SOLD_PRODUCT_PRICE,
    USED_CEMENT_AMOUNT,
    WELCOME_TEXT,
)
from utils.state_manager import Switch

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import InlineKeyboardMarkup, Message

    from data.repositories import (
        IBranchRepository,
        IEmployeeRepository,
        IProductRepository,
        IUserRepository,
    )

switch = Switch()


@switch.register("activity")
async def cmd_start(
    message: Message, state: FSMContext, user_repo: IUserRepository
) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    has_access = await login(message.from_user.id, state=state, user_repo=user_repo)  # type: ignore
    if has_access:
        return WELCOME_TEXT, current_action_kb()

    return NO_PERMISSION, None


@switch.register("branch_id")
async def show_branches(
    branch_repo: IBranchRepository,
) -> Tuple[str, InlineKeyboardMarkup]:
    branches: List[Dict[str, Any]] = branch_repo.all(as_dict=True)  # type: ignore

    return (
        SELECT_BRANCH,
        branches_kb(branches=branches),
    )


@switch.register("date")
async def select_date() -> Tuple[str, InlineKeyboardMarkup]:
    """Processes the selected branch and shows its product line"""

    return SELECT_DATE, await select_date_kb()


@switch.register("product_id")
async def show_products(
    state: FSMContext,
    branch_repo: IBranchRepository,
) -> Tuple[str, InlineKeyboardMarkup]:
    form_data = await state.get_value("form_data", {})

    branch_id = form_data["branch_id"]

    try:
        branch_name = branch_repo.get_by_id(branch_id=branch_id).name

    except RecordNotFound:
        branch_name = ""

    # load product from database
    products = branch_repo.get_branch_products(branch_id=branch_id)

    return SELECT_PRODUCT.format(branch_name), products_kb(products=products)


@switch.register("quantity")
async def get_quantity(
    state: FSMContext,
    product_repo: IProductRepository,
) -> Tuple[str, InlineKeyboardMarkup]:
    form_data = await state.get_value("form_data", {})
    product_id = form_data["product_id"]
    product_name = product_repo.get_by_id(product_id=product_id).name

    await state.update_data(product_name=product_name)

    return PRODUCT_QUANTITY.format(product_name), back_kb()


@switch.register("price")
async def get_price(state: FSMContext) -> Tuple[str, InlineKeyboardMarkup]:
    product_name = await state.get_value("product_name", "")
    return SOLD_PRODUCT_PRICE.format(product_name), back_kb()


@switch.register("used_cement_amount")
async def get_used_cement_amount(state: FSMContext) -> Tuple[str, InlineKeyboardMarkup]:
    product_name = await state.get_value("product_name", "")
    return USED_CEMENT_AMOUNT.format(product_name), back_kb()


@switch.register("workers")
async def get_workers(
    state: FSMContext,
    emp_repo: IEmployeeRepository,
) -> Tuple[str, InlineKeyboardMarkup]:
    data = await state.get_data()
    form_data = data.get("form_data", {})
    extras = data.get("extras", {})

    branch_id = form_data["branch_id"]

    workers = extras.get("workers", [])
    present_employees = extras.get("present_employees", set())
    if not workers:
        workers = emp_repo.all(branch_id=branch_id)
        present_employees = set(worker.id for worker in workers)

    extras.update(workers=workers, present_employees=present_employees)

    await state.update_data(extras=extras)

    return ATTENDANCE, workers_on_duty_kb(
        workers=workers, present_employees=present_employees
    )


@switch.register("period")
async def get_period_month() -> Tuple[str, InlineKeyboardMarkup]:
    return SELECT_MONTH, months_kb()


@switch.register("stat_period")
async def get_stat_period() -> Tuple[str, InlineKeyboardMarkup]:
    return SELECT_PERIOD, stat_period_kb()

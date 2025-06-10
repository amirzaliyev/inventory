from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from core.authentication import login
from keyboards import (back_kb, branches_kb, current_action_kb, products_kb,
                       select_date_kb)
from resources.string import (NO_PERMISSION, SELECT_BRANCH, SELECT_DATE,
                              SELECT_PRODUCT, SOLD_PRODUCT_QUANTITY,
                              WELCOME_TEXT)
from utils.state_manager import Switch

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message

    from data.repositories import (IBranchRepository, IProductRepository,
                                   IUserRepository)

switch = Switch()


@switch.register("start")
async def cmd_start(
    message: Message, state: FSMContext, user_repo: IUserRepository
) -> None:

    has_access = await login(message.from_user.id, state=state, user_repo=user_repo)  # type: ignore
    if has_access:
        await message.answer(WELCOME_TEXT, reply_markup=current_action_kb())

    else:
        await message.answer(NO_PERMISSION)


@switch.register("branch_id")
async def show_branches(
    message: Message, branch_repo: IBranchRepository, edit_msg: bool = True
) -> None:
    branches: List[Dict[str, Any]] = branch_repo.all(as_dict=True)  # type: ignore
    if edit_msg is True:
        await message.edit_text(
            text=SELECT_BRANCH, reply_markup=branches_kb(branches=branches)
        )
    else:
        await message.answer(
            text=SELECT_BRANCH, reply_markup=branches_kb(branches=branches)
        )


@switch.register("date")
async def select_date(message: Message, edit_msg: bool = True):
    """Processes the selected branch and shows its product line"""
    if edit_msg is True:
        await message.edit_text(text=SELECT_DATE, reply_markup=await select_date_kb())

    else:
        await message.answer(text=SELECT_DATE, reply_markup=await select_date_kb())


@switch.register("product_id")
async def show_products(
    message: Message,
    state: FSMContext,
    branch_repo: IBranchRepository,
    edit_msg: bool = True,
):
    new_record = await state.get_value("new_record", {})

    branch_id = new_record["branch_id"]

    # load product from database
    products = branch_repo.get_branch_products(branch_id=branch_id)

    if edit_msg is True:
        await message.edit_text(
            text=SELECT_PRODUCT, reply_markup=products_kb(products=products)
        )
    else:
        await message.answer(
            text=SELECT_PRODUCT, reply_markup=products_kb(products=products)
        )


@switch.register("quantity")
async def get_quantity(
    message: Message,
    state: FSMContext,
    product_repo: IProductRepository,
    edit_msg: bool = True,
):
    new_record = await state.get_value("new_record", {})
    product_id = new_record["product_id"]
    product_name = product_repo.get_by_id(product_id=product_id).name

    await state.update_data(product_name=product_name)

    if edit_msg is True:
        await message.edit_text(
            text=SOLD_PRODUCT_QUANTITY.format(product_name), reply_markup=back_kb()
        )

    else:
        await message.answer(
            text=SOLD_PRODUCT_QUANTITY.format(product_name), reply_markup=back_kb()
        )

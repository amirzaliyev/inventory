from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from keyboards import back_kb, products_kb, select_date_kb
from keyboards.production import branches_kb
from resources.string import (SELECT_BRANCH, SELECT_DATE, SELECT_PRODUCT,
                              SOLD_PRODUCT_QUANTITY)

if TYPE_CHECKING:
    from re import Match

    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

    from data.repositories import IBranchRepository, IProductRepository


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


async def select_date(message: Message, edit_msg: bool = True):
    """Processes the selected branch and shows its product line"""
    if edit_msg is True:
        await message.edit_text(text=SELECT_DATE, reply_markup=await select_date_kb())

    else:
        await message.answer(text=SELECT_DATE, reply_markup=await select_date_kb())


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


async def get_quantity(
    callback: CallbackQuery,
    state: FSMContext,
    product_id_re: Match,
    product_repo: IProductRepository,
):
    product_id = int(product_id_re.group(1))
    product_name = product_repo.get_by_id(product_id=product_id).name

    await callback.message.edit_text(  # type: ignore
        text=SOLD_PRODUCT_QUANTITY.format(product_name), reply_markup=back_kb()
    )

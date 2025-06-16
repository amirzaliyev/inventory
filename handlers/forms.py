from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


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
    stat_period = State()

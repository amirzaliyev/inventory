from aiogram.fsm.state import State, StatesGroup


class AccountingForm(StatesGroup):
    accounting_menu = State()
    salary = State()
    transactions = State()
    inventory = State()


class SalaryForm(StatesGroup):
    branch_id = State()
    period = State()


class InventoryForm(StatesGroup):
    results = State()

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings
from core.accounting import Accounting
from data.db import get_engine, get_sessionmaker
from data.models import (Branch, Employee, Order, Product, ProductionRecord,
                         User)
from data.repositories import (BranchRepository, EmployeeRepository,
                               OrderRepository, ProductionRecordRepository,
                               ProductRepository)
from data.repositories.user_repository import UserRepository
from handlers import (accounting_router, main_router, production_router,
                      sales_router, stat_router, unhandled_router)
from query_handlers import switch, accounting_switch
from utils import StateManager


async def main() -> None:
    bot = Bot(
        settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # register routers
    dp.include_routers(
        *[
            stat_router,
            main_router,
            production_router,
            sales_router,
            accounting_router,
        ]
    )  # todo change the logic routing to stats
    dp.include_router(unhandled_router)

    # Initialize dependencies
    engine = get_engine(settings.database_url_psycopg2)
    sessionmaker_factory = get_sessionmaker(engine)
    prod_record_repo = ProductionRecordRepository(
        session=sessionmaker_factory, model=ProductionRecord
    )
    emp_repo = EmployeeRepository(session=sessionmaker_factory, model=Employee)
    branch_repo = BranchRepository(session=sessionmaker_factory, model=Branch)
    product_repo = ProductRepository(session=sessionmaker_factory, model=Product)
    order_repo = OrderRepository(session=sessionmaker_factory, model=Order)
    user_repo = UserRepository(session=sessionmaker_factory, model=User)

    state_mgr = StateManager(
        prod_record_repo=prod_record_repo,
        emp_repo=emp_repo,
        branch_repo=branch_repo,
        product_repo=product_repo,
        order_repo=order_repo,
        user_repo=user_repo,
    )
    state_mgr.include_switch(switch=switch)
    state_mgr.include_switch(switch=accounting_switch)

    accounting = Accounting(
        branch_repo=branch_repo,
        order_repo=order_repo,
        prod_record_repo=prod_record_repo,
    )

    await dp.start_polling(
        bot,
        prod_record_repo=prod_record_repo,
        branch_repo=branch_repo,
        product_repo=product_repo,
        order_repo=order_repo,
        user_repo=user_repo,
        accounting=accounting,
        state_mgr=state_mgr,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

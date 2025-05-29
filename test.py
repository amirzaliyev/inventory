# import datetime
#
# import pandas
#
# from config import settings
# from core.accounting.accounting import Accounting
# from data.db import get_sessionmaker, get_engine
# from data.models import ProductionRecord, Branch, Order
# from data.repositories import ProductionRecordRepository, BranchRepository, OrderRepository
# from utils.visualize import make_df, to_pdf
#
# title = 'Oylik 1-seh'
# period = {'date_from': datetime.date(2025, 5, 1), 'date_to': datetime.date.today()}
#
#
# def pdf(df):
#     to_pdf(title=title, df=df, period=period, figsize=(16, 8))
#
#
# engine = get_engine(settings.database_url_psycopg2)
# cs = get_sessionmaker(engine)
# branch_repo = BranchRepository(session=cs, model=Branch)
# prod_record_repo = ProductionRecordRepository(session=cs, model=ProductionRecord)
# order_repo = OrderRepository(session=cs, model=Order)
# accounting = Accounting(branch_repo=branch_repo, prod_record_repo=prod_record_repo, order_repo=order_repo)
# result = accounting.calculate_salary(branch_id=1, period=period)
# f = result['details']
# random = result['summary']
#
# random_not_scalar = []
# for key, value in random.items():
#     random_not_scalar.append({'Name': key, 'Salary': int(round(value, -3))})
# df = make_df(f)
# dfe = make_df(random_not_scalar, human_readable=False)
# total_row = make_df([{'Name': 'Total', 'Salary': dfe['Salary'].sum()}])
# dfe = pandas.concat([dfe, total_row], ignore_index=True)
# to_pdf(df=dfe, title='summary', period=period)
# pdf(df)
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message

from config import settings


async def main():
    bot = Bot(settings.BOT_TOKEN)

    dp = Dispatcher()

    @dp.message()
    async def cmd_start(message: Message):
        await message.answer(text=str(message.from_user.id))

    await dp.start_polling(bot)

asyncio.run(main())
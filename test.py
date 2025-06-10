from __future__ import annotations

import datetime
from typing import Any

import pandas
from sqlalchemy import select

from config import settings
from core.accounting.accounting import Accounting
from data.db import get_engine, get_sessionmaker
from data.models import Branch, Order, Product, ProductionRecord, ProductRate
from data.repositories import (BranchRepository, OrderRepository,
                               ProductionRecordRepository)
from utils.query_dispatcher import QueryDispatcher
from utils.visualize import make_df, make_human_readable, to_pdf

TITLE = "Oylik {}-seh"
period = {"date_from": datetime.date(2025, 5, 1), "date_to": datetime.date.today()}


def pdf(df):
    to_pdf(title=TITLE, df=df, period=period, figsize=(16, 8))


engine = get_engine(settings.database_url_psycopg2)
cs = get_sessionmaker(engine)
branch_repo = BranchRepository(session=cs, model=Branch)
prod_record_repo = ProductionRecordRepository(session=cs, model=ProductionRecord)
order_repo = OrderRepository(session=cs, model=Order)
accounting = Accounting(
    branch_repo=branch_repo, prod_record_repo=prod_record_repo, order_repo=order_repo
)

result = order_repo.filter(**period)

df = make_df(result, sort_by="total_count")
h_df = make_human_readable(df)

print(h_df)



# query_dispatcher = QueryDispatcher(
#     branch_repo=branch_repo,
#     prod_record_repo=prod_record_repo,
#     order_repo=order_repo,
#     accounting=accounting,
# )
#
# print()
# print(query_dispatcher.__getattribute__("branch_repo"))
#
#
# session = cs()
# stmt = select(Product)
# products = session.execute(stmt).scalars().all()
# pr = {}
# for p in products:
#     pr[p.name] = 0
#
# print(pr)
# pr = {
#     "Shlakoblok 20x40": 700,
#     "Rangli shlakoblok 20x40": 700,
#     "Tumba": 1200,
#     "Rangli tumba": 1200,
#     "Shlakoblok 16x32": 500,
#     "Latok": 50000,
#     "Kalods 90": 50000,
#     "Kalods 50": 25000,
#     "Kalods qopqoq": 25000,
#     "Tumba shapka": 2000,
#     "Rangli tumba shapka": 2000,
#     "Shapka 40 cm": 2000,
#     "Shapka 60 cm": 2000,
#     "Rangli shapka 40 cm": 2000,
#     "Rangli shapka 60 cm": 2000,
# }
#
# for p in products:
#     rate = pr[p.name]
#     p.rates.append(
#         ProductRate(
#             payment_rate=rate,
#             effective_date="2025-01-01",
#             end_date="2025-12-31",
#             product_id=p.id,
#         )
#     )
#
# session.commit()
#
#
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

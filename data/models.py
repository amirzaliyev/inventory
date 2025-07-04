from datetime import datetime
from typing import List

from sqlalchemy import (DATE, TIMESTAMP, ForeignKey, Numeric, String,
                        UniqueConstraint, text)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP, default=datetime.now, server_default=text("current_timestamp")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    username: Mapped[str] = mapped_column(String(30), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(25), unique=True)

    branches: Mapped["Branch"] = relationship()


class Branch(Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=True)

    branch_products: Mapped[List["BranchProduct"]] = relationship()


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    rates: Mapped[List["ProductRate"]] = relationship(
        order_by="desc(ProductRate.effective_date)"
    )


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(
        DATE, default=datetime.now(), server_default=text("current_date")
    )
    quantity: Mapped[int]
    used_cement_amount: Mapped[float]

    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    employees = relationship("Attendance", back_populates="production_record")
    product: Mapped["Product"] = relationship()


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]

    branch_id: Mapped[str] = mapped_column(ForeignKey("branches.id"))

    attendances = relationship("Attendance", back_populates="employee")


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    production_record_id: Mapped[int] = mapped_column(
        ForeignKey("production_records.id")
    )

    employee = relationship("Employee", back_populates="attendances")
    production_record = relationship("ProductionRecord", back_populates="employees")


class BranchProduct(Base):
    __tablename__ = "branch_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))

    product: Mapped["Product"] = relationship()
    __table_args__ = (
        UniqueConstraint("product_id", "branch_id", name="uq_branch_product"),
    )


class Order(Base):
    __tablename__ = "sales_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))
    date: Mapped[str] = mapped_column(
        DATE, default=datetime.now(), server_default=text("current_date")
    )
    quantity: Mapped[int]
    price: Mapped[int]
    total_amount: Mapped[int] = mapped_column(BIGINT)


class ProductRate(Base):
    __tablename__ = "product_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    payment_rate: Mapped[float] = mapped_column(Numeric(10, 2))
    effective_date: Mapped[str] = mapped_column(DATE)
    end_date: Mapped[str] = mapped_column(DATE)

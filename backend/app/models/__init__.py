import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    credit_limit: Mapped[float] = mapped_column(Float, default=50000.0)
    credit_used: Mapped[float] = mapped_column(Float, default=0.0)
    store_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    preferred_products: Mapped[list | None] = mapped_column(JSONB, default=list)
    aliases: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    call_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    call_logs: Mapped[list["CallLog"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_hi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_ta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="general")
    unit: Mapped[str] = mapped_column(String(20), default="kg")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[float] = mapped_column(Float, default=0.0)
    min_qty: Mapped[float] = mapped_column(Float, default=1.0)
    aliases: Mapped[list | None] = mapped_column(JSONB, default=list)
    synonyms: Mapped[list | None] = mapped_column(JSONB, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False, index=True)
    call_log_id: Mapped[str | None] = mapped_column(ForeignKey("call_logs.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="confirmed", index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    nlu_tier_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    call_log: Mapped["CallLog | None"] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)
    match_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    nlu_tier: Mapped[int] = mapped_column(Integer, default=1)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


class CallLog(Base):
    __tablename__ = "call_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(10), default="inbound")
    status: Mapped[str] = mapped_column(String(30), default="started", index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    partial_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    nlu_result: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    validation_errors: Mapped[list | None] = mapped_column(JSONB, default=list)
    clarification_count: Mapped[int] = mapped_column(Integer, default=0)
    recording_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["Customer | None"] = relationship(back_populates="call_logs")
    order: Mapped["Order | None"] = relationship(back_populates="call_log", uselist=False)


class ProductAlias(Base):
    __tablename__ = "product_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    source: Mapped[str] = mapped_column(String(50), default="manual")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

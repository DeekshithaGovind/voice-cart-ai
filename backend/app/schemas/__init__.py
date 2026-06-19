from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: str
    product_name: str
    quantity: float
    unit_price: float
    line_total: float
    match_confidence: float = 1.0
    nlu_tier: int = 1


class OrderCreate(BaseModel):
    customer_id: str
    call_log_id: str | None = None
    language: str = "en"
    items: list[OrderItemCreate]
    transcript: str | None = None
    nlu_tier_used: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrderItemOut(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: float
    unit_price: float
    line_total: float
    match_confidence: float
    nlu_tier: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: str
    customer_id: str
    call_log_id: str | None
    status: str
    language: str
    total_amount: float
    transcript: str | None
    nlu_tier_used: int | None
    created_at: datetime
    items: list[OrderItemOut] = []
    customer_name: str | None = None
    customer_phone: str | None = None

    model_config = {"from_attributes": True}


class CustomerOut(BaseModel):
    id: str
    name: str
    phone: str
    language: str
    credit_limit: float
    credit_used: float
    call_count: int
    preferred_products: list | None = []
    aliases: dict | None = {}
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: str
    sku: str
    name: str
    name_hi: str | None
    name_ta: str | None
    category: str
    unit: str
    price: float
    stock: float
    min_qty: float
    aliases: list | None = []
    synonyms: list | None = []
    active: bool

    model_config = {"from_attributes": True}


class CallLogOut(BaseModel):
    id: str
    customer_id: str | None
    phone: str
    direction: str
    status: str
    language: str
    duration_sec: int
    transcript: str | None
    partial_transcript: str | None
    nlu_result: dict | None = {}
    validation_errors: list | None = []
    clarification_count: int
    started_at: datetime
    ended_at: datetime | None = None
    customer_name: str | None = None

    model_config = {"from_attributes": True}


class ParsedLineItem(BaseModel):
    raw_text: str
    product_id: str | None = None
    product_name: str | None = None
    quantity: float = 1.0
    unit: str | None = None
    confidence: float = 0.0
    nlu_tier: int = 1
    matched_alias: str | None = None


class NLUResult(BaseModel):
    items: list[ParsedLineItem]
    tier_used: int
    language: str = "en"
    raw_transcript: str
    unmatched: list[str] = []


class ValidationIssue(BaseModel):
    code: str
    message: str
    product_id: str | None = None
    field: str | None = None


class ValidationResult(BaseModel):
    valid: bool
    issues: list[ValidationIssue] = []
    total_amount: float = 0.0


class CallSessionStart(BaseModel):
    phone: str
    language: str = "en"


class TranscriptChunk(BaseModel):
    session_id: str
    text: str
    is_final: bool = False
    language: str = "en"


class AnalyticsSummary(BaseModel):
    total_orders: int
    total_revenue: float
    total_calls: int
    avg_order_value: float
    tier1_rate: float
    tier2_rate: float
    tier3_rate: float
    orders_today: int
    calls_today: int
    active_calls: int


class MonitoringStatus(BaseModel):
    api: str
    database: str
    redis: str
    backend: str
    websocket_connections: int
    active_sessions: int
    active_calls: int
    total_orders: int
    total_customers: int
    last_order_at: datetime | None
    uptime_hint: str


class AnalyticsCharts(BaseModel):
    top_products: list[dict]
    revenue_trend: list[dict]
    orders_by_day: list[dict]
    nlu_tier_usage: list[dict]


class ActiveSessionOut(BaseModel):
    session_id: str
    customer_name: str | None
    phone: str
    state: str
    current_stage: str
    stages: list[dict]
    transcript: str
    validation_details: dict | None = None

"""backend/models/schemas.py — Pydantic response models (F-29)."""
from pydantic import BaseModel


class RevenueRecord(BaseModel):
    order_year_month: str
    total_revenue: float


class CustomerRecord(BaseModel):
    customer_id: str
    name: str
    region: str
    total_spend: float
    churned: bool


class CategoryRecord(BaseModel):
    category: str
    total_revenue: float
    avg_order_value: float
    num_orders: int


class RegionRecord(BaseModel):
    region: str
    num_customers: int
    num_orders: int
    total_revenue: float
    avg_revenue_per_customer: float

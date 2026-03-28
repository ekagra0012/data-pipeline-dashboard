"""backend/routers/data.py — Data API routes (F-28)."""
from typing import List

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.config import DATA_DIR
from backend.models.schemas import (
    CategoryRecord,
    CustomerRecord,
    RegionRecord,
    RevenueRecord,
)

router = APIRouter()


def _read_csv(filename: str) -> pd.DataFrame:
    """Load a processed CSV, raising appropriate HTTP errors."""
    path = DATA_DIR / filename
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{filename} is empty")
        return df
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Data file not found. Run analyze.py first.",
        )
    except pd.errors.EmptyDataError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/revenue", response_model=List[RevenueRecord])
def get_revenue():
    """Monthly revenue trend data."""
    df = _read_csv("monthly_revenue.csv")
    df["total_revenue"] = df["total_revenue"].round(2)
    return df.to_dict(orient="records")


@router.get("/api/top-customers", response_model=List[CustomerRecord])
def get_top_customers():
    """Top 10 customers by total spend with churn status."""
    df = _read_csv("top_customers.csv")
    df["customer_id"] = df["customer_id"].astype(str)
    df["churned"] = df["churned"].astype(bool)
    df["total_spend"] = df["total_spend"].round(2)
    return df.to_dict(orient="records")


@router.get("/api/categories", response_model=List[CategoryRecord])
def get_categories():
    """Category performance metrics."""
    df = _read_csv("category_performance.csv")
    df["num_orders"] = df["num_orders"].astype(int)
    df["total_revenue"] = df["total_revenue"].round(2)
    df["avg_order_value"] = df["avg_order_value"].round(2)
    return df.to_dict(orient="records")


@router.get("/api/regions", response_model=List[RegionRecord])
def get_regions():
    """Regional analysis KPIs."""
    df = _read_csv("regional_analysis.csv")
    df["num_customers"] = df["num_customers"].astype(int)
    df["num_orders"] = df["num_orders"].astype(int)
    df["total_revenue"] = df["total_revenue"].round(2)
    df["avg_revenue_per_customer"] = df["avg_revenue_per_customer"].round(2)
    return df.to_dict(orient="records")

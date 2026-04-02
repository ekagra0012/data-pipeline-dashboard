"""
analyze.py — Data Merging & Analysis Pipeline

Merges cleaned datasets (customers_clean.csv, orders_clean.csv) with
products.csv and derives five business insight CSVs.

Usage:
    python analyze.py [--raw-dir data/raw] [--processed-dir data/processed]
"""

import argparse
import logging
import pathlib

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ── Shared utilities ──────────────────────────────────────────────────────────

def load_csv(path: pathlib.Path) -> pd.DataFrame:
    """Load a CSV with robust error handling."""
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{path} is empty")
        return df
    except FileNotFoundError:
        logger.error("File not found: %s", path)
        raise
    except pd.errors.EmptyDataError as exc:
        logger.error(str(exc))
        raise


# ── Merge steps ───────────────────────────────────────────────────────────────

def merge_datasets(
    orders_clean: pd.DataFrame,
    customers_clean: pd.DataFrame,
    products: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """F-17 + F-18: Two-step left join."""

    # Step 1: orders LEFT JOIN customers on customer_id
    orders_with_customers = pd.merge(
        orders_clean,
        customers_clean,
        on="customer_id",
        how="left",
        suffixes=("", "_cust"),
    )
    no_customer = orders_with_customers["name"].isna().sum()
    logger.info("Orders with no matching customer: %d", no_customer)

    # Step 2: orders_with_customers LEFT JOIN products on product = product_name
    full_data = pd.merge(
        orders_with_customers,
        products,
        left_on="product",
        right_on="product_name",
        how="left",
        suffixes=("", "_prod"),
    )
    no_product = full_data["product_id"].isna().sum()
    logger.info("Orders with no matching product: %d", no_product)

    return orders_with_customers, full_data


# ── Analysis functions ────────────────────────────────────────────────────────

def compute_monthly_revenue(full_data: pd.DataFrame) -> pd.DataFrame:
    """F-19: Monthly revenue trend for completed orders."""
    completed = full_data[full_data["status"] == "completed"]
    return (
        completed.groupby("order_year_month", as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_revenue"})
        .sort_values("order_year_month")
        .reset_index(drop=True)
    )


def compute_top_customers(full_data: pd.DataFrame) -> pd.DataFrame:
    """F-20: Top 10 customers by total spend (completed orders only)."""
    completed = full_data[full_data["status"] == "completed"]
    return (
        completed.groupby(["customer_id", "name", "region"], as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "total_spend"})
        .sort_values("total_spend", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )


def compute_category_performance(full_data: pd.DataFrame) -> pd.DataFrame:
    """F-21: Category performance for completed orders."""
    completed = full_data[full_data["status"] == "completed"]
    return (
        completed.groupby("category", as_index=False)
        .agg(
            total_revenue=("amount", "sum"),
            avg_order_value=("amount", "mean"),
            num_orders=("order_id", "count"),
        )
        .sort_values("total_revenue", ascending=False)
        .reset_index(drop=True)
    )


def compute_regional_analysis(
    full_data: pd.DataFrame,
    customers_clean: pd.DataFrame,
) -> pd.DataFrame:
    """F-22: Regional analysis combining customer counts and order metrics."""
    # num_customers per region from customers_clean
    region_customers = (
        customers_clean.groupby("region", as_index=False)["customer_id"]
        .nunique()
        .rename(columns={"customer_id": "num_customers"})
    )

    # num_orders + total_revenue from completed orders in full_data
    completed = full_data[full_data["status"] == "completed"]
    region_orders = (
        completed.groupby("region", as_index=False)
        .agg(
            num_orders=("order_id", "count"),
            total_revenue=("amount", "sum"),
        )
    )

    regional = pd.merge(region_customers, region_orders, on="region", how="left")
    regional["num_orders"] = regional["num_orders"].fillna(0).astype(int)
    regional["total_revenue"] = regional["total_revenue"].fillna(0.0)
    regional["avg_revenue_per_customer"] = (
        regional["total_revenue"] / regional["num_customers"]
    )
    cols = [
        "region", "num_customers", "num_orders",
        "total_revenue", "avg_revenue_per_customer",
    ]
    return regional[cols].reset_index(drop=True)


def add_churn_indicator(
    top_customers: pd.DataFrame,
    full_data: pd.DataFrame,
) -> pd.DataFrame:
    """F-23: Flag top customers with no completed orders in past 90 days as churned."""
    fd = full_data.copy()
    fd["order_date"] = pd.to_datetime(fd["order_date"], errors="coerce")

    latest_date = fd["order_date"].max()
    cutoff_date = latest_date - pd.Timedelta(days=90)

    active_ids = set(
        fd.loc[
            (fd["status"] == "completed") & (fd["order_date"] >= cutoff_date),
            "customer_id",
        ]
        .dropna()
        .unique()
    )

    top_customers = top_customers.copy()
    top_customers["churned"] = ~top_customers["customer_id"].isin(active_ids)
    return top_customers


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Merge and analyse cleaned CSVs")
    parser.add_argument(
        "--raw-dir", default="data/raw", help="Raw CSVs directory"
    )
    parser.add_argument(
        "--processed-dir",
        default="data/processed",
        help="Processed CSVs directory",
    )
    args = parser.parse_args()

    raw_dir = pathlib.Path(args.raw_dir)
    processed_dir = pathlib.Path(args.processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Load
    logger.info("Loading cleaned data...")
    customers_clean = load_csv(processed_dir / "customers_clean.csv")
    orders_clean = load_csv(processed_dir / "orders_clean.csv")
    products = load_csv(raw_dir / "products.csv")

    # Merge
    logger.info("Merging datasets...")
    _, full_data = merge_datasets(orders_clean, customers_clean, products)

    # Analysis
    logger.info("Computing monthly revenue trend...")
    monthly_revenue = compute_monthly_revenue(full_data)
    monthly_revenue.to_csv(processed_dir / "monthly_revenue.csv", index=False)

    logger.info("Computing top customers...")
    top_customers = compute_top_customers(full_data)

    logger.info("Computing category performance...")
    cat_perf = compute_category_performance(full_data)
    cat_perf.to_csv(processed_dir / "category_performance.csv", index=False)

    logger.info("Computing regional analysis...")
    regional = compute_regional_analysis(full_data, customers_clean)
    regional.to_csv(processed_dir / "regional_analysis.csv", index=False)

    logger.info("Adding churn indicators...")
    top_customers = add_churn_indicator(top_customers, full_data)
    top_customers.to_csv(processed_dir / "top_customers.csv", index=False)

    logger.info("✅ All 5 analysis CSVs saved to: %s", processed_dir)
    logger.info("Run the backend next: cd backend && uvicorn main:app --reload")


if __name__ == "__main__":
    main()

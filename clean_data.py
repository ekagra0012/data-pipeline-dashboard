"""
clean_data.py — Data Cleaning Pipeline

Cleans customers.csv and orders.csv from raw data, producing
customers_clean.csv and orders_clean.csv in the processed directory.

Usage:
    python clean_data.py [--input-dir data/raw] [--output-dir data/processed]
"""

import argparse
import logging
import pathlib

import pandas as pd
import numpy as np  # noqa: F401 (available for downstream use)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# F-14: Status normalisation map
STATUS_MAP = {
    "done": "completed",
    "complete": "completed",
    "completed": "completed",
    "Completed": "completed",
    "COMPLETED": "completed",
    "canceled": "cancelled",
    "cancelled": "cancelled",
    "Cancelled": "cancelled",
    "CANCELLED": "cancelled",
    "Canceled": "cancelled",
    "pending": "pending",
    "Pending": "pending",
    "PENDING": "pending",
    "refunded": "refunded",
    "Refunded": "refunded",
    "REFUNDED": "refunded",
}


# ── Shared utilities ──────────────────────────────────────────────────────────

def load_csv(path: pathlib.Path) -> pd.DataFrame:
    """Load a CSV with robust error handling (F-25)."""
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


def _null_counts(df: pd.DataFrame) -> dict:
    counts = df.isnull().sum()
    return {col: int(c) for col, c in counts.items() if c > 0}


# ── customers.csv cleaning ────────────────────────────────────────────────────

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    rows_before = len(df)
    null_before = _null_counts(df)

    # F-06: Deduplication — keep row with most recent signup_date per customer_id
    df["_signup_dt"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df = df.sort_values("_signup_dt", ascending=False, na_position="last")
    dupes_removed = int(df.duplicated(subset="customer_id", keep="first").sum())
    df = df.drop_duplicates(subset="customer_id", keep="first").copy()
    logger.info("[customers] Duplicates removed: %d", dupes_removed)

    # F-07: Email standardisation + is_valid_email flag
    df["email"] = df["email"].str.lower()
    df["is_valid_email"] = (
        df["email"].notna()
        & df["email"].str.contains("@", na=False)
        & df["email"].str.contains(r"\.", na=False, regex=True)
    )

    # F-08: signup_date parsing → YYYY-MM-DD
    def _parse_signup(val, idx):
        result = pd.to_datetime(val, errors="coerce")
        if pd.isna(result) and pd.notna(val):
            logger.warning("Unparseable signup_date at row %s: '%s'", idx, val)
        return result

    df["signup_date"] = df.apply(
        lambda row: _parse_signup(row["signup_date"], row.name), axis=1
    )
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # F-09: Whitespace stripping
    df["name"] = df["name"].map(lambda x: x.strip() if isinstance(x, str) else x)
    df["region"] = df["region"].map(lambda x: x.strip() if isinstance(x, str) else x)

    # F-10: Fill missing region
    df["region"] = df["region"].fillna("Unknown")

    df = df.drop(columns=["_signup_dt"], errors="ignore")

    null_after = _null_counts(df)
    print(f"\n[customers.csv]")
    print(f"  Rows before: {rows_before} | Rows after: {len(df)} | Duplicates removed: {dupes_removed}")
    print(f"  Null counts before: {null_before}")
    print(f"  Null counts after:  {null_after}")

    return df


# ── orders.csv cleaning ───────────────────────────────────────────────────────

def parse_order_date(val) -> pd.Timestamp:
    """F-11: Try parsing a date in three formats; return NaT on failure."""
    if pd.isna(val):
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            pass
    return pd.NaT


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    rows_before = len(df)
    null_before = _null_counts(df)

    # F-11: Multi-format date parsing
    df["order_date"] = df["order_date"].apply(parse_order_date)

    # F-12: Drop rows where both order_id AND customer_id are null
    unrecoverable = df["order_id"].isna() & df["customer_id"].isna()
    unrecoverable_count = int(unrecoverable.sum())
    df = df[~unrecoverable].copy()
    logger.info("[orders] Unrecoverable rows dropped: %d", unrecoverable_count)

    # F-13: Amount imputation (product-level median, fallback to global median)
    global_median = df["amount"].median()
    product_median = df.groupby("product")["amount"].transform("median")
    df["amount"] = df["amount"].fillna(product_median).fillna(global_median)

    # F-14: Status normalisation
    original = df["status"].copy()
    df["status"] = df["status"].str.strip().map(STATUS_MAP)
    unmapped = original[df["status"].isna() & original.notna()].unique()
    if len(unmapped):
        logger.warning("Unmapped status values (→ 'pending'): %s", list(unmapped))
    df["status"] = df["status"].fillna("pending")

    # F-15: order_year_month derivation
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")

    null_after = _null_counts(df)
    print(f"\n[orders.csv]")
    print(f"  Rows before: {rows_before} | Rows after: {len(df)} | Unrecoverable rows dropped: {unrecoverable_count}")
    print(f"  Null counts before: {null_before}")
    print(f"  Null counts after:  {null_after}")

    return df


# ── Entry point ───────────────────────────────────────────────────────────────

def _ensure_raw_data(input_dir: pathlib.Path) -> None:
    """Auto-generate raw CSVs if they're missing (zero-intervention guarantee)."""
    required = ["customers.csv", "orders.csv", "products.csv"]
    missing = [f for f in required if not (input_dir / f).exists()]
    if missing:
        logger.warning(
            "Missing raw files %s in '%s' — auto-generating via generate_data.py...",
            missing,
            input_dir,
        )
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "generate_data.py", "--output-dir", str(input_dir)],
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"generate_data.py failed (exit {result.returncode}). "
                "Ensure generate_data.py exists and Faker is installed."
            )
        logger.info("Raw data generated successfully.")


def main():
    parser = argparse.ArgumentParser(description="Clean raw CSV data files")
    parser.add_argument("--input-dir", default="data/raw", help="Raw CSVs directory")
    parser.add_argument("--output-dir", default="data/processed", help="Output directory")
    args = parser.parse_args()

    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Zero-intervention: auto-generate raw data if not present
    _ensure_raw_data(input_dir)

    print("=== CLEANING REPORT ===")

    customers = load_csv(input_dir / "customers.csv")
    customers_clean = clean_customers(customers)
    customers_clean.to_csv(output_dir / "customers_clean.csv", index=False)
    logger.info("Saved customers_clean.csv → %s", output_dir)

    orders = load_csv(input_dir / "orders.csv")
    orders_clean = clean_orders(orders)
    orders_clean.to_csv(output_dir / "orders_clean.csv", index=False)
    logger.info("Saved orders_clean.csv → %s", output_dir)

    print("\n=== DONE — Run analyze.py next ===")


if __name__ == "__main__":
    main()

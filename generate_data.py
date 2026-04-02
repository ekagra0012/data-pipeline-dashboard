"""
generate_data.py — Synthetic CSV Dataset Generator

Generates customers.csv, orders.csv, and products.csv with intentional
anomalies to simulate real-world messy data. Uses a fixed seed for full
reproducibility.

Usage:
    python generate_data.py [--output-dir data/raw]
"""

import argparse
import pathlib
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
fake = Faker()
Faker.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

# ── Product catalogue (30 products; last 5 are "orphans" — never ordered) ─────
PRODUCT_CATALOGUE = [
    # Active products (referenced in orders)
    ("Laptop Pro", "Electronics", 1299.99),
    ("Wireless Mouse", "Electronics", 29.99),
    ("Standing Desk", "Furniture", 449.99),
    ("Office Chair", "Furniture", 299.99),
    ("Notebook Set", "Stationery", 12.99),
    ("Pen Pack", "Stationery", 4.99),
    ('Monitor 27"', "Electronics", 399.99),
    ("USB Hub", "Electronics", 39.99),
    ("Webcam HD", "Electronics", 89.99),
    ("Headphones", "Electronics", 149.99),
    ("Coffee Maker", "Appliances", 79.99),
    ("Desk Lamp", "Furniture", 34.99),
    ("Mechanical Keyboard", "Electronics", 129.99),
    ("Mouse Pad XL", "Accessories", 19.99),
    ("Cable Organizer", "Accessories", 9.99),
    ("Backpack", "Bags", 59.99),
    ("Laptop Stand", "Accessories", 49.99),
    ("Phone Mount", "Accessories", 14.99),
    ("Whiteboard", "Office", 89.99),
    ("Sticky Notes", "Stationery", 3.99),
    ("Stapler", "Office", 8.99),
    ("Document Tray", "Office", 17.99),
    ("Marker Set", "Stationery", 11.99),
    ("File Folders", "Office", 7.99),
    ("Scissors", "Office", 5.99),
    # ── 5 orphan products (no orders will reference these) ────────────────────
    ("4K Projector", "Electronics", 799.99),
    ("Smart Thermostat", "Electronics", 199.99),
    ("Air Purifier", "Appliances", 249.99),
    ("Ergonomic Footrest", "Furniture", 54.99),
    ("Cable Management Kit", "Accessories", 22.99),
]

ACTIVE_PRODUCTS = [p[0] for p in PRODUCT_CATALOGUE[:25]]
REGIONS = ["North", "South", "East", "West", "Central"]

STATUS_VARIANTS = [
    "completed", "Completed", "COMPLETED", "done",
    "cancelled", "canceled", "Cancelled",
    "pending", "Pending", "PENDING",
    "refunded", "Refunded",
]


def _random_date(start_year: int = 2022, end_year: int = 2024) -> datetime:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))


def generate_products(output_dir: pathlib.Path) -> None:
    rows = [
        {
            "product_id": f"P{i + 1:03d}",
            "product_name": name,
            "category": category,
            "unit_price": price,
        }
        for i, (name, category, price) in enumerate(PRODUCT_CATALOGUE)
    ]
    pd.DataFrame(rows).to_csv(output_dir / "products.csv", index=False)
    print(f"  ✓ products.csv — {len(rows)} rows (5 orphan products included)")


def generate_customers(output_dir: pathlib.Path, n: int = 500) -> list:
    """Returns list of customer_ids for use in order generation."""
    customer_ids = [f"C{i + 1:04d}" for i in range(n)]
    rows = []

    for cid in customer_ids:
        date = _random_date()

        # F-01: 3% unparseable signup_dates
        if random.random() < 0.03:
            date_str = fake.word()
        else:
            date_str = date.strftime("%Y-%m-%d")

        # F-01: 8% missing emails, 5% malformed emails
        email = fake.email()
        r = random.random()
        if r < 0.08:
            email = None
        elif r < 0.13:
            if random.random() < 0.5:
                email = email.replace("@", "")   # no @
            else:
                email = email.split(".")[0] + "@example"   # no .

        # F-01: mixed whitespace in region (10%)
        region = random.choice(REGIONS)
        if random.random() < 0.10:
            region = "  " + region + "  "

        rows.append({
            "customer_id": cid,
            "name": fake.name(),
            "email": email,
            "region": region,
            "signup_date": date_str,
        })

    # F-01: ~10% duplicate customer_ids (older signup_date)
    n_dupes = int(n * 0.10)
    for source in random.sample(rows, n_dupes):
        dupe = source.copy()
        try:
            d = datetime.strptime(source["signup_date"], "%Y-%m-%d")
            dupe["signup_date"] = (
                (d - timedelta(days=random.randint(1, 60)))
                .strftime("%Y-%m-%d")
            )
        except (ValueError, TypeError):
            pass
        rows.append(dupe)

    random.shuffle(rows)
    pd.DataFrame(rows).to_csv(output_dir / "customers.csv", index=False)
    print(
        f"  ✓ customers.csv — {len(rows)} rows "
        f"(~{n_dupes} duplicates, anomalies injected)"
    )
    return customer_ids


def _order_date_str(date: datetime) -> str:
    """Randomly pick one of three date formats."""
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"])
    return date.strftime(fmt)


def generate_orders(
    output_dir: pathlib.Path, customer_ids: list, n: int = 2000
) -> None:
    # Weight toward 'completed' so analysis has enough data
    status_pool = STATUS_VARIANTS * 2 + ["completed"] * 12
    rows = []

    for i in range(n):
        order_id = f"O{i + 1:05d}"
        cid = random.choice(customer_ids)
        product = random.choice(ACTIVE_PRODUCTS)
        amount = round(random.uniform(10.0, 1500.0), 2)
        date = _random_date()

        # F-02: 5% null amounts
        if random.random() < 0.05:
            amount = None

        # F-02: 3% both order_id and customer_id null (unrecoverable)
        if random.random() < 0.03:
            order_id = None
            cid = None

        rows.append({
            "order_id": order_id,
            "customer_id": cid,
            "product": product,
            "amount": amount,
            "order_date": _order_date_str(date),
            "status": random.choice(status_pool),
        })

    pd.DataFrame(rows).to_csv(output_dir / "orders.csv", index=False)
    print(f"  ✓ orders.csv — {len(rows)} rows (mixed date formats, anomalies injected)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic CSV datasets with anomalies"
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Output directory (default: data/raw)",
    )
    args = parser.parse_args()

    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating data with seed={SEED} → {output_dir}/")
    generate_products(output_dir)
    customer_ids = generate_customers(output_dir)
    generate_orders(output_dir, customer_ids)
    print("Done. Run clean_data.py next.")


if __name__ == "__main__":
    main()

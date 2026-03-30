"""
tests/test_cleaning.py — Unit tests for data cleaning functions

Run with:
    pytest tests/ -v
"""

import sys
import pathlib

import numpy as np
import pandas as pd
import pytest

# Ensure project root is importable
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from clean_data import (
    STATUS_MAP,
    clean_customers,
    clean_orders,
    parse_order_date,
)


# ── Test 1: Multi-format date parser ──────────────────────────────────────────

class TestParseOrderDate:
    def test_iso_format(self):
        assert parse_order_date("2023-06-15") == pd.Timestamp("2023-06-15")

    def test_dmy_slash_format(self):
        assert parse_order_date("15/06/2023") == pd.Timestamp("2023-06-15")

    def test_mdy_dash_format(self):
        assert parse_order_date("06-15-2023") == pd.Timestamp("2023-06-15")

    def test_invalid_returns_nat(self):
        assert pd.isna(parse_order_date("not-a-date"))

    def test_none_returns_nat(self):
        assert pd.isna(parse_order_date(None))

    def test_nan_returns_nat(self):
        assert pd.isna(parse_order_date(float("nan")))


# ── Test 2: Email validation ──────────────────────────────────────────────────

class TestEmailValidation:
    def _make_df(self):
        return pd.DataFrame({
            "customer_id": ["C001", "C002", "C003", "C004", "C005"],
            "name":        ["Alice", "Bob", "Charlie", "Dave", "Eve"],
            "email":       [
                "alice@example.com",   # valid
                None,                  # missing
                "bobexample.com",      # no @
                "charlie@nodot",       # no .
                "eve@test.io",         # valid
            ],
            "region":      ["North"] * 5,
            "signup_date": ["2023-01-15"] * 5,
        })

    def test_valid_email_flagged_true(self):
        result = clean_customers(self._make_df())
        assert result.loc[result["name"] == "Alice", "is_valid_email"].values[0] == True

    def test_null_email_flagged_false(self):
        result = clean_customers(self._make_df())
        assert result.loc[result["name"] == "Bob", "is_valid_email"].values[0] == False

    def test_no_at_sign_flagged_false(self):
        result = clean_customers(self._make_df())
        assert result.loc[result["name"] == "Charlie", "is_valid_email"].values[0] == False

    def test_no_dot_flagged_false(self):
        result = clean_customers(self._make_df())
        assert result.loc[result["name"] == "Dave", "is_valid_email"].values[0] == False


# ── Test 3: Status normalization ──────────────────────────────────────────────

class TestStatusNormalization:
    def _make_df(self, statuses):
        return pd.DataFrame({
            "order_id":    [f"O{i:03d}" for i in range(len(statuses))],
            "customer_id": ["C001"] * len(statuses),
            "product":     ["Widget"] * len(statuses),
            "amount":      [100.0] * len(statuses),
            "order_date":  ["2023-01-01"] * len(statuses),
            "status":      statuses,
        })

    def test_done_maps_to_completed(self):
        result = clean_orders(self._make_df(["done"]))
        assert result["status"].iloc[0] == "completed"

    def test_canceled_maps_to_cancelled(self):
        result = clean_orders(self._make_df(["canceled"]))
        assert result["status"].iloc[0] == "cancelled"

    def test_uppercase_completed_normalised(self):
        result = clean_orders(self._make_df(["COMPLETED"]))
        assert result["status"].iloc[0] == "completed"

    def test_pending_variants_normalised(self):
        result = clean_orders(self._make_df(["PENDING", "Pending"]))
        assert (result["status"] == "pending").all()

    def test_unknown_status_defaults_to_pending(self):
        result = clean_orders(self._make_df(["totally_unknown"]))
        assert result["status"].iloc[0] == "pending"

    def test_all_status_map_values_are_valid(self):
        valid = {"completed", "cancelled", "pending", "refunded"}
        assert set(STATUS_MAP.values()).issubset(valid)


# ── Test 4: Deduplication keeps most recent signup_date ───────────────────────

class TestDeduplication:
    def test_keeps_most_recent(self):
        df = pd.DataFrame({
            "customer_id": ["C001", "C001", "C002"],
            "name":        ["Alice Old", "Alice New", "Bob"],
            "email":       ["alice@ex.com", "alice@ex.com", "bob@ex.com"],
            "region":      ["North", "North", "South"],
            "signup_date": ["2022-01-01", "2023-06-15", "2022-05-10"],
        })
        result = clean_customers(df)
        assert len(result) == 2
        alice = result[result["customer_id"] == "C001"]
        assert "2023" in alice["signup_date"].values[0]

    def test_duplicate_count_correct(self):
        df = pd.DataFrame({
            "customer_id": ["C001", "C001", "C001", "C002"],
            "name":        ["A", "A", "A", "B"],
            "email":       ["a@x.com"] * 3 + ["b@x.com"],
            "region":      ["North"] * 4,
            "signup_date": ["2022-01-01", "2022-06-01", "2023-01-01", "2021-01-01"],
        })
        result = clean_customers(df)
        assert len(result) == 2  # 2 unique customer_ids


# ── Test 5: Amount imputation ─────────────────────────────────────────────────

class TestAmountImputation:
    def test_product_level_median_filled(self):
        df = pd.DataFrame({
            "order_id":    ["O001", "O002", "O003"],
            "customer_id": ["C001", "C002", "C003"],
            "product":     ["Laptop", "Laptop", "Laptop"],
            "amount":      [100.0, 200.0, None],
            "order_date":  ["2023-01-01"] * 3,
            "status":      ["completed"] * 3,
        })
        result = clean_orders(df)
        # Median of 100 and 200 = 150
        assert result.loc[result["order_id"] == "O003", "amount"].values[0] == 150.0

    def test_global_median_fallback(self):
        """When entire product group is null, fall back to global median."""
        df = pd.DataFrame({
            "order_id":    ["O001", "O002", "O003"],
            "customer_id": ["C001", "C002", "C003"],
            "product":     ["Mouse", "Mouse", "Laptop"],
            "amount":      [None, None, 200.0],  # Mouse has no amounts
            "order_date":  ["2023-01-01"] * 3,
            "status":      ["completed"] * 3,
        })
        result = clean_orders(df)
        mouse_amounts = result.loc[result["product"] == "Mouse", "amount"]
        assert not mouse_amounts.isna().any()

    def test_no_null_amounts_after_imputation(self):
        df = pd.DataFrame({
            "order_id":    [f"O{i}" for i in range(10)],
            "customer_id": [f"C{i}" for i in range(10)],
            "product":     ["Widget"] * 5 + ["Gadget"] * 5,
            "amount":      [10.0, None, 20.0, None, 30.0, None, 40.0, None, 50.0, None],
            "order_date":  ["2023-01-01"] * 10,
            "status":      ["completed"] * 10,
        })
        result = clean_orders(df)
        assert result["amount"].isna().sum() == 0

# PRD & SRS: Data Pipeline & Analytics Dashboard
### Document Version: 1.0 | Author: Antigravity Dev Team | Date: 2026-04-02

---

# PART A — PRODUCT REQUIREMENTS DOCUMENT (PRD)

---

## 1. Executive Summary

This document defines the complete product and system requirements for a
self-contained, end-to-end data pipeline and analytics dashboard application.
The system ingests raw CSV data, cleans and transforms it using Python, merges
multiple datasets, performs business analysis, and surfaces the results through
a professional fullstack web application.

The solution is built to demonstrate senior-level competency across data
engineering, backend API development, and modern frontend development — with
production-grade code quality, test coverage, and documentation.

---

## 2. Problem Statement

Businesses routinely receive raw operational data that is:
- Duplicated, inconsistently formatted, and riddled with nulls
- Scattered across multiple disconnected files with no relational integrity
- Never surfaced to decision-makers in a consumable, visual format

This assignment simulates exactly that scenario. The goal is to build a
pipeline that takes three messy CSVs and turns them into an interactive,
recruiter-facing analytics dashboard — demonstrating both technical depth and
product thinking.

---

## 3. Goals & Success Criteria

### 3.1 Primary Goals
| ID | Goal | Success Metric |
|----|------|---------------|
| G-01 | Clean all three CSVs with zero data loss beyond unrecoverable rows | Cleaning report shows exact counts |
| G-02 | Produce 5 accurate analytical CSV outputs | All outputs pass manual spot-check |
| G-03 | Expose a stable REST API with 5 endpoints | All endpoints return 200 or correct error codes |
| G-04 | Render a professional, responsive dashboard | Passes on 1280px and 375px viewports |
| G-05 | Achieve 100% rubric coverage | Every rubric line has a traceable deliverable |

### 3.2 Out of Scope
- Real-time data ingestion or streaming
- User authentication or multi-tenancy
- Database persistence (CSV files are the data layer)
- Deployment to a cloud provider

---

## 4. User Personas

### Persona 1 — The Recruiter / Evaluator
- **Name:** Priya (Senior Engineering Manager)
- **Goal:** Assess code quality, architecture decisions, and UI polish in
  under 15 minutes
- **Pain Point:** Most submissions are incomplete or have broken UIs
- **What Impresses Her:** Clean folder structure, readable code, a dashboard
  that works on first run, and a README she can follow without guessing

### Persona 2 — The Follow-up Interviewer
- **Name:** Rohan (Staff Data Engineer)
- **Goal:** Understand the candidate's reasoning behind every design choice
- **Pain Point:** Candidates who copy code they cannot explain
- **What Impresses Him:** Modular functions, explicit merge arguments, custom
  date parsers, and unit tests that prove the logic works

---

## 5. User Stories

| ID | As a… | I want to… | So that… |
|----|-------|-----------|---------|
| US-01 | Evaluator | Run clean_data.py and see a cleaning report | I can verify data quality without opening files |
| US-02 | Evaluator | Run analyze.py and get 5 CSVs | I can validate business logic output |
| US-03 | Evaluator | Start the backend and hit /health | I know the server is running |
| US-04 | Evaluator | Open the dashboard and see charts load | I can assess frontend quality immediately |
| US-05 | Evaluator | Resize the browser to 375px | I can verify responsive design |
| US-06 | Evaluator | Kill the backend and reload a chart | I see a user-friendly error state, not a crash |
| US-07 | Interviewer | Read clean_data.py | I understand every transformation with no ambiguity |
| US-08 | Interviewer | Read analyze.py | I can verify merge correctness and business logic |
| US-09 | Interviewer | Run pytest | I see green tests with meaningful assertions |
| US-10 | Interviewer | Read README.md | I can reproduce the full pipeline in under 5 minutes |
| US-11 | Dashboard User | Filter revenue chart by date range | I can focus on a specific time window |
| US-12 | Dashboard User | Search the top customers table | I can find a specific customer instantly |

---

## 6. Feature Requirements

### 6.1 Data Generation (F-01 to F-05)

**F-01 — customers.csv Generation**
- 500 rows minimum
- Columns: customer_id, name, email, region, signup_date
- Intentional anomalies: 10% duplicate customer_ids, 8% missing emails,
  5% malformed emails (missing @ or .), 3% unparseable signup_dates,
  mixed whitespace in name and region

**F-02 — orders.csv Generation**
- 2000 rows minimum
- Columns: order_id, customer_id, product, amount, order_date, status
- Intentional anomalies: mixed date formats across three patterns, 5% null
  amounts, 3% rows where both order_id and customer_id are null, status
  values include 'done', 'canceled', 'COMPLETED', 'Pending', 'refunded'

**F-03 — products.csv Generation**
- 30 rows minimum
- Columns: product_id, product_name, category, unit_price
- At least 5 products with no matching orders (orphan records)

**F-04 — generate_data.py Script**
- A standalone script using the Faker library that produces all three CSVs
  deterministically via a fixed random seed
- Output path: data/raw/

**F-05 — Reproducibility**
- Running generate_data.py twice with the same seed must produce identical files

---

### 6.2 Data Cleaning — customers.csv (F-06 to F-10)

**F-06 — Deduplication**
- Identify duplicate rows by customer_id
- Among duplicates, parse signup_date and retain the row with the
  most recent (maximum) signup_date
- If signup_dates are equal, keep the first occurrence
- Log count of removed duplicates to stdout

**F-07 — Email Standardization & Validation**
- Apply str.lower() to all email values
- Add boolean column is_valid_email
- Set is_valid_email = False when: email is NaN/null, email does not
  contain '@', email does not contain '.'
- All other emails receive is_valid_email = True

**F-08 — signup_date Parsing**
- Attempt parsing with pd.to_datetime using infer_datetime_format=True
- On failure (NaT result), log a warning via Python's logging module
  with the row index and original value
- Final column dtype must be datetime64[ns]
- Output format in CSV: YYYY-MM-DD (using .dt.strftime)

**F-09 — Whitespace Stripping**
- Apply str.strip() to name and region columns
- Handle NaN values without raising exceptions (use na_action='ignore'
  or fillna before strip)

**F-10 — Missing Region Fill**
- After stripping, fill any remaining null values in region with the
  string literal 'Unknown'

---

### 6.3 Data Cleaning — orders.csv (F-11 to F-16)

**F-11 — Multi-Format Date Parser**
- Implement parse_order_date(val: str) -> pd.Timestamp function
- Try formats in order: '%Y-%m-%d', '%d/%m/%Y', '%m-%d-%Y'
- Return pd.NaT if all formats fail
- Apply via df['order_date'] = df['order_date'].apply(parse_order_date)

**F-12 — Unrecoverable Row Removal**
- Drop rows where BOTH order_id IS NULL AND customer_id IS NULL
- Condition: df[df['order_id'].isna() & df['customer_id'].isna()]
- Log count of dropped rows

**F-13 — Amount Imputation**
- Compute median amount grouped by product:
  df.groupby('product')['amount'].transform('median')
- Fill nulls in amount with the product-level median
- If a product has no non-null amounts (entire group is null),
  fall back to the global median

**F-14 — Status Normalization**
- Define a STATUS_MAP dictionary:
  {
    'done': 'completed',
    'complete': 'completed',
    'COMPLETED': 'completed',
    'Completed': 'completed',
    'canceled': 'cancelled',
    'CANCELLED': 'cancelled',
    'Cancelled': 'cancelled',
    'pending': 'pending',
    'PENDING': 'pending',
    'Pending': 'pending',
    'refunded': 'refunded',
    'REFUNDED': 'refunded',
    'Refunded': 'refunded'
  }
- Apply: df['status'] = df['status'].str.strip().map(STATUS_MAP)
- Any value not in map becomes NaN — fill with 'pending' as default
  and log a warning listing the unmapped values

**F-15 — order_year_month Derivation**
- After parsing order_date, add:
  df['order_year_month'] = df['order_date'].dt.strftime('%Y-%m')
- Rows where order_date is NaT will have NaN in this column — acceptable

**F-16 — Output & Cleaning Report**
- Save customers_clean.csv and orders_clean.csv to data/processed/
- Print to stdout:
  === CLEANING REPORT ===
  [customers.csv]
    Rows before: X | Rows after: Y | Duplicates removed: Z
    Null counts before: {col: count, ...}
    Null counts after:  {col: count, ...}
  [orders.csv]
    Rows before: X | Rows after: Y | Unrecoverable rows dropped: Z
    Null counts before: {col: count, ...}
    Null counts after:  {col: count, ...}

---

### 6.4 Data Merging & Analysis (F-17 to F-25)

**F-17 — Merge Step 1: orders_with_customers**
- pd.merge(orders_clean, customers_clean, on='customer_id', how='left')
- Log: "Orders with no matching customer: N"

**F-18 — Merge Step 2: full_data**
- pd.merge(orders_with_customers, products,
           left_on='product', right_on='product_name', how='left')
- Log: "Orders with no matching product: N"

**F-19 — Monthly Revenue Trend**
- Filter: status == 'completed'
- Group by: order_year_month
- Aggregate: total_revenue = sum(amount)
- Sort by order_year_month ascending
- Output: data/processed/monthly_revenue.csv
- Columns: order_year_month, total_revenue

**F-20 — Top 10 Customers**
- Filter: status == 'completed'
- Group by: customer_id, name, region
- Aggregate: total_spend = sum(amount)
- Sort descending, take top 10
- Output: data/processed/top_customers.csv (without churn flag yet)
- Columns: customer_id, name, region, total_spend

**F-21 — Category Performance**
- Filter: status == 'completed'
- Group by: category
- Aggregate:
  total_revenue = sum(amount)
  avg_order_value = mean(amount)
  num_orders = count(order_id)
- Output: data/processed/category_performance.csv
- Columns: category, total_revenue, avg_order_value, num_orders

**F-22 — Regional Analysis**
- num_customers: count distinct customer_ids per region from customers_clean
- num_orders: count orders per region from full_data
- total_revenue: sum(amount) for completed orders per region
- avg_revenue_per_customer: total_revenue / num_customers
- Output: data/processed/regional_analysis.csv
- Columns: region, num_customers, num_orders, total_revenue,
  avg_revenue_per_customer

**F-23 — Churn Indicator**
- latest_date = full_data['order_date'].max()
- cutoff_date = latest_date - pd.Timedelta(days=90)
- active_customers = set of customer_ids with at least one completed
  order where order_date >= cutoff_date
- In top_customers DataFrame:
  top_customers['churned'] = ~top_customers['customer_id']
                               .isin(active_customers)
- Re-save top_customers.csv with the churned column appended

**F-24 — argparse Configuration**
- analyze.py accepts:
  --raw-dir      (default: data/raw)
  --processed-dir (default: data/processed)
- clean_data.py accepts:
  --input-dir    (default: data/raw)
  --output-dir   (default: data/processed)

**F-25 — File Loading Function**
def load_csv(path: pathlib.Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{path} is empty")
        return df
    except FileNotFoundError:
        logging.error(f"File not found: {path}")
        raise
    except pd.errors.EmptyDataError as e:
        logging.error(str(e))
        raise

---

### 6.5 Backend API (F-26 to F-31)

**F-26 — Framework & Structure**
- FastAPI with Uvicorn ASGI server
- Entry point: backend/main.py
- Router file: backend/routers/data.py
- Pydantic models: backend/models/schemas.py
- Config: backend/config.py (DATA_DIR path from environment variable
  or default)

**F-27 — CORS Configuration**
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

**F-28 — Endpoints**
| Method | Path | Response Model | CSV Source |
|--------|------|---------------|------------|
| GET | /health | {"status": "ok"} | — |
| GET | /api/revenue | List[RevenueRecord] | monthly_revenue.csv |
| GET | /api/top-customers | List[CustomerRecord] | top_customers.csv |
| GET | /api/categories | List[CategoryRecord] | category_performance.csv |
| GET | /api/regions | List[RegionRecord] | regional_analysis.csv |

**F-29 — Pydantic Response Models**
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

**F-30 — Error Handling**
- FileNotFoundError → HTTP 404 with body:
  {"detail": "Data file not found. Run analyze.py first."}
- pd.errors.EmptyDataError → HTTP 500 with body:
  {"detail":
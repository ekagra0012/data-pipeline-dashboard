# Data Pipeline & Analytics Dashboard

End-to-end data engineering and fullstack dashboard assignment.  
**Stack:** Python · pandas · FastAPI · React (Vite) · Recharts

---

## Prerequisites

- Python **3.9 or above** (`python --version`)
- Node.js **18 or above** (`node --version`)
- Docker Desktop (for containerised deployment)
- `pip` and `npm` available in PATH

---

## Quick Start (5 minutes)

### 1. Install dependencies

```bash
# Python
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Generate raw data

```bash
python generate_data.py
# → data/raw/customers.csv (550 rows), orders.csv (2000 rows), products.csv (30 rows)
```

### 3. Clean the data

```bash
python clean_data.py
# Prints a cleaning report to stdout
# → data/processed/customers_clean.csv, orders_clean.csv
```

### 4. Run analysis

```bash
python analyze.py
# → data/processed/monthly_revenue.csv
#                   top_customers.csv
#                   category_performance.csv
#                   regional_analysis.csv
```

### 5. Start the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Verify it's live:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### 6. Start the frontend

```bash
# Dev mode (Vite, with HMR):
cd frontend && npm run dev
# Open: http://localhost:3000

# --- OR: production build served statically ---
cd frontend && npm run build
python -m http.server 3000 --directory dist
```

---

## API Endpoints

| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| GET    | `/health`           | Health check                       |
| GET    | `/api/revenue`      | Monthly revenue trend              |
| GET    | `/api/top-customers`| Top 10 customers with churn status |
| GET    | `/api/categories`   | Category performance metrics       |
| GET    | `/api/regions`      | Regional KPIs                      |

All endpoints return 404 with `{"detail": "Data file not found. Run analyze.py first."}` if CSVs haven't been generated yet.

---

## Run Tests

```bash
python -m pytest tests/ -v
```

Expected: **5 test classes, 20+ assertions**, all green.

---

## Project Structure

```
multiplierAI_assignment/
├── generate_data.py         # Part 0: Faker-based data generation (seed=42)
├── clean_data.py            # Part 1: Data cleaning pipeline
├── analyze.py               # Part 2: Merging & analysis
├── requirements.txt
│
├── backend/
│   ├── main.py              # FastAPI app (CORS + StaticFiles mount)
│   ├── config.py            # DATA_DIR / FRONTEND_DIR from env vars
│   ├── routers/data.py      # 4 data endpoints
│   └── models/schemas.py    # Pydantic response models
│
├── frontend/                # Vite + React dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js           # Fetch utility
│   │   ├── utils/formatters.js
│   │   ├── hooks/useAPIData.js
│   │   ├── pages/Dashboard.jsx
│   │   └── components/
│   │       ├── Layout/Sidebar.jsx
│   │       ├── Layout/TopBar.jsx
│   │       ├── charts/RevenueChart.jsx  # ← bonus: date-range filter
│   │       ├── charts/CategoryChart.jsx
│   │       ├── tables/CustomersTable.jsx # ← bonus: search box
│   │       ├── cards/RegionCard.jsx
│   │       ├── ui/KPICard.jsx
│   │       ├── ui/SkeletonLoader.jsx
│   │       └── ui/ErrorBanner.jsx
│   └── vite.config.js       # Port 3000, /api proxy → :8000
│
├── tests/
│   └── test_cleaning.py     # pytest: 5 classes, 20+ assertions
│
├── Dockerfile
└── docker-compose.yml       # Backend :8000 + Frontend :3000 + data volume
```

---

## Docker

```bash
# First generate and process data locally, then:
docker-compose up --build

# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Fixed seed (42) | Full reproducibility — two runs produce identical files |
| `parse_order_date()` custom parser | Handles 3 date formats; returns `pd.NaT` on failure as required |
| Product-level median imputation | Preserves realistic pricing; global median as safe fallback |
| Left joins (explicit `on=` + `how=`) | No silent inner-join data loss; orphan rows visible |
| FastAPI + StaticFiles mount | One port covers both API and frontend in production |
| Churn window: 90 days from `max(order_date)` | Dataset-relative; avoids dependency on wall-clock time |

---

## Environment Variables

| Variable       | Default              | Description                        |
|----------------|----------------------|------------------------------------|
| `DATA_DIR`     | `data/processed`     | Path to processed CSV files        |
| `FRONTEND_DIR` | `frontend/dist`      | Path to built React app            |
| `VITE_API_BASE`| `http://localhost:8000` | Frontend API base URL           |

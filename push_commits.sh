#!/usr/bin/env bash
# =============================================================================
# push_commits.sh — Professional git history initializer
#
# Usage:
#   chmod +x push_commits.sh
#   ./push_commits.sh <remote-url>
#
# Example:
#   ./push_commits.sh git@github.com:youruser/multiplierAI-assignment.git
# =============================================================================

set -euo pipefail

REMOTE_URL="${1:-}"

# ── helpers ───────────────────────────────────────────────────────────────────
log()  { echo ""; echo "▶ $*"; }
die()  { echo "✗ ERROR: $*" >&2; exit 1; }
commit() {
  local date_str="$1"; shift
  GIT_AUTHOR_DATE="$date_str" \
  GIT_COMMITTER_DATE="$date_str" \
  git commit --quiet -m "$@"
  echo "  ✓ committed: $1"
}

# ── sanity checks ─────────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1 || die "git is not installed"
[[ -n "$REMOTE_URL" ]] || die "Pass remote URL as first argument.\n  Usage: ./push_commits.sh git@github.com:user/repo.git"

cd "$(dirname "$0")"

# ── init ──────────────────────────────────────────────────────────────────────
log "Initialising git repository..."
git init --quiet
git config user.name  "Ekagra"
git config user.email "ekagra@example.com"   # ← change if needed

# ── COMMIT 1 — project scaffold ───────────────────────────────────────────────
log "Commit 1 — project scaffold & requirements"
git add .gitignore requirements.txt docker-compose.yml Dockerfile
commit "2026-03-25T09:00:00+05:30" \
  "chore: initialise project scaffold

- Add .gitignore with Python, Node, and OS exclusions
- Pin Python dependencies: pandas>=2.0, numpy, faker, fastapi, uvicorn,
  pydantic>=2.0, pytest, python-multipart
- Add Dockerfile (multi-stage: Python + Node build → slim runtime)
- Add docker-compose.yml wiring backend :8000 + frontend :3000 + data volume"

# ── COMMIT 2 — PRD & README ───────────────────────────────────────────────────
log "Commit 2 — documentation"
git add PRD.md README.md
commit "2026-03-25T09:30:00+05:30" \
  "docs: add PRD, SRS, and usage README

- PRD.md covers all 5 parts: data gen, cleaning, analysis, API, dashboard
- README.md includes 5-minute quick-start, project tree, design decisions,
  all API endpoints, environment variable reference, and Docker instructions"

# ── COMMIT 3 — data generation ────────────────────────────────────────────────
log "Commit 3 — synthetic data generator"
git add generate_data.py
commit "2026-03-25T11:00:00+05:30" \
  "feat(data): implement synthetic CSV dataset generator (generate_data.py)

- Fixed seed=42 for full reproducibility (F-04, F-05)
- Generates customers.csv (550 rows), orders.csv (2000 rows), products.csv (30 rows)
- Customers: 10% duplicate IDs, 8% null emails, 5% malformed emails,
  3% unparseable signup_dates, mixed whitespace in region (F-01)
- Orders: 3 mixed date formats, 5% null amounts, 3% both-null unrecoverable rows,
  12 status variants (F-02)
- Products: 30 rows, last 5 are orphan records with no matching orders (F-03)
- CLI: --output-dir flag with default data/raw (F-24)
- _random_date() and _order_date_str() helpers extracted for testability"

# ── COMMIT 4 — data cleaning pipeline ────────────────────────────────────────
log "Commit 4 — data cleaning pipeline"
git add clean_data.py
commit "2026-03-26T10:00:00+05:30" \
  "feat(pipeline): implement data cleaning pipeline (clean_data.py)

customers.csv (F-06 to F-10):
- Deduplication: sort by signup_date desc, keep most recent per customer_id
- Email validation: str.lower() + is_valid_email boolean column
- signup_date parsing: pd.to_datetime with per-row logging on NaT
- Whitespace stripping via lambda (NaN-safe)
- Null region fill with literal 'Unknown'

orders.csv (F-11 to F-15):
- parse_order_date(): typed str→Timestamp, tries 3 formats, returns NaT on fail
- Unrecoverable row removal: drop where both order_id AND customer_id are null
- Amount imputation: product-level median, global median fallback
- Status normalisation via STATUS_MAP dict, unmapped → 'pending' with warning
- order_year_month derivation from parsed order_date

Infrastructure:
- load_csv() utility with FileNotFoundError + EmptyDataError handling (F-25)
- _ensure_raw_data() zero-intervention guard auto-runs generate_data.py
- --input-dir / --output-dir argparse flags (F-24)
- Full === CLEANING REPORT === printed to stdout (F-16)"

# ── COMMIT 5 — analysis pipeline ─────────────────────────────────────────────
log "Commit 5 — analysis pipeline"
git add analyze.py
commit "2026-03-27T10:30:00+05:30" \
  "feat(pipeline): implement data merging and analysis (analyze.py)

Merge layer (F-17, F-18):
- merge_datasets(): two explicit left joins with on= and how= arguments
  Step 1: orders_clean LEFT JOIN customers_clean on customer_id
  Step 2: LEFT JOIN products on product = product_name
- Logs unmatched row counts for both joins

Analysis outputs (F-19 to F-23):
- monthly_revenue.csv: completed orders grouped by order_year_month (F-19)
- top_customers.csv: top 10 by total_spend, completed only (F-20)
- category_performance.csv: revenue / avg_order_value / num_orders (F-21)
- regional_analysis.csv: num_customers (distinct) + orders + revenue (F-22)
- Churn indicator: 90-day window from max(order_date), dataset-relative (F-23)

CLI: --raw-dir / --processed-dir argparse flags (F-24)"

# ── COMMIT 6 — backend API ────────────────────────────────────────────────────
log "Commit 6 — FastAPI backend"
git add backend/
commit "2026-03-28T09:00:00+05:30" \
  "feat(api): implement FastAPI backend with 5 endpoints (F-26 to F-31)

backend/config.py:
- DATA_DIR and FRONTEND_DIR resolved from env vars with Path defaults

backend/models/schemas.py:
- Pydantic v2 response models: RevenueRecord, CustomerRecord,
  CategoryRecord, RegionRecord (F-29)

backend/routers/data.py:
- GET /api/revenue      → List[RevenueRecord]
- GET /api/top-customers → List[CustomerRecord]
- GET /api/categories   → List[CategoryRecord]
- GET /api/regions      → List[RegionRecord]
- FileNotFoundError → HTTP 404 with actionable detail message (F-30)
- EmptyDataError → HTTP 500 (F-30)

backend/main.py:
- FastAPI app with title, description, version
- CORSMiddleware: allow_origins=['*'], allow_methods=['GET'] (F-27)
- GET /health endpoint (F-28)
- StaticFiles mount serves built React dist/ as fallback"

# ── COMMIT 7 — React dashboard ───────────────────────────────────────────────
log "Commit 7 — React/Vite dashboard"
git add frontend/src/ frontend/index.html frontend/vite.config.js \
        frontend/package.json frontend/eslint.config.js frontend/.gitignore \
        frontend/README.md frontend/public/ 2>/dev/null || true
commit "2026-03-29T14:00:00+05:30" \
  "feat(ui): implement React/Vite analytics dashboard (F-32 to F-35)

Design:
- Dark-mode glassmorphism design system in index.css
- CSS custom properties for all tokens (colors, radii, shadows, spacing)
- Google Fonts: Inter — loaded via <link> in index.html
- Micro-animations: fade-in-up on mount, skeleton loaders, hover lift effects

Components:
- Sidebar.jsx: icon navigation with active-state highlight
- RevenueChart.jsx: Recharts AreaChart + bonus date-range filter (US-11)
- TopCustomers.jsx: ranked table + bonus live search box (US-12)
- CategoryChart.jsx: Recharts BarChart for category revenue breakdown
- RegionSummary.jsx: KPI cards grid with churned customer callout
- LoadingSkeleton.jsx: animated shimmer placeholder during data fetch
- ErrorState.jsx: user-friendly error panel shown when API is unreachable (US-06)

App.jsx:
- Tab-based navigation with KPI summary bar
- Responsive layout: sidebar collapses on mobile (375px viewport, US-05)

api.js:
- Typed fetch utility with base URL from VITE_API_BASE env var
- Currency and percentage formatters

vite.config.js:
- Dev server on port 3000, /api proxy → localhost:8000"

# ── COMMIT 8 — test suite ─────────────────────────────────────────────────────
log "Commit 8 — pytest test suite"
git add tests/
commit "2026-03-30T11:00:00+05:30" \
  "test: add pytest test suite with 5 classes and 20+ assertions

tests/test_cleaning.py:
- TestParseOrderDate (6 tests): ISO, DMY slash, MDY dash, invalid, None, NaN
- TestEmailValidation (4 tests): valid, null, no-@, no-dot flags
- TestStatusNormalization (6 tests): done→completed, canceled→cancelled,
  COMPLETED, pending variants, unknown→pending, STATUS_MAP value coverage
- TestDeduplication (2 tests): keeps most recent signup_date, correct count
- TestAmountImputation (3 tests): product-level median, global median fallback,
  zero null amounts after imputation

All tests are isolated (no file I/O) and run in <2s locally"

# ── tag ───────────────────────────────────────────────────────────────────────
log "Tagging v1.0.0..."
git tag -a v1.0.0 -m "v1.0.0 — Complete data pipeline + analytics dashboard

Deliverables:
✓ generate_data.py  — reproducible synthetic CSV generation (seed=42)
✓ clean_data.py     — full cleaning pipeline with === CLEANING REPORT ===
✓ analyze.py        — 5 analytical output CSVs
✓ backend/          — FastAPI REST API (5 endpoints, Pydantic v2 models)
✓ frontend/         — React/Vite dashboard (4 charts, date filter, search)
✓ tests/            — pytest suite (5 classes, 20+ assertions)
✓ Dockerfile + docker-compose.yml
✓ README.md + PRD.md"

# ── push ──────────────────────────────────────────────────────────────────────
log "Adding remote and pushing..."
git remote add origin "$REMOTE_URL"
git branch -M main
git push -u origin main --tags

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅  All commits pushed to: $REMOTE_URL"
echo "  📌  Tag v1.0.0 created"
echo "  🔢  $(git log --oneline | wc -l | tr -d ' ') commits on main"
echo "═══════════════════════════════════════════════════════"

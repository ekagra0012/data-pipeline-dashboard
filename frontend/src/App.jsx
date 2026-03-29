// frontend/src/App.jsx
import { useState, useEffect, useCallback } from 'react'
import { fetchData, fmt } from './api'
import Sidebar from './components/Sidebar'
import RevenueChart from './components/RevenueChart'
import TopCustomers from './components/TopCustomers'
import CategoryChart from './components/CategoryChart'
import RegionSummary from './components/RegionSummary'
import { CardSkeleton } from './components/LoadingSkeleton'

// ── KPI summary cards ─────────────────────────────────────────────────────────
function KpiCards({ revenue, customers, categories, regions }) {
  const totalRevenue = revenue?.reduce((s, r) => s + r.total_revenue, 0) ?? null
  const totalOrders = categories?.reduce((s, c) => s + c.num_orders, 0) ?? null
  const totalCustomers = regions?.reduce((s, r) => s + r.num_customers, 0) ?? null
  const churnedCount = customers?.filter((c) => c.churned).length ?? null

  const cards = [
    { icon: '💰', label: 'Total Revenue', value: fmt.currency(totalRevenue), sub: 'Completed orders', accent: true },
    { icon: '📋', label: 'Total Orders', value: fmt.number(totalOrders), sub: 'All completed' },
    { icon: '👥', label: 'Total Customers', value: fmt.number(totalCustomers), sub: 'Across all regions' },
    { icon: '⚠️', label: 'Churned (Top 10)', value: churnedCount ?? '—', sub: 'No order in 90 days' },
  ]

  const loading = totalRevenue === null && totalOrders === null

  if (loading) return <CardSkeleton />

  return (
    <div className="cards-grid fade-in">
      {cards.map((c) => (
        <div key={c.label} className={`card${c.accent ? ' card-accent' : ''}`}>
          <div className="card-icon">{c.icon}</div>
          <div className="card-label">{c.label}</div>
          <div className="card-value">{c.value}</div>
          <div className="card-sub">{c.sub}</div>
        </div>
      ))}
    </div>
  )
}

// ── Page header ───────────────────────────────────────────────────────────────
const PAGE_META = {
  overview:   { title: 'Overview',            sub: 'Summary of all key business metrics' },
  revenue:    { title: 'Revenue Trend',        sub: 'Monthly completed order revenue over time' },
  customers:  { title: 'Top Customers',        sub: 'Highest-spending customers with churn indicators' },
  categories: { title: 'Category Performance', sub: 'Revenue and order metrics by product category' },
  regions:    { title: 'Regional Analysis',    sub: 'Customer distribution and revenue by region' },
}

// ── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const [state, setState] = useState({
    revenue:    { data: null, loading: true, error: null },
    customers:  { data: null, loading: true, error: null },
    categories: { data: null, loading: true, error: null },
    regions:    { data: null, loading: true, error: null },
  })

  const load = useCallback(async (key, endpoint) => {
    setState((s) => ({ ...s, [key]: { ...s[key], loading: true, error: null } }))
    try {
      const data = await fetchData(endpoint)
      setState((s) => ({ ...s, [key]: { data, loading: false, error: null } }))
    } catch (err) {
      setState((s) => ({ ...s, [key]: { data: null, loading: false, error: err.message } }))
    }
  }, [])

  useEffect(() => {
    load('revenue',    '/api/revenue')
    load('customers',  '/api/top-customers')
    load('categories', '/api/categories')
    load('regions',    '/api/regions')
  }, [load])

  const { revenue, customers, categories, regions } = state
  const meta = PAGE_META[activeTab]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            <KpiCards
              revenue={revenue.data}
              customers={customers.data}
              categories={categories.data}
              regions={regions.data}
            />
            <div className="section-title">Revenue Trend</div>
            <RevenueChart {...revenue} onRetry={() => load('revenue', '/api/revenue')} />
            <div className="section-title">Category Breakdown</div>
            <CategoryChart {...categories} onRetry={() => load('categories', '/api/categories')} />
          </>
        )
      case 'revenue':
        return <RevenueChart {...revenue} onRetry={() => load('revenue', '/api/revenue')} />
      case 'customers':
        return <TopCustomers {...customers} onRetry={() => load('customers', '/api/top-customers')} />
      case 'categories':
        return <CategoryChart {...categories} onRetry={() => load('categories', '/api/categories')} />
      case 'regions':
        return <RegionSummary {...regions} onRetry={() => load('regions', '/api/regions')} />
      default:
        return null
    }
  }

  return (
    <div className="layout">
      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          style={{ position: 'fixed', inset: 0, zIndex: 99, background: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        open={sidebarOpen}
        setOpen={setSidebarOpen}
      />

      <div className="main-area">
        {/* Page header */}
        <div className="page-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              className="hamburger"
              onClick={() => setSidebarOpen((o) => !o)}
              aria-label="Toggle menu"
            >
              ☰
            </button>
            <div>
              <h1 className="page-title">{meta.title}</h1>
              <div className="page-sub">{meta.sub}</div>
            </div>
          </div>
          <div className="header-badge">
            <span className="dot" />
            Live Data
          </div>
        </div>

        {/* Content */}
        <div className="page-content">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

// frontend/src/App.jsx
import { useState } from 'react'
import useAPIData from './hooks/useAPIData'
import Sidebar from './components/Layout/Sidebar'
import TopBar from './components/Layout/TopBar'
import KPICard from './components/ui/KPICard'
import RevenueChart from './components/charts/RevenueChart'
import CustomersTable from './components/tables/CustomersTable'
import CategoryChart from './components/charts/CategoryChart'
import RegionCard from './components/cards/RegionCard'
import Dashboard from './pages/Dashboard'

const PAGE_META = {
  overview:   { title: 'Overview',            sub: 'Summary of all key business metrics' },
  revenue:    { title: 'Revenue Trend',        sub: 'Monthly completed order revenue over time' },
  customers:  { title: 'Top Customers',        sub: 'Highest-spending customers with churn indicators' },
  categories: { title: 'Category Performance', sub: 'Revenue and order metrics by product category' },
  regions:    { title: 'Regional Analysis',    sub: 'Customer distribution and revenue by region' },
}

export default function App() {
  const [activeTab, setActiveTab] = useState('overview')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { state, load } = useAPIData()

  const { revenue, customers, categories, regions } = state
  const meta = PAGE_META[activeTab]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <Dashboard
            revenue={revenue}
            customers={customers}
            categories={categories}
            regions={regions}
            load={load}
          />
        )
      case 'revenue':
        return (
          <RevenueChart
            {...revenue}
            onRetry={() => load('revenue', '/api/revenue')}
          />
        )
      case 'customers':
        return (
          <CustomersTable
            {...customers}
            onRetry={() => load('customers', '/api/top-customers')}
          />
        )
      case 'categories':
        return (
          <CategoryChart
            {...categories}
            onRetry={() => load('categories', '/api/categories')}
          />
        )
      case 'regions':
        return (
          <RegionCard
            {...regions}
            onRetry={() => load('regions', '/api/regions')}
          />
        )
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
        <TopBar
          title={meta.title}
          subtitle={meta.sub}
          onMenuToggle={() => setSidebarOpen((o) => !o)}
        />

        {/* KPI cards always visible on overview */}
        {activeTab === 'overview' && (
          <KPICard
            revenue={revenue.data}
            customers={customers.data}
            categories={categories.data}
            regions={regions.data}
          />
        )}

        {/* Content */}
        <div className="page-content">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

// frontend/src/components/ui/KPICard.jsx — KPI summary cards strip
import { CardSkeleton } from './SkeletonLoader'
import { fmt } from '../../utils/formatters'

export default function KPICard({ revenue, customers, categories, regions }) {
  const totalRevenue =
    revenue?.reduce((s, r) => s + r.total_revenue, 0) ?? null
  const totalOrders =
    categories?.reduce((s, c) => s + c.num_orders, 0) ?? null
  const totalCustomers =
    regions?.reduce((s, r) => s + r.num_customers, 0) ?? null
  const churnedCount =
    customers?.filter((c) => c.churned).length ?? null

  const cards = [
    {
      icon: '💰',
      label: 'Total Revenue',
      value: fmt.currency(totalRevenue),
      sub: 'Completed orders',
      accent: true,
    },
    {
      icon: '📋',
      label: 'Total Orders',
      value: fmt.number(totalOrders),
      sub: 'All completed',
    },
    {
      icon: '👥',
      label: 'Total Customers',
      value: fmt.number(totalCustomers),
      sub: 'Across all regions',
    },
    {
      icon: '⚠️',
      label: 'Churned (Top 10)',
      value: churnedCount ?? '—',
      sub: 'No order in 90 days',
    },
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

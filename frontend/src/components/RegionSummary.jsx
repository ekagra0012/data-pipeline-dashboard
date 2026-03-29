// frontend/src/components/RegionSummary.jsx
import { ChartSkeleton } from './LoadingSkeleton'
import ErrorState from './ErrorState'
import { fmt } from '../api'

const REGION_ICONS = {
  North: '🧭', South: '🌊', East: '🌅', West: '🌄', Central: '🏙️', Unknown: '❓',
}

export default function RegionSummary({ data, loading, error, onRetry }) {
  if (loading) return <ChartSkeleton />
  if (error) return <ErrorState message={error} onRetry={onRetry} />

  const sorted = data ? [...data].sort((a, b) => b.total_revenue - a.total_revenue) : []

  return (
    <div className="fade-in">
      <div className="region-grid">
        {sorted.map((region) => (
          <div key={region.region} className="region-card">
            <div className="region-name">
              <span>{REGION_ICONS[region.region] ?? '📍'}</span>
              {region.region}
            </div>

            <div className="region-stat">
              <span className="region-stat-label">Customers</span>
              <span className="region-stat-value">{fmt.number(region.num_customers)}</span>
            </div>
            <div className="region-stat">
              <span className="region-stat-label">Orders</span>
              <span className="region-stat-value">{fmt.number(region.num_orders)}</span>
            </div>
            <div className="region-stat">
              <span className="region-stat-label">Total Revenue</span>
              <span className="region-stat-value" style={{ color: '#7c6ef4' }}>
                {fmt.currency(region.total_revenue)}
              </span>
            </div>
            <div className="region-stat">
              <span className="region-stat-label">Avg / Customer</span>
              <span className="region-stat-value">{fmt.currency(region.avg_revenue_per_customer)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// frontend/src/components/charts/CategoryChart.jsx
import { useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts'
import { ChartSkeleton } from '../ui/SkeletonLoader'
import ErrorBanner from '../ui/ErrorBanner'
import { fmt } from '../../utils/formatters'

const COLORS = ['#7c6ef4', '#a78bfa', '#818cf8', '#6366f1', '#4f46e5', '#34d399', '#fbbf24']

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div className="custom-tooltip">
      <div className="tt-label">{d.category}</div>
      <div className="tt-value">{fmt.currency(d.total_revenue)}</div>
      <div style={{ color: '#6b7280', fontSize: 11, marginTop: 4 }}>
        {fmt.number(d.num_orders)} orders · AOV {fmt.currency(d.avg_order_value)}
      </div>
    </div>
  )
}

export default function CategoryChart({ data, loading, error, onRetry }) {
  const sorted = useMemo(
    () => (data ? [...data].sort((a, b) => b.total_revenue - a.total_revenue) : []),
    [data]
  )

  if (loading) return <ChartSkeleton />
  if (error) return <ErrorBanner message={error} onRetry={onRetry} />

  return (
    <div className="chart-card fade-in">
      <div className="chart-header">
        <div>
          <div className="chart-title">Category Performance</div>
          <div className="chart-subtitle">Revenue by product category (completed orders)</div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        <BarChart
          data={sorted}
          layout="vertical"
          margin={{ top: 8, right: 24, left: 80, bottom: 8 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="rgba(255,255,255,0.05)"
            horizontal={false}
          />
          <XAxis
            type="number"
            tickFormatter={(v) => '$' + (v / 1000).toFixed(0) + 'k'}
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="category"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={76}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="total_revenue" radius={[0, 4, 4, 0]}>
            {sorted.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Mini stats table */}
      <div className="table-wrap" style={{ marginTop: 16 }}>
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Revenue</th>
              <th>Avg Order</th>
              <th>Orders</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr key={row.category}>
                <td><span className="customer-name">{row.category}</span></td>
                <td>{fmt.currency(row.total_revenue)}</td>
                <td>{fmt.currency(row.avg_order_value)}</td>
                <td>{fmt.number(row.num_orders)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

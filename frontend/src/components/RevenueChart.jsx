// frontend/src/components/RevenueChart.jsx
import { useState, useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts'
import { ChartSkeleton } from './LoadingSkeleton'
import ErrorState from './ErrorState'
import { fmt } from '../api'

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="custom-tooltip">
      <div className="tt-label">{label}</div>
      <div className="tt-value">{fmt.currency(payload[0]?.value)}</div>
    </div>
  )
}

export default function RevenueChart({ data, loading, error, onRetry }) {
  const [startMonth, setStartMonth] = useState('')
  const [endMonth, setEndMonth] = useState('')

  const filtered = useMemo(() => {
    if (!data) return []
    return data.filter((row) => {
      if (startMonth && row.order_year_month < startMonth) return false
      if (endMonth && row.order_year_month > endMonth) return false
      return true
    })
  }, [data, startMonth, endMonth])

  const totalRevenue = useMemo(
    () => filtered.reduce((sum, r) => sum + r.total_revenue, 0),
    [filtered]
  )

  if (loading) return <ChartSkeleton />
  if (error) return <ErrorState message={error} onRetry={onRetry} />

  return (
    <div className="chart-card fade-in">
      <div className="chart-header">
        <div>
          <div className="chart-title">Monthly Revenue Trend</div>
          <div className="chart-subtitle">
            {filtered.length} months · Total: {fmt.currency(totalRevenue)}
          </div>
        </div>

        {/* Bonus: date-range filter */}
        <div className="date-filter">
          <label htmlFor="rev-start">From</label>
          <input
            id="rev-start"
            type="month"
            value={startMonth}
            onChange={(e) => setStartMonth(e.target.value)}
          />
          <label htmlFor="rev-end">To</label>
          <input
            id="rev-end"
            type="month"
            value={endMonth}
            onChange={(e) => setEndMonth(e.target.value)}
          />
          {(startMonth || endMonth) && (
            <button
              className="btn-reset"
              onClick={() => { setStartMonth(''); setEndMonth('') }}
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">No data for selected range.</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={filtered} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="order_year_month"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              tickFormatter={(v) => '$' + (v / 1000).toFixed(0) + 'k'}
              tick={{ fill: '#6b7280', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={54}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="total_revenue"
              stroke="#7c6ef4"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#7c6ef4', strokeWidth: 0 }}
              activeDot={{ r: 5, fill: '#9d93f8', strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

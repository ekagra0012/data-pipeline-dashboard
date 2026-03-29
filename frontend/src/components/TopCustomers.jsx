// frontend/src/components/TopCustomers.jsx
import { useState, useMemo } from 'react'
import { TableSkeleton } from './LoadingSkeleton'
import ErrorState from './ErrorState'
import { fmt } from '../api'

export default function TopCustomers({ data, loading, error, onRetry }) {
  const [search, setSearch] = useState('')
  const [sortDir, setSortDir] = useState('desc')

  const filtered = useMemo(() => {
    if (!data) return []
    let rows = data.filter((r) =>
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.region.toLowerCase().includes(search.toLowerCase())
    )
    rows = [...rows].sort((a, b) =>
      sortDir === 'desc' ? b.total_spend - a.total_spend : a.total_spend - b.total_spend
    )
    return rows
  }, [data, search, sortDir])

  if (loading) {
    return (
      <div className="chart-card">
        <div className="chart-header">
          <div className="chart-title">Top Customers</div>
        </div>
        <TableSkeleton />
      </div>
    )
  }

  if (error) return <ErrorState message={error} onRetry={onRetry} />

  const churnedCount = data?.filter((r) => r.churned).length ?? 0

  return (
    <div className="chart-card fade-in">
      <div className="chart-header">
        <div>
          <div className="chart-title">Top 10 Customers</div>
          <div className="chart-subtitle">
            By total spend (completed orders) · {churnedCount} churned
          </div>
        </div>

        {/* Bonus: search box */}
        <div className="search-wrap">
          <span className="search-icon">⌕</span>
          <input
            id="customer-search"
            className="search-input"
            type="text"
            placeholder="Search by name or region…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="table-wrap">
        {filtered.length === 0 ? (
          <div className="empty-state">No customers match your search.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Region</th>
                <th
                  onClick={() => setSortDir((d) => (d === 'desc' ? 'asc' : 'desc'))}
                  title="Click to toggle sort direction"
                >
                  Total Spend {sortDir === 'desc' ? '↓' : '↑'}
                </th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row, i) => (
                <tr key={row.customer_id}>
                  <td className="rank-cell">{i + 1}</td>
                  <td>
                    <span className="customer-name">{row.name}</span>
                    <div style={{ fontSize: 11, color: '#6b7280' }}>{row.customer_id}</div>
                  </td>
                  <td>
                    <span className="badge badge-region">{row.region}</span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{fmt.currency(row.total_spend)}</td>
                  <td>
                    {row.churned ? (
                      <span className="badge badge-churned">⚠ Churned</span>
                    ) : (
                      <span className="badge badge-active">✓ Active</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

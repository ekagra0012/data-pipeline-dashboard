// frontend/src/components/ui/SkeletonLoader.jsx
export function CardSkeleton() {
  return (
    <div className="cards-grid">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="skeleton skeleton-card" />
      ))}
    </div>
  )
}

export function ChartSkeleton() {
  return <div className="skeleton skeleton-chart" style={{ marginBottom: 24 }} />
}

export function TableSkeleton() {
  return (
    <div>
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
        <div key={i} className="skeleton skeleton-row" />
      ))}
    </div>
  )
}

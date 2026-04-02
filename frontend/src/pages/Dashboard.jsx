// frontend/src/pages/Dashboard.jsx — Overview page assembling all four sections
import RevenueChart from '../components/charts/RevenueChart'
import CategoryChart from '../components/charts/CategoryChart'

export default function Dashboard({ revenue, customers, categories, regions, load }) {
  return (
    <>
      <div className="section-title">Revenue Trend</div>
      <RevenueChart
        {...revenue}
        onRetry={() => load('revenue', '/api/revenue')}
      />

      <div className="section-title">Category Breakdown</div>
      <CategoryChart
        {...categories}
        onRetry={() => load('categories', '/api/categories')}
      />
    </>
  )
}

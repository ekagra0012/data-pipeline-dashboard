// frontend/src/components/Layout/TopBar.jsx — Page header with title and live badge
export default function TopBar({ title, subtitle, onMenuToggle }) {
  return (
    <div className="page-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button
          className="hamburger"
          onClick={onMenuToggle}
          aria-label="Toggle menu"
        >
          ☰
        </button>
        <div>
          <h1 className="page-title">{title}</h1>
          <div className="page-sub">{subtitle}</div>
        </div>
      </div>
      <div className="header-badge">
        <span className="dot" />
        Live Data
      </div>
    </div>
  )
}

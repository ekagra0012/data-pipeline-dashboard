// frontend/src/components/Sidebar.jsx
export default function Sidebar({ activeTab, setActiveTab, open, setOpen }) {
  const items = [
    { id: 'overview',    icon: '◈', label: 'Overview'   },
    { id: 'revenue',     icon: '📈', label: 'Revenue'    },
    { id: 'customers',   icon: '👥', label: 'Customers'  },
    { id: 'categories',  icon: '📦', label: 'Categories' },
    { id: 'regions',     icon: '🗺️', label: 'Regions'    },
  ]

  const handleNav = (id) => {
    setActiveTab(id)
    setOpen(false)
  }

  return (
    <aside className={`sidebar${open ? ' open' : ''}`}>
      <div className="sidebar-logo">
        <div className="logo-mark">
          <div className="logo-icon">◈</div>
          <div>
            <div className="logo-text">DataLens</div>
            <div className="logo-sub">Analytics Dashboard</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {items.map(({ id, icon, label }) => (
          <button
            key={id}
            id={`nav-${id}`}
            className={`nav-item${activeTab === id ? ' active' : ''}`}
            onClick={() => handleNav(id)}
          >
            <span className="nav-icon">{icon}</span>
            {label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        Data Pipeline v1.0 · Assignment
      </div>
    </aside>
  )
}

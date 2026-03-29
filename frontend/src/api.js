// frontend/src/api.js — Centralised API utility

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function fetchData(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const fmt = {
  currency: (n) =>
    typeof n === 'number'
      ? '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
      : '—',
  number: (n) => (typeof n === 'number' ? n.toLocaleString('en-US') : '—'),
  pct: (n) => (typeof n === 'number' ? n.toFixed(1) + '%' : '—'),
}

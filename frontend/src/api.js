// frontend/src/api.js — Centralised API fetch utility
// Note: formatters have moved to ./utils/formatters.js

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function fetchData(endpoint) {
  const res = await fetch(`${API_BASE}${endpoint}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

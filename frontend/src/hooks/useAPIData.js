// frontend/src/hooks/useAPIData.js — Custom hook for all API data fetching
import { useState, useEffect, useCallback } from 'react'
import { fetchData } from '../api'

export default function useAPIData() {
  const [state, setState] = useState({
    revenue:    { data: null, loading: true, error: null },
    customers:  { data: null, loading: true, error: null },
    categories: { data: null, loading: true, error: null },
    regions:    { data: null, loading: true, error: null },
  })

  const load = useCallback(async (key, endpoint) => {
    setState((s) => ({ ...s, [key]: { ...s[key], loading: true, error: null } }))
    try {
      const data = await fetchData(endpoint)
      setState((s) => ({ ...s, [key]: { data, loading: false, error: null } }))
    } catch (err) {
      setState((s) => ({
        ...s,
        [key]: { data: null, loading: false, error: err.message },
      }))
    }
  }, [])

  useEffect(() => {
    load('revenue',    '/api/revenue')
    load('customers',  '/api/top-customers')
    load('categories', '/api/categories')
    load('regions',    '/api/regions')
  }, [load])

  return { state, load }
}

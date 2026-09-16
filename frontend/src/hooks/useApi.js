import { useState, useCallback } from 'react'
import api from '../services/api'

/**
 * Generic hook for API calls with loading/error state management.
 * Usage:
 *   const { data, loading, error, execute } = useApi()
 *   await execute(() => api.get('/resumes'))
 */
export function useApi() {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]   = useState(null)

  const execute = useCallback(async (apiFn) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiFn()
      setData(res.data)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Request failed'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setData(null); setError(null); setLoading(false)
  }, [])

  return { data, loading, error, execute, reset }
}

export default useApi

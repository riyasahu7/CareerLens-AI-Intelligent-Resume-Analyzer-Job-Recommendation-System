import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('cl_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      api.get('/auth/me')
        .then(r => setUser(r.data.user))
        .catch(() => { localStorage.removeItem('cl_token'); delete api.defaults.headers.common['Authorization'] })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    const r = await api.post('/auth/login', { email, password })
    const { token, user } = r.data
    localStorage.setItem('cl_token', token)
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    setUser(user)
    return user
  }, [])

  const register = useCallback(async (email, password, full_name) => {
    const r = await api.post('/auth/register', { email, password, full_name })
    const { token, user } = r.data
    localStorage.setItem('cl_token', token)
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    setUser(user)
    return user
  }, [])

  const logout = useCallback(async () => {
    try { await api.post('/auth/logout') } catch {}
    localStorage.removeItem('cl_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const r = await api.get('/auth/me')
    setUser(r.data.user)
    return r.data.user
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}

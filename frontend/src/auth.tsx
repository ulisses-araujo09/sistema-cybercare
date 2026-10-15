import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { post, setToken } from './api'
import type { Role } from './api'
type Auth = { role: Role | null; login: (email: string, password: string) => Promise<Role>; logout: () => Promise<void>; expired: boolean }
const Context = createContext<Auth>(null!)
export function AuthProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role | null>(null)
  const [expired, setExpired] = useState(false)
  useEffect(() => {
    const expire = () => { setRole(null); setToken(null); setExpired(true) }
    window.addEventListener('session-expired', expire)
    return () => window.removeEventListener('session-expired', expire)
  }, [])
  async function login(email: string, password: string) {
    const result = await post<{ access_token: string; role: Role }>('/auth/login', { email, password })
    setToken(result.access_token); setRole(result.role); setExpired(false)
    return result.role
  }
  async function logout() {
    try { await post('/auth/logout', {}) } finally { setToken(null); setRole(null) }
  }
  return <Context.Provider value={{ role, login, logout, expired }}>{children}</Context.Provider>
}
export const useAuth = () => useContext(Context)
export function Protected({ role, children }: { role: Role; children: ReactNode }) {
  const auth = useAuth()
  if (!auth.role) return <Navigate to="/login" replace/>
  if (auth.role !== role) return <Navigate to={auth.role === 'gestao' ? '/gestao' : '/socioemocional'} replace/>
  return children
}

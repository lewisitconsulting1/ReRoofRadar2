import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { api } from '@/lib/api'
import type { User, LoginCredentials, RegisterCredentials, AuthResponse } from '@/types/auth'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')
    if (storedUser && token) {
      setUser(JSON.parse(storedUser) as User)
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (credentials: LoginCredentials): Promise<void> => {
    const response = await api.post<AuthResponse>('/api/auth/login', credentials)
    localStorage.setItem('access_token', response.data.access_token)
    const meResponse = await api.get<User>('/api/auth/me')
    setUser(meResponse.data)
    localStorage.setItem('user', JSON.stringify(meResponse.data))
  }, [])

  const register = useCallback(async (credentials: RegisterCredentials): Promise<void> => {
    await api.post<AuthResponse>('/api/auth/register', credentials)
    await login({ email: credentials.email, password: credentials.password })
  }, [login])

  const logout = useCallback((): void => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

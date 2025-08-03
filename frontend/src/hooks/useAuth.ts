import { useCallback } from 'react'
import { useAuth as useAuthStore } from '@/store'
import { apiClient } from '@/lib/api/client'
import { API_ENDPOINTS } from '@/lib/api/endpoints'
import type { User } from '@/store/slices/authSlice'

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  name: string
  email: string
  password: string
}

export function useAuth() {
  const auth = useAuthStore()

  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      auth.setLoading(true)
      auth.clearError()

      const response = await apiClient.post<{
        user: User
        token: string
        refreshToken?: string
      }>(API_ENDPOINTS.AUTH.LOGIN, credentials)

      if (response.success) {
        auth.login(response.data.user, response.data.token, response.data.refreshToken)
        return { success: true }
      } else {
        throw new Error(response.error || 'Login failed')
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed'
      auth.setError(message)
      return { success: false, error: message }
    } finally {
      auth.setLoading(false)
    }
  }, [auth])

  const register = useCallback(async (data: RegisterData) => {
    try {
      auth.setLoading(true)
      auth.clearError()

      const response = await apiClient.post<{
        user: User
        token: string
        refreshToken?: string
      }>(API_ENDPOINTS.AUTH.REGISTER, data)

      if (response.success) {
        auth.login(response.data.user, response.data.token, response.data.refreshToken)
        return { success: true }
      } else {
        throw new Error(response.error || 'Registration failed')
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed'
      auth.setError(message)
      return { success: false, error: message }
    } finally {
      auth.setLoading(false)
    }
  }, [auth])

  const logout = useCallback(async () => {
    try {
      // Optional: Call logout endpoint to invalidate token on server
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT)
    } catch (error) {
      // Continue with logout even if server call fails
      console.warn('Failed to logout on server:', error)
    } finally {
      auth.logout()
    }
  }, [auth])

  const refreshToken = useCallback(async () => {
    // Implementation for token refresh logic
    // This would typically be called automatically by an API interceptor
  }, [])

  return {
    ...auth,
    login,
    register,
    logout,
    refreshToken,
  }
}

export default useAuth
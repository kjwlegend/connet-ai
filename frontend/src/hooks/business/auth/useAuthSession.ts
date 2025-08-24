/**
 * 会话管理业务逻辑 Hook
 * 处理用户会话管理相关的所有业务逻辑
 */

import { useCallback, useEffect } from 'react'
import { AuthService } from '@/services/api'
import { useAuth, useAppStore } from '@/store/index'
import type { User } from '@/store/slices/auth/authSlice'

interface UseAuthSessionReturn {
  // State
  isInitializing: boolean
  isAuthenticated: boolean
  user: User | null
  sessionValid: boolean
  
  // Actions
  initializeAuth: () => Promise<void>
  validateToken: () => Promise<boolean>
  refreshToken: () => Promise<boolean>
  getCurrentUser: () => Promise<User | null>
  logout: () => Promise<void>
  extendSession: () => void
  
  // Utils
  checkSessionTimeout: () => boolean
}

export const useAuthSession = (): UseAuthSessionReturn => {
  const {
    auth,
    ui,
    login,
    logout: logoutAction,
    setInitializing,
    setError,
    extendSession,
    checkSessionTimeout,
    resetSession,
    setUser,
    setToken,
    setRefreshToken,
  } = useAuth()

  const initializeAuth = useCallback(async (): Promise<void> => {
    setInitializing(true)
    setError(null)

    try {
      // 如果store中已经有认证信息，验证其有效性
      if (auth.token && auth.user) {
        try {
          // 验证当前token是否仍然有效
          const result = await AuthService.verifyToken({ token: auth.token })
          
          if (result.valid) {
            // Token有效，恢复会话时间
            extendSession()
            console.log('Session restored from persisted store')
          } else {
            // Token无效，尝试使用refresh token刷新
            if (auth.refreshToken) {
              const refreshResult = await AuthService.refreshToken({ refresh_token: auth.refreshToken })
              
              // 更新token
              setToken(refreshResult.access_token)
              if (refreshResult.refresh_token) {
                setRefreshToken(refreshResult.refresh_token)
              }
              
              console.log('Token refreshed successfully')
            } else {
              throw new Error('No valid token or refresh token')
            }
          }
        } catch (error) {
          console.warn('Failed to restore session:', error)
          // 清除无效状态
          resetSession()
        }
      } else {
        // 没有存储的认证信息，保持未认证状态
        console.log('No stored authentication found')
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      setError(error instanceof Error ? error.message : 'Auth initialization failed')
      resetSession()
    } finally {
      setInitializing(false)
    }
  }, [auth.token, auth.user, auth.refreshToken, setInitializing, setError, resetSession, setToken, setRefreshToken, extendSession])

  const validateToken = useCallback(async (): Promise<boolean> => {
    try {
      if (!auth.token) {
        return false
      }
      
      const result = await AuthService.verifyToken({ token: auth.token })
      return result.valid
    } catch (error) {
      console.error('Token validation failed:', error)
      return false
    }
  }, [auth.token])

  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      if (!auth.refreshToken) {
        return false
      }
      
      const result = await AuthService.refreshToken({ refresh_token: auth.refreshToken })
      
      // 更新store中的token（会自动持久化）
      setToken(result.access_token)
      if (result.refresh_token) {
        setRefreshToken(result.refresh_token)
      }
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
  }, [auth.refreshToken, setToken, setRefreshToken])

  const getCurrentUser = useCallback(async (): Promise<User | null> => {
    try {
      if (!auth.token) {
        return null
      }
      
      const result = await AuthService.getCurrentUser()
      
      // 更新store中的用户信息（会自动持久化）
      setUser(result)
      
      return result
    } catch (error) {
      console.error('Failed to get current user:', error)
      return null
    }
  }, [auth.token, setUser])

  const logout = useCallback(async (): Promise<void> => {
    try {
      // 如果有token，尝试调用API登出
      if (auth.token) {
        await AuthService.logout()
      }
      
      // 清除store状态（会自动清除持久化数据）
      logoutAction()
    } catch (error) {
      console.error('Logout failed:', error)
      // 即使API调用失败，也要清除本地状态
      logoutAction()
    }
  }, [auth.token, logoutAction])

  // 自动会话管理
  useEffect(() => {
    if (!auth.isAuthenticated) return

    // 设置会话检查定时器（每5分钟检查一次）
    const sessionCheckInterval = setInterval(() => {
      if (checkSessionTimeout()) {
        console.warn('Session timed out, logging out...')
        logout()
      }
    }, 5 * 60 * 1000)

    // 设置活动监听器
    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart']
    const handleActivity = () => {
      extendSession()
    }

    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, { passive: true })
    })

    // 清理函数
    return () => {
      clearInterval(sessionCheckInterval)
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity)
      })
    }
  }, [auth.isAuthenticated, checkSessionTimeout, extendSession, logout])

  // 令牌自动刷新
  useEffect(() => {
    if (!auth.isAuthenticated || !auth.refreshToken) return

    // 在令牌过期前10分钟尝试刷新
    const tokenRefreshInterval = setInterval(async () => {
      const isValid = await validateToken()
      if (!isValid) {
        const refreshed = await refreshToken()
        if (!refreshed) {
          console.warn('Token refresh failed, logging out...')
          await logout()
        }
      }
    }, 50 * 60 * 1000) // 50分钟检查一次

    return () => clearInterval(tokenRefreshInterval)
  }, [auth.isAuthenticated, auth.refreshToken, validateToken, refreshToken, logout])

  return {
    // State
    isInitializing: ui.isInitializing,
    isAuthenticated: auth.isAuthenticated,
    user: auth.user,
    sessionValid: auth.isAuthenticated && !checkSessionTimeout(),
    
    // Actions
    initializeAuth,
    validateToken,
    refreshToken,
    getCurrentUser,
    logout,
    extendSession,
    
    // Utils
    checkSessionTimeout,
  }
}
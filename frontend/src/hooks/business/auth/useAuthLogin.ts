/**
 * 登录业务逻辑 Hook
 * 处理用户登录相关的所有业务逻辑
 */

import { useCallback } from 'react'
import { AuthService } from '@/services/api'
import { useAuth } from '@/store/index'
import type { User } from '@/store/slices/auth/authSlice'

interface UseAuthLoginReturn {
  // State
  isLoading: boolean
  error: string | null
  
  // Actions
  loginWithCredentials: (email: string, password: string, rememberMe?: boolean) => Promise<User | null>
  loginWithOAuth: (provider: 'google' | 'github') => Promise<void>
  clearError: () => void
}

export const useAuthLogin = (): UseAuthLoginReturn => {
  const {
    auth,
    ui,
    error,
    login,
    setLoading,
    setError,
    clearError: clearAuthError
  } = useAuth()

  const clearError = useCallback(() => {
    clearAuthError()
  }, [clearAuthError])

  const loginWithCredentials = useCallback(async (
    email: string, 
    password: string, 
    rememberMe = false
  ): Promise<User | null> => {
    try {
      setLoading(true)
      setError(null)

      // 输入验证
      if (!email.trim()) {
        setError('邮箱不能为空', 'loginWithCredentials')
        return null
      }

      if (!password.trim()) {
        setError('密码不能为空', 'loginWithCredentials')
        return null
      }

      // 调用API
      const response = await AuthService.login({ email: email.trim(), password })

      // 登录成功，更新状态
      login(
        response.user,
        response.access_token,
        rememberMe ? response.refresh_token : undefined
      )

      return response.user
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '登录失败，请重试'
      setError(errorMessage, 'loginWithCredentials')
      return null
    } finally {
      setLoading(false)
    }
  }, [login, setError, setLoading])

  const loginWithOAuth = useCallback(async (provider: 'google' | 'github') => {
    try {
      setLoading(true)
      setError(null)

      // 检查是否在浏览器环境
      if (typeof window === 'undefined') {
        throw new Error('OAuth 登录只能在浏览器中使用')
      }

      // 获取当前页面URL作为回调地址
      const redirectUri = `${window.location.origin}/auth/callback`

      // 直接调用AuthService获取OAuth URL
      const { url } = await AuthService.getOAuthUrl(provider, redirectUri)

      // 跳转到OAuth提供商
      window.location.href = url
    } catch (error) {
      setLoading(false)
      const errorMessage = error instanceof Error 
        ? error.message 
        : `${provider} 登录失败`
      setError(errorMessage, 'loginWithOAuth')
      throw error
    }
  }, [setError, setLoading])

  return {
    // State
    isLoading: ui.isLoading,
    error: error.current,
    
    // Actions
    loginWithCredentials,
    loginWithOAuth,
    clearError,
  }
}
/**
 * OAuth 业务逻辑 Hook
 * 处理 OAuth 认证相关的所有业务逻辑
 */

import { useCallback, useEffect } from 'react'
import { AuthService } from '@/services/api'
import { useAuth } from '@/store/index'
import type { User } from '@/store/slices/auth/authSlice'

interface UseAuthOAuthReturn {
  // State
  isLoading: boolean
  error: string | null
  
  // Actions
  getOAuthUrl: (provider: 'google' | 'github', redirectUri: string) => Promise<{ url: string; state: string } | null>
  handleOAuthCallback: (provider: 'google' | 'github', code: string, state: string, redirectUri: string) => Promise<{ user: User; isNewUser: boolean } | null>
  clearError: () => void
}

export const useAuthOAuth = (): UseAuthOAuthReturn => {
  const {
    ui,
    error,
    login,
    setLoading,
    setError,
    clearError: clearAuthError,
  } = useAuth()

  const clearError = useCallback(() => {
    clearAuthError()
  }, [clearAuthError])

  const getOAuthUrl = useCallback(async (
    provider: 'google' | 'github',
    redirectUri: string
  ) => {
    try {
      setError(null)

      // 验证参数
      if (!redirectUri) {
        setError('回调地址不能为空', 'getOAuthUrl')
        return null
      }

      // 验证回调地址格式
      try {
        new URL(redirectUri)
      } catch {
        setError('回调地址格式不正确', 'getOAuthUrl')
        return null
      }

      const result = await AuthService.getOAuthUrl({
        provider,
        redirect_uri: redirectUri,
      })
      return result
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : `获取 ${provider} 授权链接失败`
      setError(errorMessage, 'getOAuthUrl')
      return null
    }
  }, [setError])

  const handleOAuthCallback = useCallback(async (
    provider: 'google' | 'github',
    code: string,
    state: string,
    redirectUri: string
  ) => {
    try {
      setLoading(true)
      setError(null)

      // 验证参数
      if (!code) {
        setError('授权码不能为空', 'handleOAuthCallback')
        return null
      }

      if (!state) {
        setError('状态参数不能为空', 'handleOAuthCallback')
        return null
      }

      if (!redirectUri) {
        setError('回调地址不能为空', 'handleOAuthCallback')
        return null
      }

      const result = await AuthService.oauthCallback({
        provider,
        code,
        state,
        redirect_uri: redirectUri,
      })
      
      // 登录成功，更新状态
      login(result.user, result.access_token, undefined)
      
      return {
        user: result.user,
        isNewUser: result.is_new_user
      }
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : `${provider} 授权处理失败`
      setError(errorMessage, 'handleOAuthCallback')
      return null
    } finally {
      setLoading(false)
    }
  }, [login, setError, setLoading])

  // 处理 URL 中的 OAuth 回调参数
  useEffect(() => {
    if (typeof window === 'undefined') return

    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const state = urlParams.get('state')
    const provider = urlParams.get('provider') as 'google' | 'github' | null

    // 如果 URL 中有 OAuth 参数，自动处理回调
    if (code && state && provider) {
      const redirectUri = `${window.location.origin}${window.location.pathname}`
      handleOAuthCallback(provider, code, state, redirectUri)
        .then((result) => {
          if (result) {
            // 清除 URL 中的参数
            const newUrl = new URL(window.location.href)
            newUrl.searchParams.delete('code')
            newUrl.searchParams.delete('state')
            newUrl.searchParams.delete('provider')
            
            window.history.replaceState({}, '', newUrl.toString())
          }
        })
        .catch((error) => {
          console.error('OAuth callback handling failed:', error)
        })
    }
  }, [handleOAuthCallback])

  return {
    // State
    isLoading: ui.isLoading,
    error: error.current,
    
    // Actions
    getOAuthUrl,
    handleOAuthCallback,
    clearError,
  }
}

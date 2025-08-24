/**
 * 认证页面组合 Hook
 * 整合认证页面所需的所有业务逻辑
 */

import { useAuthLogin, useAuthRegister, useAuthOAuth, useAuthPassword } from '@/hooks/business/auth'

interface UseAuthPageReturn {
  // Login state and actions
  login: {
    isLoading: boolean
    error: string | null
    loginWithCredentials: (email: string, password: string, rememberMe?: boolean) => Promise<any>
    loginWithOAuth: (provider: 'google' | 'github') => Promise<void>
    clearError: () => void
  }
  
  // Register state and actions
  register: {
    isLoading: boolean
    error: string | null
    registerWithCredentials: (data: any) => Promise<any>
    clearError: () => void
  }
  
  // OAuth state and actions
  oauth: {
    isLoading: boolean
    error: string | null
    getOAuthUrl: (provider: 'google' | 'github', redirectUri: string) => Promise<any>
    handleOAuthCallback: (provider: 'google' | 'github', code: string, state: string, redirectUri: string) => Promise<any>
    clearError: () => void
  }
  
  // Password reset state and actions
  password: {
    isLoading: boolean
    isRequestSent: boolean
    error: string | null
    requestPasswordReset: (email: string) => Promise<boolean>
    clearError: () => void
    reset: () => void
  }
  
  // Unified actions
  clearAllErrors: () => void
}

export const useAuthPage = (): UseAuthPageReturn => {
  // 使用各个业务 hooks
  const loginHook = useAuthLogin()
  const registerHook = useAuthRegister()
  const oauthHook = useAuthOAuth()
  const passwordHook = useAuthPassword()

  // 统一清除所有错误
  const clearAllErrors = () => {
    loginHook.clearError()
    registerHook.clearError()
    oauthHook.clearError()
    passwordHook.clearError()
  }

  return {
    // Login
    login: {
      isLoading: loginHook.isLoading,
      error: loginHook.error,
      loginWithCredentials: loginHook.loginWithCredentials,
      loginWithOAuth: loginHook.loginWithOAuth,
      clearError: loginHook.clearError,
    },
    
    // Register
    register: {
      isLoading: registerHook.isLoading,
      error: registerHook.error,
      registerWithCredentials: registerHook.registerWithCredentials,
      clearError: registerHook.clearError,
    },
    
    // OAuth
    oauth: {
      isLoading: oauthHook.isLoading,
      error: oauthHook.error,
      getOAuthUrl: oauthHook.getOAuthUrl,
      handleOAuthCallback: oauthHook.handleOAuthCallback,
      clearError: oauthHook.clearError,
    },
    
    // Password
    password: {
      isLoading: passwordHook.isLoading,
      isRequestSent: passwordHook.isRequestSent,
      error: passwordHook.error,
      requestPasswordReset: passwordHook.requestPasswordReset,
      clearError: passwordHook.clearError,
      reset: passwordHook.reset,
    },
    
    // Unified actions
    clearAllErrors,
  }
}
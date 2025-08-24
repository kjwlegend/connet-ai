/**
 * 密码管理业务逻辑 Hook
 * 处理密码重置、修改等相关的所有业务逻辑
 */

import { useCallback, useState } from 'react'
import { AuthService } from '@/services/api'
import { useAuth } from '@/store/index'

interface UseAuthPasswordReturn {
  // State
  isLoading: boolean
  isRequestSent: boolean
  error: string | null
  
  // Actions
  requestPasswordReset: (email: string) => Promise<boolean>
  clearError: () => void
  reset: () => void
}

export const useAuthPassword = (): UseAuthPasswordReturn => {
  const [isRequestSent, setIsRequestSent] = useState(false)
  
  const {
    ui,
    error,
    setLoading,
    setError,
    clearError: clearAuthError,
    requestPasswordReset: requestPasswordResetAction,
  } = useAuth()

  const clearError = useCallback(() => {
    clearAuthError()
  }, [clearAuthError])

  const reset = useCallback(() => {
    setIsRequestSent(false)
    clearError()
  }, [clearError])

  const requestPasswordReset = useCallback(async (email: string): Promise<boolean> => {
    try {
      setLoading(true)
      setError(null)
      setIsRequestSent(false)

      // 输入验证
      if (!email?.trim()) {
        setError('邮箱不能为空', 'requestPasswordReset')
        return false
      }

      // 邮箱格式验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email.trim())) {
        setError('邮箱格式不正确', 'requestPasswordReset')
        return false
      }

      // 调用密码重置API
      await requestPasswordResetAction(email.trim().toLowerCase())
      
      setIsRequestSent(true)
      return true
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '发送密码重置邮件失败，请重试'
      setError(errorMessage, 'requestPasswordReset')
      return false
    } finally {
      setLoading(false)
    }
  }, [requestPasswordResetAction, setError, setLoading])

  return {
    // State
    isLoading: ui.isLoading,
    isRequestSent,
    error: error.current,
    
    // Actions
    requestPasswordReset,
    clearError,
    reset,
  }
}
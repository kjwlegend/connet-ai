/**
 * 注册业务逻辑 Hook
 * 处理用户注册相关的所有业务逻辑
 */

import { useCallback } from 'react'
import { AuthService, type RegisterRequest, type RegisterResponse } from '@/services/api'
import { useAuth } from '@/store/index'

interface UseAuthRegisterReturn {
  // State
  isLoading: boolean
  error: string | null
  
  // Actions
  registerWithCredentials: (data: RegisterRequest) => Promise<RegisterResponse | null>
  clearError: () => void
}

export const useAuthRegister = (): UseAuthRegisterReturn => {
  const {
    ui,
    error,
    setLoading,
    setError,
    clearError: clearAuthError,
  } = useAuth()

  const clearError = useCallback(() => {
    clearAuthError()
  }, [clearAuthError])

  const registerWithCredentials = useCallback(async (
    data: RegisterRequest
  ): Promise<RegisterResponse | null> => {
    try {
      setLoading(true)
      setError(null)

      // 输入验证
      if (!data.email?.trim()) {
        setError('邮箱不能为空', 'registerWithCredentials')
        return null
      }

      if (!data.password?.trim()) {
        setError('密码不能为空', 'registerWithCredentials')
        return null
      }

      if (data.password.length < 6) {
        setError('密码长度至少6位', 'registerWithCredentials')
        return null
      }

      if (!data.full_name?.trim()) {
        setError('姓名不能为空', 'registerWithCredentials')
        return null
      }

      // 邮箱格式验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(data.email.trim())) {
        setError('邮箱格式不正确', 'registerWithCredentials')
        return null
      }

      // 调用注册API
      const response = await AuthService.register({
        ...data,
        email: data.email.trim().toLowerCase(),
        full_name: data.full_name.trim(),
      })

      return response
    } catch (error) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : '注册失败，请重试'
      setError(errorMessage, 'registerWithCredentials')
      return null
    } finally {
      setLoading(false)
    }
  }, [setError, setLoading])

  return {
    // State
    isLoading: ui.isLoading,
    error: error.current,
    
    // Actions
    registerWithCredentials,
    clearError,
  }
}
import { useCallback } from 'react'
import { useUI } from '@/store'

export interface ErrorInfo {
  message: string
  code?: string
  details?: any
}

export function useErrorHandler() {
  const { showToast } = useUI()

  const handleError = useCallback((error: Error | ErrorInfo | string) => {
    let errorMessage: string
    let errorCode: string | undefined

    if (typeof error === 'string') {
      errorMessage = error
    } else if (error instanceof Error) {
      errorMessage = error.message
      errorCode = (error as any).code
    } else {
      errorMessage = error.message
      errorCode = error.code
    }

    // Log error for debugging
    console.error('Error handled:', { message: errorMessage, code: errorCode, error })

    // Show user-friendly error message
    showToast({
      type: 'error',
      title: '错误',
      description: errorMessage,
      duration: 5000,
    })

    // Here you could also send error to monitoring service
    // sendToErrorService(error)
  }, [showToast])

  const handleAsyncError = useCallback(async (asyncFn: () => Promise<any>) => {
    try {
      return await asyncFn()
    } catch (error) {
      handleError(error as Error)
      throw error // Re-throw if caller wants to handle it
    }
  }, [handleError])

  const handleApiError = useCallback((error: any) => {
    if (error?.response?.status === 401) {
      handleError('登录已过期，请重新登录')
      // Redirect to login or refresh token
    } else if (error?.response?.status === 403) {
      handleError('您没有权限执行此操作')
    } else if (error?.response?.status === 404) {
      handleError('请求的资源不存在')
    } else if (error?.response?.status >= 500) {
      handleError('服务器错误，请稍后重试')
    } else {
      const message = error?.response?.data?.message || error?.message || '操作失败'
      handleError(message)
    }
  }, [handleError])

  return {
    handleError,
    handleAsyncError,
    handleApiError,
  }
}

export default useErrorHandler
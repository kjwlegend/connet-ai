import { APIError } from './client'
import { env } from '../config/env'
import { StorageUtil } from '../utils/storage'
import { STORAGE_KEYS, HTTP_STATUS } from '../config/constants'

export class APIInterceptors {
  private static retryQueue: Array<() => void> = []
  private static isRefreshing = false

  static setupRequestInterceptor() {
    // This would be implemented when using a proper HTTP client like axios
    // For now, we'll handle this manually in the client
  }

  static async handleRequest(url: string, options: RequestInit): Promise<RequestInit> {
    const token = StorageUtil.getItem<string>(STORAGE_KEYS.AUTH_TOKEN)
    
    if (token) {
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
      }
    }

    return options
  }

  static async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === HTTP_STATUS.UNAUTHORIZED) {
      return this.handleUnauthorized<T>(response)
    }

    if (!response.ok) {
      throw new APIError({
        message: `HTTP ${response.status}: ${response.statusText}`,
        status: response.status,
      })
    }

    return response.json()
  }

  private static async handleUnauthorized<T>(response: Response): Promise<T> {
    const refreshToken = StorageUtil.getItem<string>(STORAGE_KEYS.REFRESH_TOKEN)
    
    if (!refreshToken) {
      this.redirectToLogin()
      throw new APIError({
        message: 'Unauthorized',
        status: HTTP_STATUS.UNAUTHORIZED,
      })
    }

    if (this.isRefreshing) {
      // If already refreshing, queue this request
      return new Promise((resolve, reject) => {
        this.retryQueue.push(() => {
          // Retry the original request
          fetch(response.url, {
            ...response,
            headers: {
              ...response.headers,
              'Authorization': `Bearer ${StorageUtil.getItem<string>(STORAGE_KEYS.AUTH_TOKEN)}`,
            },
          })
            .then(res => res.json())
            .then(resolve)
            .catch(reject)
        })
      })
    }

    this.isRefreshing = true

    try {
      const refreshResponse = await fetch(`${env.API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      })

      if (refreshResponse.ok) {
        const { token: newToken, refreshToken: newRefreshToken } = await refreshResponse.json()
        
        StorageUtil.setItem(STORAGE_KEYS.AUTH_TOKEN, newToken)
        if (newRefreshToken) {
          StorageUtil.setItem(STORAGE_KEYS.REFRESH_TOKEN, newRefreshToken)
        }

        // Process retry queue
        this.retryQueue.forEach(callback => callback())
        this.retryQueue = []

        // Retry original request with new token
        const retryResponse = await fetch(response.url, {
          ...response,
          headers: {
            ...response.headers,
            'Authorization': `Bearer ${newToken}`,
          },
        })

        return retryResponse.json()
      } else {
        this.redirectToLogin()
        throw new APIError({
          message: 'Token refresh failed',
          status: HTTP_STATUS.UNAUTHORIZED,
        })
      }
    } catch (error) {
      this.redirectToLogin()
      throw error
    } finally {
      this.isRefreshing = false
    }
  }

  private static redirectToLogin() {
    StorageUtil.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    StorageUtil.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
    
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
  }

  static handleError(error: any): APIError {
    if (error instanceof APIError) {
      return error
    }

    if (error?.response) {
      return new APIError({
        message: error.response.data?.message || error.response.statusText,
        status: error.response.status,
        code: error.response.data?.code,
      })
    }

    if (error?.code === 'NETWORK_ERROR') {
      return new APIError({
        message: '网络连接失败，请检查网络连接',
        status: 0,
        code: 'NETWORK_ERROR',
      })
    }

    return new APIError({
      message: error?.message || '未知错误',
      status: 0,
    })
  }
}

export default APIInterceptors
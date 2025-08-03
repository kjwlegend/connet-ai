import { APIError } from './client'
import { HTTP_STATUS } from '../config/constants'

export interface ErrorResponse {
  message: string
  code?: string
  details?: any
  status: number
}

export class APIErrorHandler {
  static handle(error: APIError): ErrorResponse {
    const { status, message, code } = error

    switch (status) {
      case HTTP_STATUS.BAD_REQUEST:
        return {
          message: '请求参数错误',
          code,
          status,
        }

      case HTTP_STATUS.UNAUTHORIZED:
        return {
          message: '登录已过期，请重新登录',
          code,
          status,
        }

      case HTTP_STATUS.FORBIDDEN:
        return {
          message: '您没有权限执行此操作',
          code,
          status,
        }

      case HTTP_STATUS.NOT_FOUND:
        return {
          message: '请求的资源不存在',
          code,
          status,
        }

      case HTTP_STATUS.CONFLICT:
        return {
          message: '数据冲突，请刷新后重试',
          code,
          status,
        }

      case HTTP_STATUS.INTERNAL_SERVER_ERROR:
        return {
          message: '服务器内部错误',
          code,
          status,
        }

      case 0:
        return {
          message: '网络连接失败，请检查网络连接',
          code: 'NETWORK_ERROR',
          status,
        }

      default:
        if (status >= 500) {
          return {
            message: '服务器错误，请稍后重试',
            code,
            status,
          }
        }

        return {
          message: message || '操作失败，请重试',
          code,
          status,
        }
    }
  }

  static getErrorMessage(error: any): string {
    if (error instanceof APIError) {
      return this.handle(error).message
    }

    if (typeof error === 'string') {
      return error
    }

    if (error?.message) {
      return error.message
    }

    return '未知错误'
  }

  static isNetworkError(error: APIError): boolean {
    return error.status === 0 || error.code === 'NETWORK_ERROR'
  }

  static isAuthError(error: APIError): boolean {
    return error.status === HTTP_STATUS.UNAUTHORIZED || error.status === HTTP_STATUS.FORBIDDEN
  }

  static isServerError(error: APIError): boolean {
    return error.status >= 500
  }

  static isClientError(error: APIError): boolean {
    return error.status >= 400 && error.status < 500
  }
}

export default APIErrorHandler
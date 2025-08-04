import { ApiError, ApiResponse, ApiErrorResponse } from '@/types/api'

export class APIError extends Error {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.code = code
  }
}

export class ApiClient {
  private baseURL: string
  private getAuthToken: (() => string | null) | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  // Set function to get auth token
  setAuthTokenGetter(getter: () => string | null) {
    this.getAuthToken = getter
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    // Add authorization header if token is available
    if (this.getAuthToken) {
      const token = this.getAuthToken()
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }
    }
    
    const config: RequestInit = {
      ...options,
      headers,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`
        let errorDetails: any = null

        try {
          errorDetails = await response.json()
          if (errorDetails.detail) {
            if (typeof errorDetails.detail === 'string') {
              errorMessage = errorDetails.detail
            } else if (Array.isArray(errorDetails.detail)) {
              // Handle validation errors
              errorMessage = errorDetails.detail.map((err: any) => err.msg).join(', ')
            }
          }
        } catch {
          // Ignore JSON parse errors
        }

        throw new APIError(errorMessage, response.status)
      }

      const data = await response.json()
      return { data, status: response.status }
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      
      throw new APIError(
        error instanceof Error ? error.message : 'Unknown error',
        0
      )
    }
  }

  async get<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

// Create default client instance
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
export const apiClient = new ApiClient(API_BASE_URL)
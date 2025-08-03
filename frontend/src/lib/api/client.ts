import { env } from '../config/env'

export interface APIResponse<T = any> {
  data: T
  message?: string
  success: boolean
  error?: string
}

export interface APIError {
  message: string
  status: number
  code?: string
}

class APIClient {
  private baseURL: string
  private timeout: number

  constructor() {
    this.baseURL = env.API_BASE_URL
    this.timeout = env.API_TIMEOUT
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new APIError({
          message: `HTTP ${response.status}: ${response.statusText}`,
          status: response.status,
        })
      }

      const data = await response.json()
      return data
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      
      throw new APIError({
        message: error instanceof Error ? error.message : 'Unknown error',
        status: 0,
      })
    }
  }

  async get<T>(endpoint: string, options?: RequestInit): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any, options?: RequestInit): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any, options?: RequestInit): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string, options?: RequestInit): Promise<APIResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

export const apiClient = new APIClient()
export { APIError }
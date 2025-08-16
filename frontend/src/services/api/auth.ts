import { apiClient } from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  username?: string
  invited_by_code?: string
  registration_source?: string
  registration_channel?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface PasswordResetRequest {
  email: string
}

export interface VerifyTokenRequest {
  token: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RegisterResponse {
  user: User
  message: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface User {
  id: string
  email: string
  full_name: string
  username?: string
  is_active: boolean
  is_verified?: boolean
  invitation_code?: string
  created_at: string
  updated_at: string
  last_login_at?: string
  permissions: string[]
  roles: string[]
  avatar?: string
}

export interface VerifyTokenResponse {
  valid: boolean
  user?: User
}

export interface MessageResponse {
  message: string
}

export interface OAuthUrlRequest {
  provider: 'google' | 'github'
  redirect_uri: string
  state?: string
}

export interface OAuthUrlResponse {
  url: string
  state: string
}

export interface OAuthCallbackRequest {
  provider: 'google' | 'github'
  code: string
  state?: string
  redirect_uri: string
}

export interface OAuthLoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
  is_new_user: boolean
}

export class AuthAPI {
  private static client = apiClient

  /**
   * 用户注册
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await this.client.post<UserResponse>(
        '/api/v1/auth/register',
        data
      )
      // BFF returns UserResponse directly, wrap it in RegisterResponse format
      return {
        user: response.data,
        message: 'User registered successfully'
      }
    } catch (error: any) {
      // Re-throw with proper error message for toast display
      const errorMessage = error?.message || 'Registration failed. Please try again.'
      throw new Error(errorMessage)
    }
  } 

  /**
   * 用户登录
   */
  static async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await this.client.post<LoginResponse>(
        '/api/v1/auth/login',
        data
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Login failed. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * 刷新访问令牌
   */
  static async refreshToken(
    data: RefreshTokenRequest
  ): Promise<RefreshTokenResponse> {
    const response = await this.client.post<LoginResponse>(
      '/api/v1/auth/refresh',
      data
    )
    // BFF returns LoginResponse, map to RefreshTokenResponse
    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      token_type: response.data.token_type,
      expires_in: response.data.expires_in,
      user: response.data.user
    }
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<User> {
    const response = await this.client.get<UserResponse>('/api/v1/auth/me')
    return response.data
  }

  /**
   * 用户登出
   */
  static async logout(): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      '/api/v1/auth/logout',
      {}
    )
    return response.data
  }

  /**
   * 密码重置请求
   */
  static async requestPasswordReset(
    data: PasswordResetRequest
  ): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      '/api/v1/auth/password-reset',
      data
    )
    return response.data
  }

  /**
   * 验证邮箱
   */
  static async verifyEmail(
    token: string,
    email: string
  ): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      `/api/v1/auth/verify-email?token=${encodeURIComponent(
        token
      )}&email=${encodeURIComponent(email)}`,
      {}
    )
    return response.data
  }

  /**
   * 验证令牌
   */
  static async verifyToken(
    data: VerifyTokenRequest
  ): Promise<VerifyTokenResponse> {
    const response = await this.client.post<any>(
      '/api/v1/auth/verify',
      data
    )
    // BFF returns { valid: boolean, payload?: any, error?: string }
    return {
      valid: response.data.valid,
      user: response.data.payload ? undefined : undefined // BFF doesn't return user in verify
    }
  }

  /**
   * 获取 OAuth 授权 URL
   */
  static async getOAuthUrl(data: OAuthUrlRequest): Promise<OAuthUrlResponse> {
    const response = await this.client.get<OAuthUrlResponse>(
      '/api/v1/auth/oauth/url',
      data
    )
    return response.data
  }

  /**
   * OAuth 回调处理
   */
  static async oauthCallback(
    data: OAuthCallbackRequest
  ): Promise<OAuthLoginResponse> {
    const response = await this.client.post<OAuthLoginResponse>(
      '/api/v1/auth/oauth/callback',
      data
    )
    return response.data
  }
}

// Export the class
export { AuthAPI as default }

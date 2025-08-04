import { 
  LoginRequest, 
  RegisterRequest, 
  RefreshTokenRequest,
  PasswordResetRequest,
  VerifyTokenRequest,
  LoginResponse,
  RegisterResponse,
  RefreshTokenResponse,
  User,
  VerifyTokenResponse,
  MessageResponse
} from '@/types/api'
import { apiClient } from './client'

export class AuthAPI {
  private static client = apiClient

  /**
   * 用户注册
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.client.post<RegisterResponse>('/auth/register', data)
    return response.data
  }

  /**
   * 用户登录
   */
  static async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await this.client.post<LoginResponse>('/auth/login', data)
    return response.data
  }

  /**
   * 刷新访问令牌
   */
  static async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    const response = await this.client.post<RefreshTokenResponse>('/auth/refresh', data)
    return response.data
  }

  /**
   * 获取当前用户信息
   */
  static async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me')
    return response.data
  }

  /**
   * 用户登出
   */
  static async logout(): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>('/auth/logout', {})
    return response.data
  }

  /**
   * 密码重置请求
   */
  static async requestPasswordReset(data: PasswordResetRequest): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>('/auth/password-reset', data)
    return response.data
  }

  /**
   * 验证邮箱
   */
  static async verifyEmail(token: string, email: string): Promise<MessageResponse> {
    const response = await this.client.post<MessageResponse>(
      `/auth/verify-email?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`,
      {}
    )
    return response.data
  }

  /**
   * 验证令牌
   */
  static async verifyToken(data: VerifyTokenRequest): Promise<VerifyTokenResponse> {
    const response = await this.client.post<VerifyTokenResponse>('/auth/verify', data)
    return response.data
  }
}
/**
 * Authentication API Service
 * Handles all authentication-related API calls
 */

import { apiClient } from '../client'
import type { 
  LoginRequest,
  RegisterRequest, 
  RefreshTokenRequest,
  PasswordResetRequest,
  VerifyTokenRequest,
  OAuthUrlRequest,
  OAuthCallbackRequest,
  LoginResponse,
  RegisterResponse,
  RefreshTokenResponse,
  User,
  UserResponse,
  VerifyTokenResponse,
  MessageResponse,
  OAuthUrlResponse,
  OAuthLoginResponse
} from '../types/auth'

export class AuthService {
  private static readonly BASE_PATH = '/api/v1/auth'

  /**
   * User registration
   */
  static async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await apiClient.post<UserResponse>(
        `${this.BASE_PATH}/register`,
        data
      )
      // BFF returns UserResponse directly, wrap it in RegisterResponse format
      return {
        user: response.data,
        message: 'User registered successfully',
      }
    } catch (error: any) {
      // Re-throw with proper error message for toast display
      const errorMessage =
        error?.message || 'Registration failed. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * User login
   */
  static async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>(
        `${this.BASE_PATH}/login`,
        data
      )
      return response.data
    } catch (error: any) {
      const errorMessage = error?.message || 'Login failed. Please try again.'
      throw new Error(errorMessage)
    }
  }

  /**
   * Refresh access token
   */
  static async refreshToken(
    data: RefreshTokenRequest
  ): Promise<RefreshTokenResponse> {
    const response = await apiClient.post<LoginResponse>(
      `${this.BASE_PATH}/refresh`,
      data
    )
    // BFF returns LoginResponse, map to RefreshTokenResponse
    return {
      access_token: response.data.access_token,
      refresh_token: response.data.refresh_token,
      token_type: response.data.token_type,
      expires_in: response.data.expires_in,
      user: response.data.user,
    }
  }

  /**
   * Get current user information
   */
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<UserResponse>(`${this.BASE_PATH}/me`)
    return response.data
  }

  /**
   * User logout
   */
  static async logout(): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      `${this.BASE_PATH}/logout`,
      {}
    )
    return response.data
  }

  /**
   * Password reset request
   */
  static async requestPasswordReset(
    data: PasswordResetRequest
  ): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      `${this.BASE_PATH}/password-reset`,
      data
    )
    return response.data
  }

  /**
   * Verify email
   */
  static async verifyEmail(
    token: string,
    email: string
  ): Promise<MessageResponse> {
    const response = await apiClient.post<MessageResponse>(
      `${this.BASE_PATH}/verify-email?token=${encodeURIComponent(
        token
      )}&email=${encodeURIComponent(email)}`,
      {}
    )
    return response.data
  }

  /**
   * Verify token
   */
  static async verifyToken(
    data: VerifyTokenRequest
  ): Promise<VerifyTokenResponse> {
    const response = await apiClient.post<any>(`${this.BASE_PATH}/verify`, data)
    // BFF returns { valid: boolean, payload?: any, error?: string }
    return {
      valid: response.data.valid,
      user: response.data.payload ? undefined : undefined, // BFF doesn't return user in verify
    }
  }

  /**
   * Get OAuth authorization URL
   */
  static async getOAuthUrl(data: OAuthUrlRequest): Promise<OAuthUrlResponse> {
    const response = await apiClient.get<OAuthUrlResponse>(
      `${this.BASE_PATH}/oauth/url`,
      data
    )
    return response.data
  }

  /**
   * OAuth callback handling
   */
  static async oauthCallback(
    data: OAuthCallbackRequest
  ): Promise<OAuthLoginResponse> {
    const response = await apiClient.post<OAuthLoginResponse>(
      `${this.BASE_PATH}/oauth/callback`,
      data
    )
    return response.data
  }
}

export default AuthService
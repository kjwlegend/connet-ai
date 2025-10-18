/**
 * Authentication API Types
 * All types related to authentication and user management
 */

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
  refresh_token?: string
}

export interface PasswordResetRequest {
  email: string
}

export interface VerifyTokenRequest {
  token: string
}

export interface OAuthUrlRequest {
  provider: 'google' | 'github'
  redirect_uri: string
  state?: string
}

export interface OAuthCallbackRequest {
  provider: 'google' | 'github'
  code: string
  state?: string
  redirect_uri: string
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

export interface UserResponse extends User {}

export interface LoginResponse {
  access_token: string
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
  token_type: string
  expires_in: number
  user: User
}

export interface VerifyTokenResponse {
  valid: boolean
  user?: User
}

export interface MessageResponse {
  message: string
}

export interface OAuthUrlResponse {
  url: string
  state: string
}

export interface OAuthLoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
  is_new_user: boolean
}

// API Request Types
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
  registration_source?: 'web' | 'mobile' | 'api'
  registration_channel?: 'organic' | 'invite' | 'social' | 'campaign'
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

// API Response Types
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RegisterResponse {
  id: string
  email: string
  full_name: string
  username?: string
  is_active: boolean
  invitation_code: string
  created_at: string
  updated_at: string
  last_login_at?: string
  permissions: string[]
  roles: string[]
}

export interface User {
  id: string
  email: string
  full_name: string
  username?: string
  is_active: boolean
  invitation_code?: string
  created_at: string
  updated_at: string
  last_login_at?: string
  permissions: string[]
  roles: string[]
}

export interface TokenPayload {
  sub: string
  exp: number
  iat: number
  type: string
  scopes: string[]
}

export interface VerifyTokenResponse {
  valid: boolean
  payload?: TokenPayload
}

export interface ApiError {
  detail: string | ValidationError[]
}

export interface ValidationError {
  loc: string[]
  msg: string
  type: string
}

export interface MessageResponse {
  message: string
}

// Utility Types
export type ApiResponse<T> = {
  data: T
  status: number
}

export type ApiErrorResponse = {
  error: ApiError
  status: number
}
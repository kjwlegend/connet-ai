import { BaseEntity } from './common'

/**
 * Authentication and user-related types
 */

// User profile types
export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'zh'
  timezone: string
  dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD'
  timeFormat: '12h' | '24h'
  notifications: {
    email: boolean
    push: boolean
    mentions: boolean
    directMessages: boolean
    groupMessages: boolean
    systemUpdates: boolean
  }
  privacy: {
    showOnlineStatus: boolean
    allowDirectMessages: boolean
    showLastSeen: boolean
  }
}

export interface UserProfile extends BaseEntity {
  email: string
  username?: string
  fullName: string
  displayName?: string
  avatar?: string
  bio?: string
  title?: string
  department?: string
  location?: string
  phoneNumber?: string
  isActive: boolean
  isVerified: boolean
  invitationCode?: string
  lastLoginAt?: string
  preferences: UserPreferences
}

// Permission and role types
export type Permission = 
  // Basic permissions
  | 'read' | 'write' | 'delete' | 'admin'
  // Chat permissions  
  | 'chat.create' | 'chat.join' | 'chat.moderate' | 'chat.archive'
  // User permissions
  | 'user.invite' | 'user.manage' | 'user.impersonate'
  // System permissions
  | 'system.config' | 'system.monitor' | 'system.backup'
  // Content permissions
  | 'content.publish' | 'content.moderate' | 'content.analytics'

export interface Role extends BaseEntity {
  name: string
  displayName: string
  description?: string
  permissions: Permission[]
  isSystem: boolean
  color?: string
  priority: number
}

// Authentication state types
export interface AuthTokens {
  accessToken: string
  refreshToken?: string
  tokenType: 'Bearer'
  expiresAt: string
  refreshExpiresAt?: string
}

export interface AuthSession {
  id: string
  userId: string
  deviceId: string
  deviceName?: string
  deviceType: 'web' | 'mobile' | 'desktop' | 'api'
  ipAddress: string
  userAgent?: string
  location?: string
  isActive: boolean
  lastActivity: string
  createdAt: string
  expiresAt: string
}

// Organization/Team types (for future multi-tenant support)
export interface Organization extends BaseEntity {
  name: string
  displayName?: string
  description?: string
  logo?: string
  website?: string
  settings: {
    allowPublicSignup: boolean
    requireInvitation: boolean
    defaultRole: string
    maxUsers?: number
    features: {
      chatEnabled: boolean
      filesEnabled: boolean
      pluginsEnabled: boolean
      customBranding: boolean
    }
  }
}

export interface OrganizationMembership extends BaseEntity {
  userId: string
  organizationId: string
  roleId: string
  status: 'pending' | 'active' | 'suspended' | 'removed'
  joinedAt: string
  invitedBy?: string
  invitationCode?: string
}

// Authentication request/response types
export interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
  deviceId?: string
  deviceName?: string
}

export interface RegisterRequest {
  email: string
  password: string
  fullName: string
  username?: string
  invitationCode?: string
  acceptTerms: boolean
}

export interface AuthResponse {
  user: UserProfile
  tokens: AuthTokens
  session: AuthSession
  organization?: Organization
  roles: Role[]
  permissions: Permission[]
}

export interface RefreshTokenRequest {
  refreshToken: string
  deviceId?: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirmRequest {
  token: string
  newPassword: string
}

export interface ChangePasswordRequest {
  currentPassword: string
  newPassword: string
}

export interface UpdateProfileRequest {
  fullName?: string
  displayName?: string
  bio?: string
  title?: string
  department?: string
  location?: string
  phoneNumber?: string
  preferences?: Partial<UserPreferences>
}

// Auth state interface
export interface AuthState {
  // Core auth state
  isAuthenticated: boolean
  user: UserProfile | null
  tokens: AuthTokens | null
  session: AuthSession | null
  
  // Permissions and roles
  roles: Role[]
  permissions: Permission[]
  
  // Organization context (for multi-tenant)
  organization: Organization | null
  membership: OrganizationMembership | null
  
  // Loading and error states
  isLoading: boolean
  isInitializing: boolean
  error: string | null
  
  // Session management
  lastActivity: string
  sessionWarningShown: boolean
  
  // Security
  failedAttempts: number
  lockoutUntil?: string
  requiresMFA: boolean
  mfaVerified: boolean
}

// Auth action types
export interface AuthActions {
  // Authentication
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: (revokeAllSessions?: boolean) => Promise<void>
  refreshToken: () => Promise<boolean>
  
  // Session management
  validateSession: () => Promise<boolean>
  updateActivity: () => void
  handleSessionExpiry: () => void
  
  // Profile management
  updateProfile: (updates: UpdateProfileRequest) => Promise<void>
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<void>
  uploadAvatar: (file: File) => Promise<string>
  
  // Password management
  changePassword: (data: ChangePasswordRequest) => Promise<void>
  requestPasswordReset: (email: string) => Promise<void>
  confirmPasswordReset: (data: PasswordResetConfirmRequest) => Promise<void>
  
  // Two-factor authentication
  enableMFA: () => Promise<{ qrCode: string; backupCodes: string[] }>
  disableMFA: (code: string) => Promise<void>
  verifyMFA: (code: string) => Promise<void>
  
  // Session management
  getSessions: () => Promise<AuthSession[]>
  revokeSession: (sessionId: string) => Promise<void>
  revokeAllOtherSessions: () => Promise<void>
  
  // Internal state management
  setUser: (user: UserProfile) => void
  setTokens: (tokens: AuthTokens) => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
  clearError: () => void
  initialize: () => Promise<void>
}

// Utility types
export type AuthSlice = AuthState & AuthActions

// Helper type for checking permissions
export type PermissionCheck = {
  hasPermission: (permission: Permission) => boolean
  hasRole: (roleName: string) => boolean
  hasAnyPermission: (permissions: Permission[]) => boolean
  hasAllPermissions: (permissions: Permission[]) => boolean
}

// Auth context type (for React components)
export interface AuthContextType extends AuthSlice, PermissionCheck {
  isReady: boolean
}

// Export collections
export type AuthEntities = {
  UserProfile: UserProfile
  Role: Role
  AuthSession: AuthSession
  Organization: Organization
  OrganizationMembership: OrganizationMembership
}

export type AuthRequests = {
  Login: LoginRequest
  Register: RegisterRequest
  UpdateProfile: UpdateProfileRequest
  ChangePassword: ChangePasswordRequest
  PasswordReset: PasswordResetRequest
  PasswordResetConfirm: PasswordResetConfirmRequest
}
/**
 * 简化的认证状态管理 Slice
 * 只负责状态管理，不包含业务逻辑
 * 业务逻辑已移至 /hooks/business/auth/
 */

import { StateCreator } from "zustand"

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
  avatar?: string
  preferences?: UserPreferences
}

export interface UserPreferences {
  theme: "light" | "dark" | "system"
  language: "en" | "zh"
  notifications: {
    email: boolean
    push: boolean
    mentions: boolean
  }
}

// 认证状态接口
export interface AuthState {
  // 核心认证数据
  auth: {
    user: User | null
    token: string | null
    refreshToken: string | null
    isAuthenticated: boolean
    sessionStarted: Date | null
    lastActivity: Date | null
  }
  
  // UI状态
  authUI: {
    isLoading: boolean
    isInitializing: boolean
    showLoginModal: boolean
  }
  
  // 错误状态
  error: {
    current: string | null
    history: Array<{
      message: string
      timestamp: Date
      action: string
    }>
  }
}

// 认证动作接口
export interface AuthActions {
  // 核心状态管理动作
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setRefreshToken: (refreshToken: string | null) => void
  setAuthenticated: (authenticated: boolean) => void
  setSessionStarted: (started: Date | null) => void
  updateLastActivity: () => void
  
  // UI状态管理
  setLoading: (loading: boolean) => void
  setInitializing: (initializing: boolean) => void
  toggleLoginModal: (show?: boolean) => void
  
  // 错误状态管理
  setError: (error: string | null, action?: string) => void
  clearError: () => void
  clearErrorHistory: () => void
  
  // 用户偏好管理
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void
  
  // 会话管理
  extendSession: () => void
  clearSession: () => void
  checkSessionTimeout: () => boolean
  resetSession: () => void
  
  // 认证业务逻辑（异步操作的占位符）
  initializeAuth: () => Promise<void>
  validateToken: () => Promise<boolean>
  refreshAuthToken: () => Promise<boolean>
  getCurrentUser: () => Promise<void>
  
  // 复合操作（保留最基本的）
  login: (user: User, token: string, refreshToken?: string) => void
  logout: () => void
}

export type AuthSlice = AuthState & AuthActions

// 初始状态
const initialAuthState: AuthState = {
  auth: {
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    sessionStarted: null,
    lastActivity: null,
  },
  authUI: {
    isLoading: false,
    isInitializing: false,
    showLoginModal: false,
  },
  error: {
    current: null,
    history: [],
  },
}

const createAuthSlice: StateCreator<AuthSlice, [], [], AuthSlice> = (set, get) => ({
  ...initialAuthState,

  // 核心状态管理动作
  setUser: (user) => {
    set(state => ({
      auth: {
        ...state.auth,
        user,
        lastActivity: user ? new Date() : state.auth.lastActivity,
      }
    }))
  },

  setToken: (token) => {
    set(state => ({
      auth: { ...state.auth, token }
    }))
  },

  setRefreshToken: (refreshToken) => {
    set(state => ({
      auth: { ...state.auth, refreshToken }
    }))
  },

  setAuthenticated: (isAuthenticated) => {
    set(state => ({
      auth: { ...state.auth, isAuthenticated }
    }))
  },

  setSessionStarted: (sessionStarted) => {
    set(state => ({
      auth: { ...state.auth, sessionStarted }
    }))
  },

  updateLastActivity: () => {
    set(state => ({
      auth: {
        ...state.auth,
        lastActivity: new Date(),
      }
    }))
  },

  // UI状态管理
  setLoading: (isLoading) => {
    set(state => ({
      authUI: { ...state.authUI, isLoading }
    }))
  },

  setInitializing: (isInitializing) => {
    set(state => ({
      authUI: { ...state.authUI, isInitializing }
    }))
  },

  toggleLoginModal: (show) => {
    set(state => ({
      authUI: {
        ...state.authUI,
        showLoginModal: show !== undefined ? show : !state.authUI.showLoginModal,
      }
    }))
  },

  // 错误状态管理
  setError: (error, action = 'unknown') => {
    set(state => ({
      error: {
        current: error,
        history: error ? [
          ...state.error.history.slice(-4),
          {
            message: error,
            timestamp: new Date(),
            action,
          }
        ] : state.error.history,
      },
      authUI: {
        ...state.authUI,
        isLoading: false, // 出错时停止loading
      }
    }))
  },

  clearError: () => {
    set(state => ({
      error: { ...state.error, current: null }
    }))
  },

  clearErrorHistory: () => {
    set(state => ({
      error: { ...state.error, history: [] }
    }))
  },

  // 用户偏好管理
  updateUserPreferences: (preferences) => {
    const { auth } = get()
    if (auth.user) {
      const updatedUser = {
        ...auth.user,
        preferences: {
          ...auth.user.preferences,
          ...preferences,
        },
      }
      get().setUser(updatedUser)
    }
  },

  // 会话管理
  extendSession: () => {
    set(state => ({
      auth: {
        ...state.auth,
        lastActivity: new Date(),
      }
    }))
  },

  clearSession: () => {
    set(state => ({
      auth: {
        ...initialAuthState.auth,
      }
    }))
  },

  checkSessionTimeout: () => {
    const { auth } = get()
    if (!auth.isAuthenticated || !auth.lastActivity) {
      return true
    }
    
    // 检查是否超过2小时无活动（可配置）
    const sessionTimeout = 2 * 60 * 60 * 1000 // 2小时
    const timeSinceLastActivity = Date.now() - auth.lastActivity.getTime()
    return timeSinceLastActivity > sessionTimeout
  },

  resetSession: () => {
    set(() => ({
      ...initialAuthState
    }))
  },

  // 认证业务逻辑（异步操作的占位符）
  // 这些方法在store中只是占位符，实际实现在对应的hook中
  initializeAuth: async () => {
    // 占位符：实际逻辑在 useAuthSession 中实现
    console.warn('initializeAuth called from store - this should be implemented in useAuthSession hook')
  },

  validateToken: async () => {
    // 占位符：实际逻辑在 useAuthSession 中实现
    console.warn('validateToken called from store - this should be implemented in useAuthSession hook')
    return false
  },

  refreshAuthToken: async () => {
    // 占位符：实际逻辑在 useAuthSession 中实现
    console.warn('refreshAuthToken called from store - this should be implemented in useAuthSession hook')
    return false
  },

  getCurrentUser: async () => {
    // 占位符：实际逻辑在 useAuthSession 中实现
    console.warn('getCurrentUser called from store - this should be implemented in useAuthSession hook')
  },

  // 复合操作
  login: (user, token, refreshToken) => {
    const now = new Date()
    set(state => ({
      auth: {
        ...state.auth,
        user,
        token,
        refreshToken: refreshToken || null,
        isAuthenticated: true,
        sessionStarted: now,
        lastActivity: now,
      },
      authUI: {
        ...state.authUI,
        isLoading: false,
        showLoginModal: false,
      },
      error: {
        ...state.error,
        current: null,
      },
    }))
  },

  logout: () => {
    set(state => ({
      auth: {
        ...initialAuthState.auth,
      },
      authUI: {
        ...state.authUI,
        isLoading: false,
      },
      error: {
        ...state.error,
        current: null,
      },
    }))
  },
})

export default createAuthSlice
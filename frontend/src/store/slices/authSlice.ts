import { StateCreator } from 'zustand'
import { StoreState } from '../types'
import { StorageUtil } from '@/lib/utils/storage'
import { STORAGE_KEYS } from '@/lib/config/constants'

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  role: 'user' | 'admin'
  preferences?: UserPreferences
  createdAt: string
  updatedAt: string
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'zh'
  notifications: {
    email: boolean
    push: boolean
    mentions: boolean
  }
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface AuthActions {
  login: (userData: User, token: string, refreshToken?: string) => void
  logout: () => void
  setUser: (user: User) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
  updateUserPreferences: (preferences: Partial<UserPreferences>) => void
  initializeAuth: () => void
}

export type AuthSlice = AuthState & AuthActions

const createAuthSlice: StateCreator<StoreState, [], [], AuthSlice> = (set, get) => ({
  // State
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Actions
  login: (userData, token, refreshToken) => {
    StorageUtil.setItem(STORAGE_KEYS.AUTH_TOKEN, token)
    if (refreshToken) {
      StorageUtil.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken)
    }
    
    set({
      user: userData,
      token,
      refreshToken,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    })
  },

  logout: () => {
    StorageUtil.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    StorageUtil.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
    
    set({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
  },

  setUser: (user) => {
    set({ user })
  },

  setLoading: (isLoading) => {
    set({ isLoading })
  },

  setError: (error) => {
    set({ error, isLoading: false })
  },

  clearError: () => {
    set({ error: null })
  },

  updateUserPreferences: (preferences) => {
    const { user } = get()
    if (user) {
      const updatedUser = {
        ...user,
        preferences: {
          ...user.preferences,
          ...preferences,
        },
      }
      set({ user: updatedUser })
    }
  },

  initializeAuth: () => {
    const token = StorageUtil.getItem<string>(STORAGE_KEYS.AUTH_TOKEN)
    const refreshToken = StorageUtil.getItem<string>(STORAGE_KEYS.REFRESH_TOKEN)
    
    if (token) {
      set({
        token,
        refreshToken,
        isAuthenticated: true,
        isLoading: true,
      })
      // Here you would typically validate the token with your backend
    }
  },
})

export default createAuthSlice

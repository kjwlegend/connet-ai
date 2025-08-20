import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { env } from '@/lib/config/env'

// Import slice creators
import createAuthSlice from './slices/auth/authSlice'
import createPreferencesSlice from './slices/ui/preferencesSlice'
import createLayoutSlice from './slices/ui/layoutSlice'
import createNotificationSlice from './slices/ui/notificationSlice'
import createConversationSlice from './slices/chat/conversationSlice'

// Import utilities
import { PERSIST_CONFIGS, STORAGE_CATEGORIES } from './utils/persistence'
import { logger } from './middleware/logger'

// Import types
import { AuthSlice } from './slices/auth/authSlice'
import { PreferencesSlice } from './slices/ui/preferencesSlice'
import { LayoutSlice } from './slices/ui/layoutSlice'
import { NotificationSlice } from './slices/ui/notificationSlice'
import { ConversationSlice } from './slices/chat/conversationSlice'

/**
 * Enhanced Store Architecture - Phase 1 Implementation
 * 
 * Features:
 * - Layered data architecture (UI, App, Cache, Realtime)
 * - Selective persistence with TTL support
 * - Optimized slice structure for performance
 * - Comprehensive type safety
 * - Cache management with automatic cleanup
 */

// Combined store state type
export interface AppStoreState extends 
  AuthSlice, 
  PreferencesSlice, 
  LayoutSlice, 
  NotificationSlice, 
  ConversationSlice {}

// Create the main store with enhanced middleware
const useAppStore = create<AppStoreState>()(
  devtools(
    logger(
      subscribeWithSelector(
        (set, get, store) => ({
          // Auth slice - with secure persistence
          ...createAuthSlice(set, get, store),
          
          // UI slices - with different persistence strategies
          ...createPreferencesSlice(set, get, store),
          ...createLayoutSlice(set, get, store),
          ...createNotificationSlice(set, get, store),
          
          // Chat slices - with cache-based persistence
          ...createConversationSlice(set, get, store),
        })
      ),
      'AppStore-v2'
    ),
    {
      name: 'connet-ai-devtools-v2',
      enabled: env.ENABLE_DEBUG,
    }
  )
)

// Separate stores for different persistence strategies
const createUIPreferencesStore = () => create<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>()(
  persist(
    devtools(
      (set, get, store) => ({
        ...createPreferencesSlice(set, get, store),
        ...createLayoutSlice(set, get, store),
        ...createNotificationSlice(set, get, store),
        ...createConversationSlice(set, get, store),
      }),
      { name: 'ui-preferences' }
    ),
    PERSIST_CONFIGS.UI_PREFERENCES<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>('ui-preferences')
  )
)

const createLayoutStore = () => create<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>()(
  persist(
    devtools(
      (set, get, store) => ({
        ...createPreferencesSlice(set, get, store),
        ...createLayoutSlice(set, get, store),
        ...createNotificationSlice(set, get, store),
        ...createConversationSlice(set, get, store),
      }),
      { name: 'layout-state' }
    ),
    PERSIST_CONFIGS.LAYOUT_STATE<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>('layout-state')
  )
)

const createChatCacheStore = () => create<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>()(
  persist(
    devtools(
      (set, get, store) => ({
        ...createPreferencesSlice(set, get, store),
        ...createLayoutSlice(set, get, store),
        ...createNotificationSlice(set, get, store),
        ...createConversationSlice(set, get, store),
      }),
      { name: 'chat-cache' }
    ),
    PERSIST_CONFIGS.CHAT_CACHE<PreferencesSlice & LayoutSlice & NotificationSlice & ConversationSlice>('chat-cache', ['conversations'])
  )
)

export default useAppStore

// Export specialized store hooks with optimized selectors

// Enhanced Auth Hook with Better Performance - use stable selectors to prevent infinite loops
export const useAuth = () => {
  const auth = useAppStore((state) => state.auth)
  const ui = useAppStore((state) => state.ui)
  const error = useAppStore((state) => state.error)
  
  // Get actions with stable selectors
  const login = useAppStore((state) => state.login)
  const logout = useAppStore((state) => state.logout)
  const setUser = useAppStore((state) => state.setUser)
  const setLoading = useAppStore((state) => state.setLoading)
  const setInitializing = useAppStore((state) => state.setInitializing)
  const toggleLoginModal = useAppStore((state) => state.toggleLoginModal)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
  const clearErrorHistory = useAppStore((state) => state.clearErrorHistory)
  const updateUserPreferences = useAppStore((state) => state.updateUserPreferences)
  const initializeAuth = useAppStore((state) => state.initializeAuth)
  const loginWithCredentials = useAppStore((state) => state.loginWithCredentials)
  const registerWithCredentials = useAppStore((state) => state.registerWithCredentials)
  const validateToken = useAppStore((state) => state.validateToken)
  const refreshAuthToken = useAppStore((state) => state.refreshAuthToken)
  const getCurrentUser = useAppStore((state) => state.getCurrentUser)
  const getOAuthUrl = useAppStore((state) => state.getOAuthUrl)
  const handleOAuthCallback = useAppStore((state) => state.handleOAuthCallback)
  const loginWithOAuth = useAppStore((state) => state.loginWithOAuth)
  const requestPasswordReset = useAppStore((state) => state.requestPasswordReset)
  const extendSession = useAppStore((state) => state.extendSession)
  const checkSessionTimeout = useAppStore((state) => state.checkSessionTimeout)
  const resetSession = useAppStore((state) => state.resetSession)
  
  return {
    auth,
    ui,
    error,
    login,
    logout,
    setUser,
    setLoading,
    setInitializing,
    toggleLoginModal,
    setError,
    clearError,
    clearErrorHistory,
    updateUserPreferences,
    initializeAuth,
    loginWithCredentials,
    registerWithCredentials,
    validateToken,
    refreshAuthToken,
    getCurrentUser,
    getOAuthUrl,
    handleOAuthCallback,
    loginWithOAuth,
    requestPasswordReset,
    extendSession,
    checkSessionTimeout,
    resetSession,
  }
}

// Lightweight auth hooks for specific use cases
export const useAuthUser = () => useAppStore((state) => state.auth.user)
export const useAuthToken = () => useAppStore((state) => state.auth.token)
export const useIsAuthenticated = () => useAppStore((state) => state.auth.isAuthenticated)
export const useAuthLoading = () => useAppStore((state) => state.ui.isLoading)
export const useAuthError = () => useAppStore((state) => state.error.current)

export const useUIPreferences = () => {
  return useAppStore((state) => ({
    preferences: state.preferences,
    setTheme: state.setTheme,
    setLanguage: state.setLanguage,
    updatePreferences: state.updatePreferences,
    resetPreferences: state.resetPreferences,
  }))
}

export const useLayout = () => {
  return useAppStore((state) => ({
    layout: state.layout,
    navigation: state.navigation,
    toggleSidebar: state.toggleSidebar,
    setSidebarCollapsed: state.setSidebarCollapsed,
    setMiddlePanelWidth: state.setMiddlePanelWidth,
    setCurrentNavigation: state.setCurrentNavigation,
    navigateTo: state.navigateTo,
    applyLayoutPreset: state.applyLayoutPreset,
  }))
}

export const useNotifications = () => {
  return useAppStore((state) => ({
    notifications: state.notifications,
    modals: state.modals,
    showToast: state.showToast,
    removeToast: state.removeToast,
    clearToasts: state.clearToasts,
    openModal: state.openModal,
    closeModal: state.closeModal,
    closeAllModals: state.closeAllModals,
  }))
}

export const useConversations = () => {
  return useAppStore((state) => ({
    conversations: state.conversations,
    activeConversationId: state.activeConversationId,
    isLoading: state.isLoading,
    conversationError: state.conversationError,
    loadConversations: state.loadConversations,
    createConversation: state.createConversation,
    setActiveConversation: state.setActiveConversation,
    pinConversation: state.pinConversation,
    archiveConversation: state.archiveConversation,
    exportConversation: state.exportConversation,
    setConversationError: state.setConversationError,
    clearConversationError: state.clearConversationError,
  }))
}

// Helper hooks with toast shortcuts
export const useToasts = () => {
  const showToast = useAppStore((state) => state.showToast)
  
  return {
    success: (title: string, description?: string) =>
      showToast({ type: 'success', title, description, persistent: false }),
    error: (title: string, description?: string) =>
      showToast({ type: 'error', title, description, persistent: true }),
    warning: (title: string, description?: string) =>
      showToast({ type: 'warning', title, description, persistent: false }),
    info: (title: string, description?: string) =>
      showToast({ type: 'info', title, description, persistent: false }),
    loading: (title: string, description?: string) =>
      showToast({ type: 'loading', title, description, persistent: true }),
  }
}

// Performance monitoring hook
export const useStoreStats = () => {
  return useAppStore((state) => {
    const stateSize = JSON.stringify(state).length
    const conversationsCount = state.conversations.data.length
    const toastsCount = state.notifications.toasts.length
    const modalsCount = state.modals.modals.length
    
    return {
      stateSize,
      counts: {
        conversations: conversationsCount,
        toasts: toastsCount,
        modals: modalsCount,
      },
      cacheStatus: {
        conversationsValid: state.conversations.timestamp + state.conversations.ttl > Date.now(),
        conversationsAge: Date.now() - state.conversations.timestamp,
      },
    }
  })
}

// Development helpers
export const useDevTools = () => {
  if (!env.ENABLE_DEBUG) {
    return {
      getState: () => null,
      resetStore: () => {},
      exportState: () => '{}',
    }
  }
  
  return {
    getState: () => useAppStore.getState(),
    resetStore: () => {
      // Reset to initial state
      useAppStore.setState({
        preferences: createPreferencesSlice((() => {}) as any, (() => {}) as any, (() => {}) as any).preferences,
        layout: createLayoutSlice((() => {}) as any, (() => {}) as any, (() => {}) as any).layout,
        notifications: createNotificationSlice((() => {}) as any, (() => {}) as any, (() => {}) as any).notifications,
        modals: createNotificationSlice((() => {}) as any, (() => {}) as any, (() => {}) as any).modals,
      })
    },
    exportState: () => JSON.stringify(useAppStore.getState(), null, 2),
  }
}

// Initialize store on client side
if (typeof window !== 'undefined') {
  const store = useAppStore.getState()
  
  // Initialize auth
  store.initializeAuth()
  
  // Load initial data
  store.loadConversations()
  
  // Setup periodic maintenance
  setInterval(() => {
    const state = useAppStore.getState()
    
    // Clean up expired toasts
    const expiredToasts = state.notifications.toasts.filter(
      toast => !toast.persistent && toast.duration && 
      Date.now() - new Date(toast.createdAt).getTime() > toast.duration
    )
    expiredToasts.forEach(toast => state.removeToast(toast.id))
    
    // Check session timeout
    if (state.auth.isAuthenticated && state.checkSessionTimeout()) {
      console.warn('Session timed out')
      state.logout()
    }
    
    // Clean up old error history (keep last 5)
    if (state.error.history.length > 5) {
      state.clearErrorHistory()
    }
  }, 30000) // Every 30 seconds
  
  // Auto-extend session on user activity
  const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart']
  const handleActivity = () => {
    const state = useAppStore.getState()
    if (state.auth.isAuthenticated) {
      state.extendSession()
    }
  }
  
  activityEvents.forEach(event => {
    document.addEventListener(event, handleActivity, { passive: true })
  })
}

// Type-safe store access
export type AppStore = typeof useAppStore
export type AppStoreActions = AppStoreState
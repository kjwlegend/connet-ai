import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { env } from '@/lib/config/env'

// Import slice creators
import createPreferencesSlice from './slices/ui/preferencesSlice'
import createLayoutSlice from './slices/ui/layoutSlice'
import createNotificationSlice from './slices/ui/notificationSlice'
import createConversationSlice from './slices/chat/conversationSlice'

// Import utilities
import { PERSIST_CONFIGS, STORAGE_CATEGORIES } from './utils/persistence'
import { logger } from './middleware/logger'

// Import types
import { UIState } from './types/ui'
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
export interface AppStoreState extends UIState {
  // Chat slices will be added here
  conversations: ConversationSlice
}

// Create the main store with enhanced middleware
const useAppStore = create<AppStoreState>()(
  devtools(
    logger(
      subscribeWithSelector(
        (...args) => ({
          // UI slices - with different persistence strategies
          ...createPreferencesSlice(...args),
          ...createLayoutSlice(...args),
          ...createNotificationSlice(...args),
          
          // Chat slices - with cache-based persistence
          ...createConversationSlice(...args),
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
const createUIPreferencesStore = () => create<AppStoreState>()(
  persist(
    devtools(
      (...args) => ({
        ...createPreferencesSlice(...args),
        ...createLayoutSlice(...args),
        ...createNotificationSlice(...args),
        ...createConversationSlice(...args),
      }),
      { name: 'ui-preferences' }
    ),
    PERSIST_CONFIGS.UI_PREFERENCES<AppStoreState>('ui-preferences')
  )
)

const createLayoutStore = () => create<AppStoreState>()(
  persist(
    devtools(
      (...args) => ({
        ...createPreferencesSlice(...args),
        ...createLayoutSlice(...args),
        ...createNotificationSlice(...args),
        ...createConversationSlice(...args),
      }),
      { name: 'layout-state' }
    ),
    PERSIST_CONFIGS.LAYOUT_STATE<AppStoreState>('layout-state')
  )
)

const createChatCacheStore = () => create<AppStoreState>()(
  persist(
    devtools(
      (...args) => ({
        ...createPreferencesSlice(...args),
        ...createLayoutSlice(...args),
        ...createNotificationSlice(...args),
        ...createConversationSlice(...args),
      }),
      { name: 'chat-cache' }
    ),
    PERSIST_CONFIGS.CHAT_CACHE<AppStoreState>('chat-cache', ['conversations'])
  )
)

export default useAppStore

// Export specialized store hooks with optimized selectors
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
    error: state.error,
    loadConversations: state.loadConversations,
    createConversation: state.createConversation,
    setActiveConversation: state.setActiveConversation,
    pinConversation: state.pinConversation,
    archiveConversation: state.archiveConversation,
    exportConversation: state.exportConversation,
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
  // Load initial data
  useAppStore.getState().loadConversations()
  
  // Setup periodic cache cleanup
  setInterval(() => {
    const state = useAppStore.getState()
    // Clean up expired toasts
    const expiredToasts = state.notifications.toasts.filter(
      toast => !toast.persistent && toast.duration && 
      Date.now() - new Date(toast.createdAt).getTime() > toast.duration
    )
    expiredToasts.forEach(toast => state.removeToast(toast.id))
  }, 30000) // Every 30 seconds
}

// Type-safe store access
export type AppStore = typeof useAppStore
export type AppStoreActions = AppStoreState
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { env } from '@/lib/config/env'

// Import slice creators
import createAuthSlice from './slices/auth/authSlice'
import createPreferencesSlice from './slices/ui/preferencesSlice'
import createLayoutSlice from './slices/ui/layoutSlice'
import createNotificationSlice from './slices/ui/notificationSlice'
import createConversationSlice from './slices/chat/conversationSlice'
import createAgentsSlice from './slices/agents/agentsSlice'
import createContactsSlice from './slices/contacts/contactsSlice'

// Import utilities
import { PERSIST_CONFIGS, STORAGE_CATEGORIES } from './utils/persistence'
import { logger } from './middleware/logger'

// Import types
import { AuthSlice } from './slices/auth/authSlice'
import { PreferencesSlice } from './slices/ui/preferencesSlice'
import { LayoutSlice } from './slices/ui/layoutSlice'
import { NotificationSlice } from './slices/ui/notificationSlice'
import { ConversationSlice } from './slices/chat/conversationSlice'
import { AgentsSlice } from './slices/agents/agentsSlice'
import { ContactsSlice } from './slices/contacts/contactsSlice'

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
  ConversationSlice,
  AgentsSlice,
  ContactsSlice {}

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
          
          // Data slices - for managing external data
          ...createAgentsSlice(set, get, store),
          ...createContactsSlice(set, get, store),
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

// Note: Specialized stores removed - using single store architecture for better performance

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
  // Use separate selectors to prevent object creation on every render
  const preferences = useAppStore((state) => state.preferences)
  const setTheme = useAppStore((state) => state.setTheme)
  const setLanguage = useAppStore((state) => state.setLanguage)
  const updatePreferences = useAppStore((state) => state.updatePreferences)
  const resetPreferences = useAppStore((state) => state.resetPreferences)
  
  return {
    preferences,
    setTheme,
    setLanguage,
    updatePreferences,
    resetPreferences,
  }
}

export const useLayout = () => {
  // Use separate selectors to prevent object creation on every render
  const layout = useAppStore((state) => state.layout)
  const navigation = useAppStore((state) => state.navigation)
  const toggleSidebar = useAppStore((state) => state.toggleSidebar)
  const setSidebarCollapsed = useAppStore((state) => state.setSidebarCollapsed)
  const setMiddlePanelWidth = useAppStore((state) => state.setMiddlePanelWidth)
  const setCurrentNavigation = useAppStore((state) => state.setCurrentNavigation)
  const navigateTo = useAppStore((state) => state.navigateTo)
  const applyLayoutPreset = useAppStore((state) => state.applyLayoutPreset)
  
  return {
    layout,
    navigation,
    toggleSidebar,
    setSidebarCollapsed,
    setMiddlePanelWidth,
    setCurrentNavigation,
    navigateTo,
    applyLayoutPreset,
  }
}

export const useNotifications = () => {
  // Use separate selectors to prevent object creation on every render
  const notifications = useAppStore((state) => state.notifications)
  const modals = useAppStore((state) => state.modals)
  const showToast = useAppStore((state) => state.showToast)
  const removeToast = useAppStore((state) => state.removeToast)
  const clearToasts = useAppStore((state) => state.clearToasts)
  const openModal = useAppStore((state) => state.openModal)
  const closeModal = useAppStore((state) => state.closeModal)
  const closeAllModals = useAppStore((state) => state.closeAllModals)
  
  return {
    notifications,
    modals,
    showToast,
    removeToast,
    clearToasts,
    openModal,
    closeModal,
    closeAllModals,
  }
}

export const useConversations = () => {
  // Use separate selectors to prevent object creation on every render
  const conversations = useAppStore((state) => state.conversations)
  const activeConversationId = useAppStore((state) => state.activeConversationId)
  const isLoading = useAppStore((state) => state.isLoading)
  const conversationError = useAppStore((state) => state.conversationError)
  const loadConversations = useAppStore((state) => state.loadConversations)
  const createConversation = useAppStore((state) => state.createConversation)
  const setActiveConversation = useAppStore((state) => state.setActiveConversation)
  const pinConversation = useAppStore((state) => state.pinConversation)
  const archiveConversation = useAppStore((state) => state.archiveConversation)
  const exportConversation = useAppStore((state) => state.exportConversation)
  const setConversationError = useAppStore((state) => state.setConversationError)
  const clearConversationError = useAppStore((state) => state.clearConversationError)
  
  return {
    conversations,
    activeConversationId,
    isLoading,
    conversationError,
    loadConversations,
    createConversation,
    setActiveConversation,
    pinConversation,
    archiveConversation,
    exportConversation,
    setConversationError,
    clearConversationError,
  }
}

export const useAgents = () => {
  // Use separate selectors for data and actions to prevent infinite loops
  const agents = useAppStore((state) => state.agents)
  const currentAgent = useAppStore((state) => state.currentAgent)
  const agentVersions = useAppStore((state) => state.agentVersions)
  const pagination = useAppStore((state) => state.agentsPagination)
  const filters = useAppStore((state) => state.agentsFilters)
  const ui = useAppStore((state) => state.agentsUI)
  const error = useAppStore((state) => state.agentsError)
  
  // Get actions with stable selectors
  const setAgents = useAppStore((state) => state.setAgents)
  const addAgent = useAppStore((state) => state.addAgent)
  const updateAgentInList = useAppStore((state) => state.updateAgentInList)
  const removeAgent = useAppStore((state) => state.removeAgent)
  const setCurrentAgent = useAppStore((state) => state.setCurrentAgent)
  const setAgentVersions = useAppStore((state) => state.setAgentVersions)
  const setLoading = useAppStore((state) => state.setLoading)
  const setCreating = useAppStore((state) => state.setCreating)
  const setUpdating = useAppStore((state) => state.setUpdating)
  const setDeleting = useAppStore((state) => state.setDeleting)
  const setDeploying = useAppStore((state) => state.setDeploying)
  const toggleCreateModal = useAppStore((state) => state.toggleCreateModal)
  const toggleEditModal = useAppStore((state) => state.toggleEditModal)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
  const clearErrorHistory = useAppStore((state) => state.clearErrorHistory)
  const setFilters = useAppStore((state) => state.setAgentsFilters)
  const clearFilters = useAppStore((state) => state.clearAgentsFilters)
  const setPagination = useAppStore((state) => state.setAgentsPagination)
  const createAgent = useAppStore((state) => state.createAgent)
  const listAgents = useAppStore((state) => state.listAgents)
  const getAgent = useAppStore((state) => state.getAgent)
  const updateAgent = useAppStore((state) => state.updateAgent)
  const deleteAgent = useAppStore((state) => state.deleteAgent)
  const deployAgent = useAppStore((state) => state.deployAgent)
  const getAgentVersions = useAppStore((state) => state.getAgentVersions)
  const rollbackAgent = useAppStore((state) => state.rollbackAgent)
  const refreshAgents = useAppStore((state) => state.refreshAgents)
  const searchAgents = useAppStore((state) => state.searchAgents)
  const loadMoreAgents = useAppStore((state) => state.loadMoreAgents)
  
  return {
    // Data
    agents,
    currentAgent,
    agentVersions,
    pagination,
    filters,
    ui,
    error,
    
    // Data actions
    setAgents,
    addAgent,
    updateAgentInList,
    removeAgent,
    setCurrentAgent,
    setAgentVersions,
    
    // UI actions
    setLoading,
    setCreating,
    setUpdating,
    setDeleting,
    setDeploying,
    toggleCreateModal,
    toggleEditModal,
    
    // Error actions
    setError,
    clearError,
    clearErrorHistory,
    
    // Filter actions
    setFilters,
    clearFilters,
    setPagination,
    
    // API operations
    createAgent,
    listAgents,
    getAgent,
    updateAgent,
    deleteAgent,
    deployAgent,
    getAgentVersions,
    rollbackAgent,
    
    // Utility operations
    refreshAgents,
    searchAgents,
    loadMoreAgents,
  }
}

export const useContacts = () => {
  // Use separate selectors for data and actions to prevent infinite loops
  const contacts = useAppStore((state) => state.contacts)
  const searchResults = useAppStore((state) => state.searchResults)
  const currentContact = useAppStore((state) => state.currentContact)
  const contactKnowledge = useAppStore((state) => state.contactKnowledge)
  const contactTools = useAppStore((state) => state.contactTools)
  const pagination = useAppStore((state) => state.contactsPagination)
  const filters = useAppStore((state) => state.contactsFilters)
  const ui = useAppStore((state) => state.contactsUI)
  const error = useAppStore((state) => state.contactsError)
  
  // Get actions with stable selectors
  const setContacts = useAppStore((state) => state.setContacts)
  const addContact = useAppStore((state) => state.addContact)
  const updateContactInList = useAppStore((state) => state.updateContactInList)
  const removeContact = useAppStore((state) => state.removeContact)
  const setCurrentContact = useAppStore((state) => state.setCurrentContact)
  const setSearchResults = useAppStore((state) => state.setSearchResults)
  const setContactKnowledge = useAppStore((state) => state.setContactKnowledge)
  const setContactTools = useAppStore((state) => state.setContactTools)
  const setLoading = useAppStore((state) => state.setLoading)
  const setSearching = useAppStore((state) => state.setSearching)
  const setCreating = useAppStore((state) => state.setCreating)
  const setUpdating = useAppStore((state) => state.setUpdating)
  const setDeleting = useAppStore((state) => state.setDeleting)
  const toggleAddModal = useAppStore((state) => state.toggleAddModal)
  const toggleEditModal = useAppStore((state) => state.toggleEditModal)
  const toggleSearchModal = useAppStore((state) => state.toggleSearchModal)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
  const clearErrorHistory = useAppStore((state) => state.clearErrorHistory)
  const setFilters = useAppStore((state) => state.setContactsFilters)
  const clearFilters = useAppStore((state) => state.clearContactsFilters)
  const setPagination = useAppStore((state) => state.setContactsPagination)
  const createContact = useAppStore((state) => state.createContact)
  const getUserContacts = useAppStore((state) => state.getUserContacts)
  const searchContacts = useAppStore((state) => state.searchContacts)
  const getContact = useAppStore((state) => state.getContact)
  const updateContact = useAppStore((state) => state.updateContact)
  const deleteContact = useAppStore((state) => state.deleteContact)
  const toggleFavorite = useAppStore((state) => state.toggleFavorite)
  const addKnowledgeToContact = useAppStore((state) => state.addKnowledgeToContact)
  const removeKnowledgeFromContact = useAppStore((state) => state.removeKnowledgeFromContact)
  const getContactKnowledgeBases = useAppStore((state) => state.getContactKnowledgeBases)
  const addToolToContact = useAppStore((state) => state.addToolToContact)
  const removeToolFromContact = useAppStore((state) => state.removeToolFromContact)
  const getContactTools = useAppStore((state) => state.getContactTools)
  const updateContactToolConfig = useAppStore((state) => state.updateContactToolConfig)
  const refreshContacts = useAppStore((state) => state.refreshContacts)
  const loadMoreContacts = useAppStore((state) => state.loadMoreContacts)
  const clearSearchResults = useAppStore((state) => state.clearSearchResults)
  
  return {
    // Data
    contacts,
    searchResults,
    currentContact,
    contactKnowledge,
    contactTools,
    pagination,
    filters,
    ui,
    error,
    
    // Data actions
    setContacts,
    addContact,
    updateContactInList,
    removeContact,
    setCurrentContact,
    setSearchResults,
    setContactKnowledge,
    setContactTools,
    
    // UI actions
    setLoading,
    setSearching,
    setCreating,
    setUpdating,
    setDeleting,
    toggleAddModal,
    toggleEditModal,
    toggleSearchModal,
    
    // Error actions
    setError,
    clearError,
    clearErrorHistory,
    
    // Filter actions
    setFilters,
    clearFilters,
    setPagination,
    
    // API operations - Contact Management
    createContact,
    getUserContacts,
    searchContacts,
    getContact,
    updateContact,
    deleteContact,
    toggleFavorite,
    
    // API operations - Knowledge Management
    addKnowledgeToContact,
    removeKnowledgeFromContact,
    getContactKnowledgeBases,
    
    // API operations - Tool Management
    addToolToContact,
    removeToolFromContact,
    getContactTools,
    updateContactToolConfig,
    
    // Utility operations
    refreshContacts,
    loadMoreContacts,
    clearSearchResults,
  }
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

// Performance monitoring hook - Fixed infinite loop by using stable selectors
export const useStoreStats = () => {
  // Use separate selectors to prevent object creation on every render
  const stateSize = useAppStore((state) => JSON.stringify(state).length)
  const conversationsCount = useAppStore((state) => state.conversations.data.length)
  const toastsCount = useAppStore((state) => state.notifications.toasts.length)
  const modalsCount = useAppStore((state) => state.modals.modals.length)
  const conversationsTimestamp = useAppStore((state) => state.conversations.timestamp)
  const conversationsTtl = useAppStore((state) => state.conversations.ttl)
  
  // Calculate derived values
  const conversationsValid = conversationsTimestamp + conversationsTtl > Date.now()
  const conversationsAge = Date.now() - conversationsTimestamp
  
  return {
    stateSize,
    counts: {
      conversations: conversationsCount,
      toasts: toastsCount,
      modals: modalsCount,
    },
    cacheStatus: {
      conversationsValid,
      conversationsAge,
    },
  }
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
      // Reset to initial state - simplified to avoid function call issues
      if (typeof window !== 'undefined') {
        localStorage.clear()
        window.location.reload()
      }
    },
    exportState: () => JSON.stringify(useAppStore.getState(), null, 2),
  }
}

// Initialize store on client side with proper cleanup
if (typeof window !== 'undefined') {
  const store = useAppStore.getState()
  
  // Initialize auth
  store.initializeAuth()
  
  // Load initial data
  store.loadConversations()
  
  // Setup periodic maintenance with cleanup
  const maintenanceInterval = setInterval(() => {
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
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    clearInterval(maintenanceInterval)
    activityEvents.forEach(event => {
      document.removeEventListener(event, handleActivity)
    })
  })
}

// Type-safe store access
export type AppStore = typeof useAppStore
export type AppStoreActions = AppStoreState
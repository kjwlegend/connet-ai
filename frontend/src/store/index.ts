/**
 * 简化的 Store 架构
 * 只负责状态管理，业务逻辑已移至 /hooks/business/
 * 
 * @version 2.0.0 - 重构后的新架构，UI属性命名空间化
 * @changelog
 * - v2.0.0 (2025-01-23): 重构架构分离业务逻辑，修复UI属性冲突，添加版本管理
 * - v1.0.0 (2024-12-01): 初始版本，包含业务逻辑的完整store
 */

import { create } from 'zustand'
import { devtools, subscribeWithSelector } from 'zustand/middleware'
import { persist } from './middleware/persist'
import { PERSIST_CONFIGS } from './utils/persistence'
import { env } from '@/lib/config/env'

// Store版本管理
export const STORE_VERSION = '2.0.0'
export const STORE_VERSION_KEY = 'connet-ai-store-version'

// 版本兼容性检查
export const checkStoreVersion = () => {
  if (typeof window === 'undefined') return true // SSR环境跳过检查
  
  const storedVersion = localStorage.getItem(STORE_VERSION_KEY)
  
  if (!storedVersion) {
    // 首次使用，保存当前版本
    localStorage.setItem(STORE_VERSION_KEY, STORE_VERSION)
    return true
  }
  
  if (storedVersion !== STORE_VERSION) {
    console.warn(`Store version mismatch. Current: ${STORE_VERSION}, Stored: ${storedVersion}`)
    
    // 这里可以添加版本迁移逻辑
    if (shouldClearStoreOnVersionMismatch(storedVersion, STORE_VERSION)) {
      console.warn('Clearing store due to version incompatibility')
      clearStorageForNewVersion()
    }
    
    // 更新版本标记
    localStorage.setItem(STORE_VERSION_KEY, STORE_VERSION)
  }
  
  return true
}

// 判断是否需要清空store（版本不兼容时）
const shouldClearStoreOnVersionMismatch = (oldVersion: string, newVersion: string): boolean => {
  // 主版本号变更时清空store
  const oldMajor = parseInt(oldVersion.split('.')[0])
  const newMajor = parseInt(newVersion.split('.')[0])
  
  return oldMajor !== newMajor
}

// 清空存储（用于版本不兼容时）
const clearStorageForNewVersion = () => {
  // 清空Zustand持久化的数据
  localStorage.removeItem('connet-ai-store')
  
  // 可以保留用户偏好等重要数据
  // const userPreferences = localStorage.getItem('user-preferences')
  // 清空后可以恢复：
  // if (userPreferences) localStorage.setItem('user-preferences', userPreferences)
}

// Import slice creators
import createAuthSlice from './slices/auth/authSlice'
import createPreferencesSlice from './slices/ui/preferencesSlice'
import createLayoutSlice from './slices/ui/layoutSlice'
import createNotificationSlice from './slices/ui/notificationSlice'
import createConversationSlice from './slices/chat/conversationSlice'
import createAgentsSlice from './slices/agents/agentsSlice'
import createContactsSlice from './slices/contacts/contactsSlice'

// Import types
import { AuthSlice } from './slices/auth/authSlice'
import { PreferencesSlice } from './slices/ui/preferencesSlice'
import { LayoutSlice } from './slices/ui/layoutSlice'
import { NotificationSlice } from './slices/ui/notificationSlice'
import { ConversationSlice } from './slices/chat/conversationSlice'
import { AgentsSlice } from './slices/agents/agentsSlice'
import { ContactsSlice } from './slices/contacts/contactsSlice'

// Combined store state type
export interface AppStoreState extends 
  AuthSlice, 
  PreferencesSlice, 
  LayoutSlice, 
  NotificationSlice, 
  ConversationSlice,
  AgentsSlice,
  ContactsSlice {
  // Store元数据
  version: string
}

// Create the main store
const useAppStore = create<AppStoreState>()(
  devtools(
    persist(
      subscribeWithSelector(
        (set, get, store) => {
          // 执行版本兼容性检查
          checkStoreVersion()
          
          return {
            // Store版本信息
            version: STORE_VERSION,
            
            // Auth slice
            ...createAuthSlice(set, get, store),
            
            // UI slices
            ...createPreferencesSlice(set, get, store),
            ...createLayoutSlice(set, get, store),
            ...createNotificationSlice(set, get, store),
            
            // Chat slices
            ...createConversationSlice(set, get, store),
            
            // Data slices
            ...createAgentsSlice(set, get, store),
            ...createContactsSlice(set, get, store),
          }
        }
      ),
      // 持久化配置 - 选择性存储重要数据
      {
        name: 'connet-ai-store',
        ...PERSIST_CONFIGS.UI_PREFERENCES<AppStoreState>('connet-ai-store'),
        partialize: (state) => ({
          // 持久化认证信息
          auth: {
            user: state.auth.user,
            token: state.auth.token,
            refreshToken: state.auth.refreshToken,
            isAuthenticated: state.auth.isAuthenticated,
            sessionStarted: state.auth.sessionStarted,
            // 不持久化 lastActivity，每次启动时重新设置
          },
          // 持久化用户偏好设置
          preferences: state.preferences,
          // 持久化布局设置
          layout: {
            ...state.layout,
            // 不持久化临时状态
            isLoading: false,
          },
          // 其他需要持久化的状态...
        }),
        version: parseFloat(STORE_VERSION),
      }
    ),
    {
      name: 'connet-ai-store-devtools',
      enabled: env.ENABLE_DEBUG,
      version: parseFloat(STORE_VERSION),
    }
  )
)

export default useAppStore

// Export simple store hooks - 只提供基础的状态访问器
// 复杂的业务逻辑使用 /hooks/business/ 中的 hooks

export const useAuth = () => {
  const auth = useAppStore((state) => state.auth)
  const authUI = useAppStore((state) => state.authUI)
  const error = useAppStore((state) => state.error)
  
  // 只导出基础的状态操作，不包含复杂业务逻辑
  const login = useAppStore((state) => state.login)
  const logout = useAppStore((state) => state.logout)
  const setUser = useAppStore((state) => state.setUser)
  const setToken = useAppStore((state) => state.setToken)
  const setRefreshToken = useAppStore((state) => state.setRefreshToken)
  const setLoading = useAppStore((state) => state.setLoading)
  const setInitializing = useAppStore((state) => state.setInitializing)
  const toggleLoginModal = useAppStore((state) => state.toggleLoginModal)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
  const updateUserPreferences = useAppStore((state) => state.updateUserPreferences)
  const extendSession = useAppStore((state) => state.extendSession)
  const checkSessionTimeout = useAppStore((state) => state.checkSessionTimeout)
  const resetSession = useAppStore((state) => state.resetSession)
  const initializeAuth = useAppStore((state) => state.initializeAuth)
  const validateToken = useAppStore((state) => state.validateToken)
  const refreshAuthToken = useAppStore((state) => state.refreshAuthToken)
  const getCurrentUser = useAppStore((state) => state.getCurrentUser)
  
  return {
    auth,
    ui: authUI, // 为了向后兼容，添加 ui 别名
    authUI,
    error,
    login,
    logout,
    setUser,
    setToken,
    setRefreshToken,
    setLoading,
    setInitializing,
    toggleLoginModal,
    setError,
    clearError,
    updateUserPreferences,
    extendSession,
    checkSessionTimeout,
    resetSession,
    initializeAuth,
    validateToken,
    refreshAuthToken,
    getCurrentUser,
  }
}

export const useUIPreferences = () => {
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
  const layout = useAppStore((state) => state.layout)
  const navigation = useAppStore((state) => state.navigation)
  const toggleSidebar = useAppStore((state) => state.toggleSidebar)
  const setSidebarCollapsed = useAppStore((state) => state.setSidebarCollapsed)
  const setMiddlePanelWidth = useAppStore((state) => state.setMiddlePanelWidth)
  const setCurrentNavigation = useAppStore((state) => state.setCurrentNavigation)
  const navigateTo = useAppStore((state) => state.navigateTo)
  
  return {
    layout,
    navigation,
    toggleSidebar,
    setSidebarCollapsed,
    setMiddlePanelWidth,
    setCurrentNavigation,
    navigateTo,
  }
}

export const useNotifications = () => {
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
  const conversations = useAppStore((state) => state.conversations)
  const activeConversationId = useAppStore((state) => state.activeConversationId)
  const isLoading = useAppStore((state) => state.isLoading)
  const conversationError = useAppStore((state) => state.conversationError)
  const setActiveConversation = useAppStore((state) => state.setActiveConversation)
  
  return {
    conversations,
    activeConversationId,
    isLoading,
    conversationError,
    setActiveConversation,
  }
}

export const useAgents = () => {
  const agents = useAppStore((state) => state.agents)
  const currentAgent = useAppStore((state) => state.currentAgent)
  const agentVersions = useAppStore((state) => state.agentVersions)
  const ui = useAppStore((state) => state.agentsUI)
  const error = useAppStore((state) => state.agentsError)
  const pagination = useAppStore((state) => state.agentsPagination)
  const filters = useAppStore((state) => state.agentsFilters)
  
  // 基础状态操作
  const setAgents = useAppStore((state) => state.setAgents)
  const addAgent = useAppStore((state) => state.addAgent)
  const updateAgentInList = useAppStore((state) => state.updateAgentInList)
  const setCurrentAgent = useAppStore((state) => state.setCurrentAgent)
  const setLoading = useAppStore((state) => state.setLoading)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
  const setAgentsFilters = useAppStore((state) => state.setAgentsFilters)
  
  return {
    agents,
    currentAgent,
    agentVersions,
    ui,
    error,
    pagination,
    filters,
    setAgents,
    addAgent,
    updateAgentInList,
    setCurrentAgent,
    setLoading,
    setError,
    clearError,
    setAgentsFilters,
  }
}

export const useContacts = () => {
  const data = useAppStore((state) => state.data)
  const contactsUI = useAppStore((state) => state.contactsUI)
  const error = useAppStore((state) => state.error)
  const contactsFilters = useAppStore((state) => state.contactsFilters)
  const pagination = useAppStore((state) => state.pagination)
  
  // 基础状态操作
  const setContacts = useAppStore((state) => state.setContacts)
  const addContact = useAppStore((state) => state.addContact)
  const updateContactInList = useAppStore((state) => state.updateContactInList)
  const removeContactFromList = useAppStore((state) => state.removeContactFromList)
  const setCurrentContact = useAppStore((state) => state.setCurrentContact)
  const setSearchResults = useAppStore((state) => state.setSearchResults)
  const setContactKnowledge = useAppStore((state) => state.setContactKnowledge)
  const setContactTools = useAppStore((state) => state.setContactTools)
  const clearSearchResults = useAppStore((state) => state.clearSearchResults)
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
  const setFilters = useAppStore((state) => state.setFilters)
  const clearFilters = useAppStore((state) => state.clearFilters)
  const setPagination = useAppStore((state) => state.setPagination)
  const resetPagination = useAppStore((state) => state.resetPagination)
  const clearAllData = useAppStore((state) => state.clearAllData)
  
  return {
    contacts: data.contacts,
    searchResults: data.searchResults,
    currentContact: data.currentContact,
    contactKnowledge: data.contactKnowledge,
    contactTools: data.contactTools,
    contactsUI,
    error,
    contactsFilters,
    pagination,
    setContacts,
    addContact,
    updateContactInList,
    removeContactFromList,
    setCurrentContact,
    setSearchResults,
    setContactKnowledge,
    setContactTools,
    clearSearchResults,
    setLoading,
    setSearching,
    setCreating,
    setUpdating,
    setDeleting,
    toggleAddModal,
    toggleEditModal,
    toggleSearchModal,
    setError,
    clearError,
    setFilters,
    clearFilters,
    setPagination,
    resetPagination,
    clearAllData,
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

// Export store version utilities
export const useStoreVersion = () => {
  const version = useAppStore((state) => state.version)
  return {
    version,
    checkVersion: checkStoreVersion,
    STORE_VERSION,
  }
}

// Export store types
export type AppStore = typeof useAppStore
export type AppStoreActions = AppStoreState
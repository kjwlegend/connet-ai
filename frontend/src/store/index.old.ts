import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { logger } from './middleware/logger'
import { env } from '@/lib/config/env'
import { useHydration } from './middleware/hydration'
import { useMemo, useCallback } from 'react'

import createAuthSlice from './slices/authSlice'
import createUISlice from './slices/uiSlice'
import createChatSlice from './slices/chatSlice'
import { StoreState } from './types'

// Create store without persistence for now to avoid hydration issues
const useAppStore = create<StoreState>()(
  devtools(
    logger(
      (...a) => ({
        ...createAuthSlice(...a),
        ...createUISlice(...a),
        ...createChatSlice(...a),
      }),
      'AppStore'
    ),
    {
      name: 'connet-ai-devtools',
      enabled: env.ENABLE_DEBUG,
    }
  )
)

export default useAppStore

// Create stable selectors to avoid infinite loops
const uiSelector = (state: StoreState) => ({
  theme: state.theme,
  sidebarCollapsed: state.sidebarCollapsed,
  currentNavigation: state.currentNavigation,
  modals: state.modals,
  toasts: state.toasts,
  setTheme: state.setTheme,
  toggleSidebar: state.toggleSidebar,
  setCurrentNavigation: state.setCurrentNavigation,
  showToast: state.showToast,
  openModal: state.openModal,
  closeModal: state.closeModal,
})

const chatSelector = (state: StoreState) => ({
  conversations: state.conversations,
  activeConversationId: state.activeConversationId,
  messages: state.messages,
  isLoading: state.isLoading,
  isSending: state.isSending,
  error: state.error,
  draft: state.draft,
  mentionSuggestions: state.mentionSuggestions,
  showMentionSuggestions: state.showMentionSuggestions,
  setActiveConversation: state.setActiveConversation,
  addConversation: state.addConversation,
  loadConversations: state.loadConversations,
  sendMessage: state.sendMessage,
  addMessage: state.addMessage,
  loadMessages: state.loadMessages,
  setDraft: state.setDraft,
  clearDraft: state.clearDraft,
  setError: state.setError,
  clearError: state.clearError,
})

// Export store actions for easier access with proper hydration handling
export const useAuth = () => {
  const hydrated = useHydration()
  
  // Use individual selectors to avoid object recreation
  const user = useAppStore((state) => state.user)
  const token = useAppStore((state) => state.token)
  const refreshToken = useAppStore((state) => state.refreshToken)
  const isAuthenticated = useAppStore((state) => state.isAuthenticated)
  const isLoading = useAppStore((state) => state.isLoading)
  const error = useAppStore((state) => state.error)
  
  // Actions (these are stable references from zustand)
  const login = useAppStore((state) => state.login)
  const logout = useAppStore((state) => state.logout)
  const setUser = useAppStore((state) => state.setUser)
  const setLoading = useAppStore((state) => state.setLoading)
  const setError = useAppStore((state) => state.setError)
  const clearError = useAppStore((state) => state.clearError)
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
  
  // Return memoized object to prevent unnecessary re-renders
  return useMemo(() => {
    if (!hydrated) {
      return {
        user: null,
        token: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        login: () => {},
        logout: async () => {},
        setUser: () => {},
        setLoading: () => {},
        setError: () => {},
        clearError: () => {},
        updateUserPreferences: () => {},
        initializeAuth: async () => {},
        loginWithCredentials: async () => {},
        registerWithCredentials: async () => ({ user: null as any, message: '' }),
        validateToken: async () => false,
        refreshAuthToken: async () => false,
        getCurrentUser: async () => {},
        getOAuthUrl: async () => ({ url: '', state: '' }),
        handleOAuthCallback: async () => {},
        loginWithOAuth: async () => {},
      }
    }
    
    return {
      user,
      token,
      refreshToken,
      isAuthenticated,
      isLoading,
      error,
      login,
      logout,
      setUser,
      setLoading,
      setError,
      clearError,
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
    }
  }, [
    hydrated,
    user,
    token,
    refreshToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    setUser,
    setLoading,
    setError,
    clearError,
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
  ])
}

export const useUI = () => {
  const hydrated = useHydration()
  const state = useAppStore(uiSelector)
  
  return useMemo(() => {
    if (!hydrated) {
      return {
        theme: 'system' as const,
        sidebarCollapsed: false,
        currentNavigation: 'chat' as const,
        modals: {},
        toasts: [],
        setTheme: () => {},
        toggleSidebar: () => {},
        setCurrentNavigation: () => {},
        showToast: () => {},
        openModal: () => {},
        closeModal: () => {},
      }
    }
    return state
  }, [hydrated, state])
}

export const useChat = () => {
  const hydrated = useHydration()
  
  // Get stable references to the functions
  const conversations = useAppStore(state => state.conversations)
  const activeConversationId = useAppStore(state => state.activeConversationId)
  const messages = useAppStore(state => state.messages)
  const isLoading = useAppStore(state => state.isLoading)
  const isSending = useAppStore(state => state.isSending)
  const error = useAppStore(state => state.error)
  const draft = useAppStore(state => state.draft)
  const mentionSuggestions = useAppStore(state => state.mentionSuggestions)
  const showMentionSuggestions = useAppStore(state => state.showMentionSuggestions)
  
  // Create stable function references
  const setActiveConversation = useCallback((id: string) => {
    useAppStore.getState().setActiveConversation(id)
  }, [])
  
  const addConversation = useCallback((conversation: any) => {
    useAppStore.getState().addConversation(conversation)
  }, [])
  
  const createNewConversation = useCallback(async (agentId: string, agentName: string, title?: string) => {
    return await useAppStore.getState().createNewConversation(agentId, agentName, title)
  }, [])
  
  const loadConversations = useCallback(async () => {
    await useAppStore.getState().loadConversations()
  }, [])
  
  const sendMessage = useCallback(async (conversationId: string, content: string, mentions?: string[]) => {
    await useAppStore.getState().sendMessage(conversationId, content, mentions)
  }, [])
  
  const addMessage = useCallback((message: any) => {
    useAppStore.getState().addMessage(message)
  }, [])
  
  const loadMessages = useCallback(async (conversationId: string) => {
    await useAppStore.getState().loadMessages(conversationId)
  }, [])
  
  const setDraft = useCallback((draft: string) => {
    useAppStore.getState().setDraft(draft)
  }, [])
  
  const clearDraft = useCallback(() => {
    useAppStore.getState().clearDraft()
  }, [])
  
  const setError = useCallback((error: string | null) => {
    useAppStore.getState().setError(error)
  }, [])
  
  const clearError = useCallback(() => {
    useAppStore.getState().clearError()
  }, [])

  const pinConversation = useCallback((conversationId: string) => {
    useAppStore.getState().pinConversation(conversationId)
  }, [])

  const unpinConversation = useCallback((conversationId: string) => {
    useAppStore.getState().unpinConversation(conversationId)
  }, [])

  const exportConversation = useCallback(async (conversationId: string) => {
    return await useAppStore.getState().exportConversation(conversationId)
  }, [])

  const deleteConversation = useCallback((conversationId: string) => {
    useAppStore.getState().deleteConversation(conversationId)
  }, [])

  const addParticipantsToConversation = useCallback((conversationId: string, participantIds: string[]) => {
    useAppStore.getState().addParticipantsToConversation(conversationId, participantIds)
  }, [])
  
  return useMemo(() => {
    if (!hydrated) {
      return {
        conversations: [],
        activeConversationId: null,
        messages: {},
        isLoading: false,
        isSending: false,
        error: null,
        draft: '',
        mentionSuggestions: [],
        showMentionSuggestions: false,
        setActiveConversation: () => {},
        addConversation: () => {},
        createNewConversation: async () => '',
        loadConversations: async () => {},
        sendMessage: async () => {},
        addMessage: () => {},
        loadMessages: async () => {},
        setDraft: () => {},
        clearDraft: () => {},
        setError: () => {},
        clearError: () => {},
        pinConversation: () => {},
        unpinConversation: () => {},
        exportConversation: async () => '',
        deleteConversation: () => {},
        addParticipantsToConversation: () => {},
      }
    }
    
    return {
      conversations,
      activeConversationId,
      messages,
      isLoading,
      isSending,
      error,
      draft,
      mentionSuggestions,
      showMentionSuggestions,
      setActiveConversation,
      addConversation,
      createNewConversation,
      loadConversations,
      sendMessage,
      addMessage,
      loadMessages,
      setDraft,
      clearDraft,
      setError,
      clearError,
      pinConversation,
      unpinConversation,
      exportConversation,
      deleteConversation,
      addParticipantsToConversation,
    }
  }, [
    hydrated,
    conversations,
    activeConversationId,
    messages,
    isLoading,
    isSending,
    error,
    draft,
    mentionSuggestions,
    showMentionSuggestions,
    setActiveConversation,
    addConversation,
    loadConversations,
    sendMessage,
    addMessage,
    loadMessages,
    setDraft,
    clearDraft,
    setError,
    clearError,
    pinConversation,
    unpinConversation,
    exportConversation,
    deleteConversation,
    addParticipantsToConversation,
  ])
}

// Initialize auth after hydration
if (typeof window !== 'undefined') {
  useAppStore.getState().initializeAuth()
}

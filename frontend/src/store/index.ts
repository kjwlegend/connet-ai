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
const authSelector = (state: StoreState) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
  login: state.login,
  logout: state.logout,
  setUser: state.setUser,
})

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
  const state = useAppStore(authSelector)
  
  // Return default values during SSR to prevent hydration mismatch
  return useMemo(() => {
    if (!hydrated) {
      return {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        login: () => {},
        logout: async () => {},
        setUser: () => {},
      }
    }
    return state
  }, [hydrated, state])
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
  ])
}

// Initialize auth after hydration
if (typeof window !== 'undefined') {
  useAppStore.getState().initializeAuth()
}

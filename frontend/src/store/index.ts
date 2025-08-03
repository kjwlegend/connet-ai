import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { logger } from './middleware/logger'
import { env } from '@/lib/config/env'

import createAuthSlice from './slices/authSlice'
import createUISlice from './slices/uiSlice'
import { StoreState } from './types'

// Create store without persistence for now to avoid hydration issues
const useAppStore = create<StoreState>()(
  devtools(
    logger(
      (...a) => ({
        ...createAuthSlice(...a),
        ...createUISlice(...a),
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

// Export store actions for easier access with proper hydration handling
export const useAuth = () => {
  const state = useAppStore((state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login: state.login,
    logout: state.logout,
    setUser: state.setUser,
  }))
  
  return state
}

export const useUI = () => {
  const state = useAppStore((state) => ({
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
  }))
  
  return state
}

// Initialize auth after hydration
if (typeof window !== 'undefined') {
  useAppStore.getState().initializeAuth()
}

// TODO: Add chat selectors when chat slice is implemented
// export const useChat = () => useAppStore((state) => ({
//   conversations: state.conversations,
//   currentConversation: state.currentConversation,
//   messages: state.messages,
//   isTyping: state.isTyping,
//   sendMessage: state.sendMessage,
//   setCurrentConversation: state.setCurrentConversation,
// }))

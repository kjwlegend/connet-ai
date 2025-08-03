import { StateCreator } from 'zustand'
import { StoreState } from '../types'
import { StorageUtil } from '@/lib/utils/storage'
import { STORAGE_KEYS } from '@/lib/config/constants'

export interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  description?: string
  duration?: number
}

export interface Modal {
  id: string
  type: string
  props?: Record<string, any>
  isOpen: boolean
}

export interface UIState {
  // Layout
  sidebarCollapsed: boolean
  middlePanelWidth: number
  
  // Theme & Appearance
  theme: 'light' | 'dark' | 'system'
  
  // Modals & Overlays
  modals: Modal[]
  
  // Notifications
  toasts: Toast[]
  
  // Loading States
  globalLoading: boolean
  loadingStates: Record<string, boolean>
  
  // Navigation
  currentNavigation: string
  
  // Responsive
  isMobile: boolean
  isTablet: boolean
}

export interface UIActions {
  // Sidebar
  toggleSidebar: () => void
  setSidebarCollapsed: (collapsed: boolean) => void
  
  // Middle Panel
  setMiddlePanelWidth: (width: number) => void
  
  // Theme
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  
  // Modals
  openModal: (modal: Omit<Modal, 'isOpen'>) => void
  closeModal: (id: string) => void
  closeAllModals: () => void
  
  // Toasts
  showToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
  
  // Loading
  setGlobalLoading: (loading: boolean) => void
  setLoadingState: (key: string, loading: boolean) => void
  clearLoadingState: (key: string) => void
  
  // Navigation
  setCurrentNavigation: (nav: string) => void
  
  // Responsive
  setIsMobile: (isMobile: boolean) => void
  setIsTablet: (isTablet: boolean) => void
}

export type UISlice = UIState & UIActions

const createUISlice: StateCreator<StoreState, [], [], UISlice> = (set, get) => ({
  // State
  sidebarCollapsed: StorageUtil.getItem<boolean>(STORAGE_KEYS.SIDEBAR_COLLAPSED, false),
  middlePanelWidth: 350,
  theme: StorageUtil.getItem<'light' | 'dark' | 'system'>(STORAGE_KEYS.THEME, 'system'),
  modals: [],
  toasts: [],
  globalLoading: false,
  loadingStates: {},
  currentNavigation: 'chat',
  isMobile: false,
  isTablet: false,

  // Actions
  toggleSidebar: () => {
    const { sidebarCollapsed } = get()
    const newState = !sidebarCollapsed
    StorageUtil.setItem(STORAGE_KEYS.SIDEBAR_COLLAPSED, newState)
    set({ sidebarCollapsed: newState })
  },

  setSidebarCollapsed: (collapsed) => {
    StorageUtil.setItem(STORAGE_KEYS.SIDEBAR_COLLAPSED, collapsed)
    set({ sidebarCollapsed: collapsed })
  },

  setMiddlePanelWidth: (width) => {
    set({ middlePanelWidth: Math.max(300, Math.min(400, width)) })
  },

  setTheme: (theme) => {
    StorageUtil.setItem(STORAGE_KEYS.THEME, theme)
    set({ theme })
  },

  openModal: (modal) => {
    const { modals } = get()
    const newModal: Modal = { ...modal, isOpen: true }
    set({ modals: [...modals, newModal] })
  },

  closeModal: (id) => {
    const { modals } = get()
    set({ modals: modals.filter(modal => modal.id !== id) })
  },

  closeAllModals: () => {
    set({ modals: [] })
  },

  showToast: (toast) => {
    const { toasts } = get()
    const newToast: Toast = {
      ...toast,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      duration: toast.duration || 5000,
    }
    set({ toasts: [...toasts, newToast] })

    // Auto remove toast after duration
    if (newToast.duration > 0) {
      setTimeout(() => {
        get().removeToast(newToast.id)
      }, newToast.duration)
    }
  },

  removeToast: (id) => {
    const { toasts } = get()
    set({ toasts: toasts.filter(toast => toast.id !== id) })
  },

  clearToasts: () => {
    set({ toasts: [] })
  },

  setGlobalLoading: (loading) => {
    set({ globalLoading: loading })
  },

  setLoadingState: (key, loading) => {
    const { loadingStates } = get()
    set({
      loadingStates: {
        ...loadingStates,
        [key]: loading,
      },
    })
  },

  clearLoadingState: (key) => {
    const { loadingStates } = get()
    const newStates = { ...loadingStates }
    delete newStates[key]
    set({ loadingStates: newStates })
  },

  setCurrentNavigation: (nav) => {
    set({ currentNavigation: nav })
  },

  setIsMobile: (isMobile) => {
    set({ isMobile })
  },

  setIsTablet: (isTablet) => {
    set({ isTablet })
  },
})

export default createUISlice
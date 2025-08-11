import { StateCreator } from 'zustand'
import { UIState, Toast, ToastType, Modal, NotificationState, ModalState } from '../../types/ui'

/**
 * Notification Slice - handles toasts, modals, and temporary UI notifications
 * This data is temporary and should NOT be persisted
 */

// Default notification state
const DEFAULT_NOTIFICATION_STATE: NotificationState = {
  toasts: [],
  maxToasts: 5,
  defaultDuration: 5000,
  position: 'top-right',
}

const DEFAULT_MODAL_STATE: ModalState = {
  modals: [],
  activeModalId: null,
  backdrop: true,
}

// State interface
export interface NotificationSliceState {
  notifications: NotificationState
  modals: ModalState
}

// Actions interface
export interface NotificationActions {
  // Toast actions
  showToast: (toast: Omit<Toast, 'id' | 'createdAt' | 'updatedAt'>) => string
  updateToast: (id: string, updates: Partial<Toast>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
  clearToastsByType: (type: ToastType) => void
  
  // Toast configuration
  setMaxToasts: (max: number) => void
  setDefaultDuration: (duration: number) => void
  setToastPosition: (position: NotificationState['position']) => void
  
  // Modal actions
  openModal: (modal: Omit<Modal, 'isOpen'>) => void
  closeModal: (id: string) => void
  closeAllModals: () => void
  setActiveModal: (id: string | null) => void
  updateModal: (id: string, updates: Partial<Modal>) => void
  
  // Modal configuration
  setModalBackdrop: (backdrop: boolean) => void
  
  // Bulk operations
  clearAllNotifications: () => void
}

// Complete slice type
export type NotificationSlice = NotificationSliceState & NotificationActions

// Toast ID generator
let toastIdCounter = 0
const generateToastId = (): string => {
  toastIdCounter += 1
  return `toast-${Date.now()}-${toastIdCounter}`
}

// Slice creator
const createNotificationSlice: StateCreator<
  UIState,
  [],
  [],
  NotificationSlice
> = (set, get) => ({
  // Initial state
  notifications: DEFAULT_NOTIFICATION_STATE,
  modals: DEFAULT_MODAL_STATE,

  // Toast actions
  showToast: (toastData) => {
    const id = generateToastId()
    const toast: Toast = {
      ...toastData,
      id,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      duration: toastData.duration ?? get().notifications.defaultDuration,
      persistent: toastData.persistent ?? false,
    }

    set((state) => {
      const currentToasts = state.notifications.toasts
      const maxToasts = state.notifications.maxToasts
      
      // Remove oldest toasts if we exceed the limit
      const newToasts = currentToasts.length >= maxToasts
        ? [...currentToasts.slice(-(maxToasts - 1)), toast]
        : [...currentToasts, toast]

      return {
        notifications: {
          ...state.notifications,
          toasts: newToasts,
        },
      }
    })

    // Auto-remove non-persistent toasts
    if (!toast.persistent && toast.duration && toast.duration > 0) {
      setTimeout(() => {
        get().removeToast(id)
      }, toast.duration)
    }

    return id
  },

  updateToast: (id, updates) => set((state) => ({
    notifications: {
      ...state.notifications,
      toasts: state.notifications.toasts.map((toast) =>
        toast.id === id
          ? { ...toast, ...updates, updatedAt: new Date().toISOString() }
          : toast
      ),
    },
  })),

  removeToast: (id) => set((state) => ({
    notifications: {
      ...state.notifications,
      toasts: state.notifications.toasts.filter((toast) => toast.id !== id),
    },
  })),

  clearToasts: () => set((state) => ({
    notifications: {
      ...state.notifications,
      toasts: [],
    },
  })),

  clearToastsByType: (type) => set((state) => ({
    notifications: {
      ...state.notifications,
      toasts: state.notifications.toasts.filter((toast) => toast.type !== type),
    },
  })),

  // Toast configuration
  setMaxToasts: (maxToasts) => set((state) => {
    const currentToasts = state.notifications.toasts
    const newToasts = currentToasts.length > maxToasts
      ? currentToasts.slice(-maxToasts)
      : currentToasts

    return {
      notifications: {
        ...state.notifications,
        maxToasts,
        toasts: newToasts,
      },
    }
  }),

  setDefaultDuration: (defaultDuration) => set((state) => ({
    notifications: {
      ...state.notifications,
      defaultDuration,
    },
  })),

  setToastPosition: (position) => set((state) => ({
    notifications: {
      ...state.notifications,
      position,
    },
  })),

  // Modal actions
  openModal: (modalData) => {
    const modal: Modal = {
      ...modalData,
      isOpen: true,
    }

    set((state) => {
      const existingModalIndex = state.modals.modals.findIndex((m) => m.id === modal.id)
      
      let newModals: Modal[]
      if (existingModalIndex >= 0) {
        // Update existing modal
        newModals = state.modals.modals.map((m, index) =>
          index === existingModalIndex ? modal : m
        )
      } else {
        // Add new modal
        newModals = [...state.modals.modals, modal]
      }

      return {
        modals: {
          ...state.modals,
          modals: newModals,
          activeModalId: modal.id,
        },
      }
    })
  },

  closeModal: (id) => set((state) => {
    const newModals = state.modals.modals.filter((modal) => modal.id !== id)
    const newActiveModalId = newModals.length > 0 
      ? newModals[newModals.length - 1].id 
      : null

    return {
      modals: {
        ...state.modals,
        modals: newModals,
        activeModalId: newActiveModalId,
      },
    }
  }),

  closeAllModals: () => set((state) => ({
    modals: {
      ...state.modals,
      modals: [],
      activeModalId: null,
    },
  })),

  setActiveModal: (activeModalId) => set((state) => ({
    modals: {
      ...state.modals,
      activeModalId,
    },
  })),

  updateModal: (id, updates) => set((state) => ({
    modals: {
      ...state.modals,
      modals: state.modals.modals.map((modal) =>
        modal.id === id ? { ...modal, ...updates } : modal
      ),
    },
  })),

  // Modal configuration
  setModalBackdrop: (backdrop) => set((state) => ({
    modals: {
      ...state.modals,
      backdrop,
    },
  })),

  // Bulk operations
  clearAllNotifications: () => set({
    notifications: { ...DEFAULT_NOTIFICATION_STATE },
    modals: { ...DEFAULT_MODAL_STATE },
  }),
})

export default createNotificationSlice

// Helper functions for common toast types
export const createToastHelpers = (showToast: NotificationActions['showToast']) => ({
  success: (title: string, description?: string, options?: Partial<Toast>) =>
    showToast({ type: 'success', title, description, ...options }),
  
  error: (title: string, description?: string, options?: Partial<Toast>) =>
    showToast({ type: 'error', title, description, persistent: true, ...options }),
  
  warning: (title: string, description?: string, options?: Partial<Toast>) =>
    showToast({ type: 'warning', title, description, ...options }),
  
  info: (title: string, description?: string, options?: Partial<Toast>) =>
    showToast({ type: 'info', title, description, ...options }),
  
  loading: (title: string, description?: string, options?: Partial<Toast>) =>
    showToast({ type: 'loading', title, description, persistent: true, ...options }),
})
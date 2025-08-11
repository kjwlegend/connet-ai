import { useCallback, useMemo } from 'react'
import { shallow } from 'zustand/shallow'
import useAppStore from '../index.new'
import { Conversation, Message } from '../types'

/**
 * Optimized selectors to prevent unnecessary re-renders
 * Uses memoization and shallow comparison for better performance
 */

// Conversation selectors
export const useConversationList = () => {
  return useAppStore(
    useCallback((state) => ({
      conversations: state.conversations.data,
      isLoading: state.isLoading,
      lastUpdate: state.conversations.timestamp,
    }), []),
    shallow
  )
}

export const useActiveConversation = () => {
  return useAppStore(
    useCallback((state) => {
      const activeId = state.activeConversationId
      if (!activeId) return null
      
      return state.conversations.data.find(c => c.id === activeId) || null
    }, []),
    shallow
  )
}

export const useConversationById = (conversationId: string | null) => {
  return useAppStore(
    useCallback((state) => {
      if (!conversationId) return null
      return state.conversations.data.find(c => c.id === conversationId) || null
    }, [conversationId]),
    shallow
  )
}

export const useFilteredConversations = () => {
  return useAppStore(
    useCallback((state) => {
      const { conversations, filters, searchQuery } = state
      let filtered = conversations.data

      // Apply filters
      if (!filters.showArchived) {
        filtered = filtered.filter(c => !c.isArchived)
      }
      if (!filters.showMuted) {
        filtered = filtered.filter(c => !c.isMuted)
      }

      // Apply search
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim()
        filtered = filtered.filter(c =>
          c.title.toLowerCase().includes(query) ||
          c.participants.some(p => p.name.toLowerCase().includes(query))
        )
      }

      // Sort: pinned first, then by last update
      return filtered.sort((a, b) => {
        if (a.isPinned && !b.isPinned) return -1
        if (!a.isPinned && b.isPinned) return 1
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      })
    }, []),
    shallow
  )
}

export const useConversationStats = () => {
  return useAppStore(
    useCallback((state) => {
      const conversations = state.conversations.data
      return {
        total: conversations.length,
        unread: conversations.reduce((sum, c) => sum + c.unreadCount, 0),
        pinned: conversations.filter(c => c.isPinned).length,
        archived: conversations.filter(c => c.isArchived).length,
        muted: conversations.filter(c => c.isMuted).length,
      }
    }, []),
    shallow
  )
}

// UI selectors
export const useLayoutState = () => {
  return useAppStore(
    useCallback((state) => ({
      sidebarCollapsed: state.layout.sidebarCollapsed,
      middlePanelWidth: state.layout.middlePanelWidth,
      rightPanelWidth: state.layout.rightPanelWidth,
    }), []),
    shallow
  )
}

export const useNavigationState = () => {
  return useAppStore(
    useCallback((state) => ({
      currentMode: state.navigation.currentMode,
      previousMode: state.navigation.previousMode,
      breadcrumbs: state.navigation.breadcrumbs,
    }), []),
    shallow
  )
}

export const useNotificationCounts = () => {
  return useAppStore(
    useCallback((state) => ({
      toastCount: state.notifications.toasts.length,
      modalCount: state.modals.modals.length,
      hasUnreadToasts: state.notifications.toasts.some(t => !t.persistent),
      hasActiveModal: state.modals.activeModalId !== null,
    }), []),
    shallow
  )
}

// Theme and preferences selectors
export const useThemePreferences = () => {
  return useAppStore(
    useCallback((state) => ({
      mode: state.preferences.theme.mode,
      colorScheme: state.preferences.theme.colorScheme,
      fontScale: state.preferences.theme.fontScale,
      compactMode: state.preferences.theme.compactMode,
    }), []),
    shallow
  )
}

export const useAccessibilityPreferences = () => {
  return useAppStore(
    useCallback((state) => state.preferences.accessibility, []),
    shallow
  )
}

// Computed selectors with memoization
export const useComputedStats = () => {
  const conversations = useAppStore(s => s.conversations.data)
  const notifications = useAppStore(s => s.notifications.toasts)
  
  return useMemo(() => {
    const now = Date.now()
    const oneHourAgo = now - (60 * 60 * 1000)
    const oneDayAgo = now - (24 * 60 * 60 * 1000)
    
    return {
      conversations: {
        recentlyActive: conversations.filter(c => 
          new Date(c.updatedAt).getTime() > oneHourAgo
        ).length,
        activeToday: conversations.filter(c => 
          new Date(c.updatedAt).getTime() > oneDayAgo
        ).length,
      },
      notifications: {
        activeCount: notifications.length,
        errorCount: notifications.filter(n => n.type === 'error').length,
        warningCount: notifications.filter(n => n.type === 'warning').length,
      },
    }
  }, [conversations, notifications])
}

// Batched selector for dashboard/overview components
export const useDashboardData = () => {
  return useAppStore(
    useCallback((state) => ({
      conversations: {
        total: state.conversations.data.length,
        unread: state.conversations.data.reduce((sum, c) => sum + c.unreadCount, 0),
        active: state.activeConversationId,
        isLoading: state.isLoading,
      },
      ui: {
        theme: state.preferences.theme.mode,
        sidebarCollapsed: state.layout.sidebarCollapsed,
        currentNavigation: state.navigation.currentMode,
      },
      notifications: {
        toasts: state.notifications.toasts.length,
        modals: state.modals.modals.length,
      },
    }), []),
    shallow
  )
}

// Performance monitoring selector
export const useStorePerformanceMetrics = () => {
  return useAppStore(
    useCallback((state) => {
      const stateString = JSON.stringify(state)
      const stateSize = stateString.length
      
      return {
        stateSize,
        stateSizeFormatted: `${(stateSize / 1024).toFixed(1)} KB`,
        conversationsCached: state.conversations.data.length,
        cacheAge: Date.now() - state.conversations.timestamp,
        isStale: Date.now() - state.conversations.timestamp > state.conversations.ttl,
      }
    }, []),
    shallow
  )
}
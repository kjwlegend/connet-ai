import { StateCreator } from 'zustand'
import { Conversation, ConversationState, CreateConversationPayload, UpdateConversationPayload } from '../../types/chat'
import { CachedData } from '../../types/common'
import { createCachedData, isCacheValid, CACHE_TTL } from '../../utils/cache'

/**
 * Conversation Slice - handles conversation list and metadata
 * This data is cached for performance but synced with server
 */

// State interface
export interface ConversationSliceState {
  conversations: CachedData<Conversation[]>
  activeConversationId: string | null
  
  // Filters and search
  searchQuery: string
  conversationFilters: ConversationState['filters']
  
  // UI state
  isLoading: boolean
  isCreating: boolean
  conversationError: string | null
  
  // Sync state
  lastSyncTime: number
  hasPendingChanges: boolean
}

// Actions interface
export interface ConversationActions {
  // Basic CRUD operations
  loadConversations: (force?: boolean) => Promise<void>
  createConversation: (payload: CreateConversationPayload) => Promise<string>
  updateConversation: (payload: UpdateConversationPayload) => Promise<void>
  deleteConversation: (conversationId: string) => Promise<void>
  
  // Conversation management
  setActiveConversation: (conversationId: string | null) => void
  pinConversation: (conversationId: string) => void
  unpinConversation: (conversationId: string) => void
  archiveConversation: (conversationId: string) => void
  unarchiveConversation: (conversationId: string) => void
  muteConversation: (conversationId: string) => void
  unmuteConversation: (conversationId: string) => void
  
  // Bulk operations
  markAllAsRead: () => void
  archiveAllOld: (daysOld: number) => void
  deleteAllArchived: () => void
  
  // Search and filtering
  setSearchQuery: (query: string) => void
  setFilters: (filters: Partial<ConversationState['filters']>) => void
  resetFilters: () => void
  
  // Cache management
  invalidateConversationsCache: () => void
  refreshConversations: () => Promise<void>
  
  // Export functionality
  exportConversation: (conversationId: string) => Promise<string>
  exportAllConversations: () => Promise<string>
  
  // Error handling
  setConversationError: (conversationError: string | null) => void
  clearConversationError: () => void
}

// Complete slice type
export type ConversationSlice = ConversationSliceState & ConversationActions

// Mock data (will be replaced with API calls)
const createMockConversations = (): Conversation[] => [
  {
    id: '1',
    title: 'AI Programming Assistant',
    type: 'individual',
    participants: [
      {
        id: 'user-1',
        name: 'You',
        type: 'user',
        status: 'online',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        joinedAt: new Date().toISOString(),
      },
      {
        id: 'agent-1',
        name: 'AI Programming Assistant',
        type: 'agent',
        status: 'online',
        capabilities: ['coding', 'debugging', 'architecture'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        joinedAt: new Date().toISOString(),
      }
    ],
    unreadCount: 2,
    totalMessages: 15,
    isPinned: true,
    isArchived: false,
    isMuted: false,
    settings: {
      allowNotifications: true,
      soundEnabled: true,
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
  },
  {
    id: '2',
    title: 'Design Review Team',
    type: 'group',
    participants: [
      {
        id: 'user-1',
        name: 'You',
        type: 'user',
        status: 'online',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        joinedAt: new Date().toISOString(),
      },
      {
        id: 'agent-2',
        name: 'Design Review Agent',
        type: 'agent',
        status: 'online',
        capabilities: ['design', 'ui/ux', 'feedback'],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        joinedAt: new Date().toISOString(),
      }
    ],
    unreadCount: 0,
    totalMessages: 8,
    isPinned: false,
    isArchived: false,
    isMuted: false,
    settings: {
      allowNotifications: true,
      soundEnabled: false,
    },
    metadata: {
      category: 'design',
      tags: ['ui', 'review'],
    },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
  }
]

// Slice creator
const createConversationSlice: StateCreator<
  ConversationSlice,
  [],
  [],
  ConversationSlice
> = (set, get) => ({
  // Initial state
  conversations: createCachedData([], CACHE_TTL.CONVERSATIONS),
  activeConversationId: null,
  searchQuery: '',
  conversationFilters: {
    showArchived: false,
    showMuted: false,
  },
  isLoading: false,
  isCreating: false,
  conversationError: null,
  lastSyncTime: 0,
  hasPendingChanges: false,

  // Load conversations
  loadConversations: async (force = false) => {
    const state = get()
    
    // Check if cache is still valid
    if (!force && isCacheValid(state.conversations)) {
      return
    }

    try {
      set({ isLoading: true, conversationError: null })
      
      // TODO: Replace with actual API call
      // const conversations = await ConversationAPI.getConversations()
      
      // Mock API delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const mockConversations = createMockConversations()
      
      set({
        conversations: createCachedData(mockConversations, CACHE_TTL.CONVERSATIONS),
        lastSyncTime: Date.now(),
        isLoading: false,
      })
    } catch (error) {
      set({
        conversationError: error instanceof Error ? error.message : 'Failed to load conversations',
        isLoading: false,
      })
    }
  },

  // Create new conversation
  createConversation: async (payload) => {
    try {
      set({ isCreating: true, conversationError: null })
      
      // TODO: Replace with actual API call
      // const conversation = await ConversationAPI.createConversation(payload)
      
      // Mock API delay
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Create mock conversation
      const newConversation: Conversation = {
        id: `conv-${Date.now()}`,
        title: payload.title,
        type: payload.type,
        participants: [], // Would be populated by API
        unreadCount: 0,
        totalMessages: 0,
        isPinned: false,
        isArchived: false,
        isMuted: false,
        settings: payload.settings || {
          allowNotifications: true,
          soundEnabled: true,
        },
        metadata: payload.metadata,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      
      // Add to conversations list
      const state = get()
      const currentConversations = state.conversations.data
      const updatedConversations = [newConversation, ...currentConversations]
      
      set({
        conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
        activeConversationId: newConversation.id,
        isCreating: false,
      })
      
      return newConversation.id
    } catch (error) {
      set({
        conversationError: error instanceof Error ? error.message : 'Failed to create conversation',
        isCreating: false,
      })
      throw error
    }
  },

  // Update conversation
  updateConversation: async (payload) => {
    try {
      set({ conversationError: null })
      
      // TODO: Replace with actual API call
      // await ConversationAPI.updateConversation(payload.conversationId, payload)
      
      // Update local state immediately (optimistic update)
      const state = get()
      const currentConversations = state.conversations.data
      const updatedConversations = currentConversations.map(conv =>
        conv.id === payload.conversationId
          ? {
              ...conv,
              ...payload,
              updatedAt: new Date().toISOString(),
            }
          : conv
      )
      
      set({
        conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
        hasPendingChanges: true,
      })
    } catch (error) {
      set({
        conversationError: error instanceof Error ? error.message : 'Failed to update conversation',
      })
      throw error
    }
  },

  // Delete conversation
  deleteConversation: async (conversationId) => {
    try {
      set({ conversationError: null })
      
      // TODO: Replace with actual API call
      // await ConversationAPI.deleteConversation(conversationId)
      
      // Remove from local state immediately
      const state = get()
      const currentConversations = state.conversations.data
      const updatedConversations = currentConversations.filter(conv => conv.id !== conversationId)
      
      set({
        conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
        activeConversationId: state.activeConversationId === conversationId 
          ? null 
          : state.activeConversationId,
      })
    } catch (error) {
      set({
        conversationError: error instanceof Error ? error.message : 'Failed to delete conversation',
      })
      throw error
    }
  },

  // Set active conversation
  setActiveConversation: (conversationId) => {
    set({ activeConversationId: conversationId })
    
    // Mark as read when opened
    if (conversationId) {
      const state = get()
      const conversation = state.conversations.data.find(c => c.id === conversationId)
      if (conversation && conversation.unreadCount > 0) {
        get().updateConversation({
          conversationId,
          unreadCount: 0,
        })
      }
    }
  },

  // Pin/Unpin conversation
  pinConversation: (conversationId) => {
    get().updateConversation({ conversationId, isPinned: true })
  },

  unpinConversation: (conversationId) => {
    get().updateConversation({ conversationId, isPinned: false })
  },

  // Archive/Unarchive conversation
  archiveConversation: (conversationId) => {
    get().updateConversation({ conversationId, isArchived: true })
  },

  unarchiveConversation: (conversationId) => {
    get().updateConversation({ conversationId, isArchived: false })
  },

  // Mute/Unmute conversation
  muteConversation: (conversationId) => {
    get().updateConversation({ 
      conversationId, 
      isMuted: true,
      settings: { allowNotifications: false, soundEnabled: false }
    })
  },

  unmuteConversation: (conversationId) => {
    get().updateConversation({ 
      conversationId, 
      isMuted: false,
      settings: { allowNotifications: true, soundEnabled: true }
    })
  },

  // Bulk operations
  markAllAsRead: () => {
    const state = get()
    const updatedConversations = state.conversations.data.map(conv => ({
      ...conv,
      unreadCount: 0,
      updatedAt: new Date().toISOString(),
    }))
    
    set({
      conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
    })
  },

  archiveAllOld: (daysOld) => {
    const cutoffDate = Date.now() - (daysOld * 24 * 60 * 60 * 1000)
    const state = get()
    const updatedConversations = state.conversations.data.map(conv => ({
      ...conv,
      isArchived: conv.isArchived || new Date(conv.updatedAt).getTime() < cutoffDate,
      updatedAt: new Date().toISOString(),
    }))
    
    set({
      conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
    })
  },

  deleteAllArchived: () => {
    const state = get()
    const updatedConversations = state.conversations.data.filter(conv => !conv.isArchived)
    
    set({
      conversations: createCachedData(updatedConversations, CACHE_TTL.CONVERSATIONS),
    })
  },

  // Search and filtering
  setSearchQuery: (searchQuery) => {
    set({ searchQuery })
  },

  setFilters: (filters) => set((state) => ({
    conversationFilters: { ...state.conversationFilters, ...filters }
  })),

  resetFilters: () => set({
    conversationFilters: {
      showArchived: false,
      showMuted: false,
    },
    searchQuery: '',
  }),

  // Cache management
  invalidateConversationsCache: () => set((state) => ({
    conversations: createCachedData(state.conversations.data, 0), // Force expiry
  })),

  refreshConversations: () => get().loadConversations(true),

  // Export functionality
  exportConversation: async (conversationId) => {
    const state = get()
    const conversation = state.conversations.data.find(c => c.id === conversationId)
    
    if (!conversation) {
      throw new Error('Conversation not found')
    }

    // Generate export content
    let content = `# ${conversation.title}\n\n`
    content += `**Type**: ${conversation.type}\n`
    content += `**Participants**: ${conversation.participants.map(p => p.name).join(', ')}\n`
    content += `**Created**: ${new Date(conversation.createdAt).toLocaleDateString()}\n`
    content += `**Total Messages**: ${conversation.totalMessages}\n\n`

    if (conversation.metadata?.description) {
      content += `**Description**: ${conversation.metadata.description}\n\n`
    }

    content += `---\n\n*Exported on ${new Date().toLocaleString()}*\n`

    return content
  },

  exportAllConversations: async () => {
    const state = get()
    const conversations = state.conversations.data

    let content = `# All Conversations Export\n\n`
    content += `**Total Conversations**: ${conversations.length}\n`
    content += `**Exported**: ${new Date().toLocaleString()}\n\n`
    content += `---\n\n`

    for (const conv of conversations) {
      content += `## ${conv.title}\n`
      content += `- **Type**: ${conv.type}\n`
      content += `- **Messages**: ${conv.totalMessages}\n`
      content += `- **Last Updated**: ${new Date(conv.updatedAt).toLocaleDateString()}\n`
      content += `- **Status**: ${conv.isArchived ? 'Archived' : 'Active'}\n\n`
    }

    return content
  },

  // Error handling
  setConversationError: (conversationError) => set({ conversationError }),
  clearConversationError: () => set({ conversationError: null }),
})

export default createConversationSlice
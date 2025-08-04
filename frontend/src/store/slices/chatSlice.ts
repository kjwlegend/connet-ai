import { StateCreator } from 'zustand'
import { StoreState } from '../types'

// Chat Types
export interface Message {
  id: string
  conversationId: string
  senderId: string
  senderName: string
  senderType: 'user' | 'agent' | 'system'
  content: string
  contentType: 'text' | 'image' | 'file' | 'code'
  timestamp: string
  isRead: boolean
  metadata?: {
    mentions?: string[]
    attachments?: string[]
    reactions?: Record<string, string[]>
  }
}

export interface Conversation {
  id: string
  title: string
  participants: Participant[]
  lastMessage?: Message
  updatedAt: string
  isActive: boolean
  unreadCount: number
  tags?: string[]
  metadata?: {
    description?: string
    category?: string
  }
}

export interface Participant {
  id: string
  name: string
  type: 'user' | 'agent'
  avatar?: string
  status: 'online' | 'offline' | 'busy'
  capabilities?: string[]
}

export interface ChatState {
  // Conversations
  conversations: Conversation[]
  activeConversationId: string | null
  
  // Messages
  messages: Record<string, Message[]> // conversationId -> messages
  
  // UI State
  isLoading: boolean
  isSending: boolean
  error: string | null
  
  // Message composition
  draft: string
  mentionSuggestions: Participant[]
  showMentionSuggestions: boolean
}

export interface ChatActions {
  // Conversation management
  setActiveConversation: (conversationId: string | null) => void
  addConversation: (conversation: Conversation) => void
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void
  deleteConversation: (conversationId: string) => void
  loadConversations: () => Promise<void>
  
  // Message management
  addMessage: (message: Message) => void
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  deleteMessage: (messageId: string) => void
  loadMessages: (conversationId: string) => Promise<void>
  sendMessage: (conversationId: string, content: string, mentions?: string[]) => Promise<void>
  
  // Draft management
  setDraft: (content: string) => void
  clearDraft: () => void
  
  // Mention system
  setMentionSuggestions: (suggestions: Participant[]) => void
  showMentions: () => void
  hideMentions: () => void
  
  // UI state
  setLoading: (loading: boolean) => void
  setSending: (sending: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export type ChatSlice = ChatState & ChatActions

const createChatSlice: StateCreator<StoreState, [], [], ChatSlice> = (set, get) => ({
  // Initial state
  conversations: [],
  activeConversationId: null,
  messages: {},
  isLoading: false,
  isSending: false,
  error: null,
  draft: '',
  mentionSuggestions: [],
  showMentionSuggestions: false,

  // Conversation management
  setActiveConversation: (conversationId) => {
    set({ activeConversationId: conversationId })
    
    // Load messages for the active conversation
    if (conversationId && !get().messages[conversationId]) {
      get().loadMessages(conversationId)
    }
  },

  addConversation: (conversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations]
    }))
  },

  updateConversation: (conversationId, updates) => {
    set((state) => ({
      conversations: state.conversations.map(conv =>
        conv.id === conversationId ? { ...conv, ...updates } : conv
      )
    }))
  },

  deleteConversation: (conversationId) => {
    set((state) => {
      const newMessages = { ...state.messages }
      delete newMessages[conversationId]
      
      return {
        conversations: state.conversations.filter(conv => conv.id !== conversationId),
        messages: newMessages,
        activeConversationId: state.activeConversationId === conversationId 
          ? null 
          : state.activeConversationId
      }
    })
  },

  loadConversations: async () => {
    try {
      set({ isLoading: true, error: null })
      
      // TODO: Replace with actual API call
      // const conversations = await ChatAPI.getConversations()
      
      // Mock data for now
      const mockConversations: Conversation[] = [
        {
          id: '1',
          title: 'AI Programming Assistant',
          participants: [
            {
              id: 'user-1',
              name: 'You',
              type: 'user',
              status: 'online'
            },
            {
              id: 'agent-1',
              name: 'AI Programming Assistant',
              type: 'agent',
              status: 'online',
              capabilities: ['coding', 'debugging', 'architecture']
            }
          ],
          updatedAt: new Date().toISOString(),
          isActive: true,
          unreadCount: 2,
        },
        {
          id: '2',
          title: 'Design Review Agent',
          participants: [
            {
              id: 'user-1',
              name: 'You',
              type: 'user',
              status: 'online'
            },
            {
              id: 'agent-2',
              name: 'Design Review Agent',
              type: 'agent',
              status: 'online',
              capabilities: ['design', 'ui/ux', 'feedback']
            }
          ],
          updatedAt: new Date(Date.now() - 3600000).toISOString(),
          isActive: true,
          unreadCount: 0,
        }
      ]
      
      set({ conversations: mockConversations })
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to load conversations' })
    } finally {
      set({ isLoading: false })
    }
  },

  // Message management
  addMessage: (message) => {
    set((state) => ({
      messages: {
        ...state.messages,
        [message.conversationId]: [
          ...(state.messages[message.conversationId] || []),
          message
        ]
      }
    }))

    // Update conversation's last message
    get().updateConversation(message.conversationId, {
      lastMessage: message,
      updatedAt: message.timestamp
    })
  },

  updateMessage: (messageId, updates) => {
    set((state) => {
      const newMessages = { ...state.messages }
      
      for (const conversationId in newMessages) {
        const messages = newMessages[conversationId]
        const messageIndex = messages.findIndex(msg => msg.id === messageId)
        
        if (messageIndex !== -1) {
          newMessages[conversationId] = [
            ...messages.slice(0, messageIndex),
            { ...messages[messageIndex], ...updates },
            ...messages.slice(messageIndex + 1)
          ]
          break
        }
      }
      
      return { messages: newMessages }
    })
  },

  deleteMessage: (messageId) => {
    set((state) => {
      const newMessages = { ...state.messages }
      
      for (const conversationId in newMessages) {
        newMessages[conversationId] = newMessages[conversationId].filter(
          msg => msg.id !== messageId
        )
      }
      
      return { messages: newMessages }
    })
  },

  loadMessages: async (conversationId) => {
    try {
      set({ isLoading: true, error: null })
      
      // TODO: Replace with actual API call
      // const messages = await ChatAPI.getMessages(conversationId)
      
      // Mock messages for now
      const mockMessages: Message[] = [
        {
          id: 'msg-1',
          conversationId,
          senderId: 'agent-1',
          senderName: 'AI Programming Assistant',
          senderType: 'agent',
          content: '你好！我是你的AI编程助手，可以帮你解决各种编程问题。有什么我可以帮助你的吗？',
          contentType: 'text',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          isRead: true,
        },
        {
          id: 'msg-2',
          conversationId,
          senderId: 'user-1',
          senderName: 'You',
          senderType: 'user',
          content: '我想优化一下React组件的性能，有什么建议吗？',
          contentType: 'text',
          timestamp: new Date(Date.now() - 7080000).toISOString(),
          isRead: true,
        },
        {
          id: 'msg-3',
          conversationId,
          senderId: 'agent-1',
          senderName: 'AI Programming Assistant',
          senderType: 'agent',
          content: '当然可以！React性能优化有几个关键点：\n\n1. 使用React.memo包装组件避免不必要的重渲染\n2. 使用useMemo和useCallback缓存计算结果和函数\n3. 合理使用useState和useEffect\n4. 避免在render中创建新对象\n\n你想了解哪个方面的详细实现？',
          contentType: 'text',
          timestamp: new Date(Date.now() - 7020000).toISOString(),
          isRead: true,
        }
      ]
      
      set((state) => ({
        messages: {
          ...state.messages,
          [conversationId]: mockMessages
        }
      }))
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to load messages' })
    } finally {
      set({ isLoading: false })
    }
  },

  sendMessage: async (conversationId, content, mentions = []) => {
    try {
      set({ isSending: true, error: null })
      
      const message: Message = {
        id: `msg-${Date.now()}`,
        conversationId,
        senderId: 'user-1', // TODO: Get from auth state
        senderName: 'You',
        senderType: 'user',
        content,
        contentType: 'text',
        timestamp: new Date().toISOString(),
        isRead: false,
        metadata: mentions.length > 0 ? { mentions } : undefined
      }
      
      // Add message locally first
      get().addMessage(message)
      
      // TODO: Send to API
      // await ChatAPI.sendMessage(conversationId, content, mentions)
      
      // Mock AI response
      setTimeout(() => {
        const aiResponse: Message = {
          id: `msg-${Date.now()}-ai`,
          conversationId,
          senderId: 'agent-1',
          senderName: 'AI Programming Assistant',
          senderType: 'agent',
          content: '我理解你的问题。让我为你提供一个详细的解决方案...',
          contentType: 'text',
          timestamp: new Date().toISOString(),
          isRead: false,
        }
        
        get().addMessage(aiResponse)
      }, 1000)
      
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to send message' })
    } finally {
      set({ isSending: false })
    }
  },

  // Draft management
  setDraft: (content) => {
    set({ draft: content })
  },

  clearDraft: () => {
    set({ draft: '' })
  },

  // Mention system
  setMentionSuggestions: (suggestions) => {
    set({ mentionSuggestions: suggestions })
  },

  showMentions: () => {
    set({ showMentionSuggestions: true })
  },

  hideMentions: () => {
    set({ showMentionSuggestions: false })
  },

  // UI state management
  setLoading: (loading) => {
    set({ isLoading: loading })
  },

  setSending: (sending) => {
    set({ isSending: sending })
  },

  setError: (error) => {
    set({ error })
  },

  clearError: () => {
    set({ error: null })
  },
})

export default createChatSlice
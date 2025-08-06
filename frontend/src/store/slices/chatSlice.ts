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
  isPinned?: boolean
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
  createNewConversation: (agentId: string, agentName: string, title?: string) => Promise<string>
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void
  deleteConversation: (conversationId: string) => void
  loadConversations: () => Promise<void>
  pinConversation: (conversationId: string) => void
  unpinConversation: (conversationId: string) => void
  exportConversation: (conversationId: string) => Promise<string>
  
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

  createNewConversation: async (agentId: string, agentName: string, title?: string) => {
    try {
      set({ isLoading: true, error: null })
      
      // Generate unique conversation ID
      const conversationId = `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      const newConversation: Conversation = {
        id: conversationId,
        title: title || `Chat with ${agentName}`,
        participants: [
          {
            id: 'user-1',
            name: 'You',
            type: 'user',
            status: 'online'
          },
          {
            id: agentId,
            name: agentName,
            type: 'agent',
            status: 'online',
            capabilities: ['chat', 'assistance']
          }
        ],
        updatedAt: new Date().toISOString(),
        isActive: true,
        unreadCount: 0,
      }

      // Add the new conversation to the list
      get().addConversation(newConversation)
      
      // Set it as the active conversation
      get().setActiveConversation(conversationId)
      
      // Add a welcome message from the agent
      const welcomeMessage: Message = {
        id: `msg-${conversationId}-welcome`,
        conversationId: conversationId,
        senderId: agentId,
        senderName: agentName,
        senderType: 'agent',
        content: `你好！我是 ${agentName}，很高兴为您服务。请告诉我需要什么帮助？`,
        contentType: 'text',
        timestamp: new Date().toISOString(),
        isRead: false
      }
      
      get().addMessage(welcomeMessage)
      
      return conversationId
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to create conversation' })
      throw error
    } finally {
      set({ isLoading: false })
    }
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
      
      // Mock data for now - Extended with more conversations
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
          lastMessage: {
            id: 'msg-1-3',
            conversationId: '1',
            senderId: 'agent-1',
            senderName: 'AI Programming Assistant',
            senderType: 'agent',
            content: '我可以帮您优化这段代码的性能。建议使用 useMemo 来缓存计算结果。',
            contentType: 'text',
            timestamp: new Date(Date.now() - 300000).toISOString(), // 5分钟前
            isRead: false
          },
          updatedAt: new Date(Date.now() - 300000).toISOString(),
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
          lastMessage: {
            id: 'msg-2-2',
            conversationId: '2',
            senderId: 'user-1',
            senderName: 'You',
            senderType: 'user',
            content: '请帮我审查这个新的用户界面设计',
            contentType: 'text',
            timestamp: new Date(Date.now() - 3600000).toISOString(), // 1小时前
            isRead: true
          },
          updatedAt: new Date(Date.now() - 3600000).toISOString(),
          isActive: true,
          unreadCount: 0,
        },
        {
          id: '3',
          title: 'Content Writing Assistant',
          participants: [
            {
              id: 'user-1',
              name: 'You',
              type: 'user',
              status: 'online'
            },
            {
              id: 'agent-3',
              name: 'Content Writing Assistant',
              type: 'agent',
              status: 'online',
              capabilities: ['writing', 'editing', 'translation']
            }
          ],
          lastMessage: {
            id: 'msg-3-1',
            conversationId: '3',
            senderId: 'agent-3',
            senderName: 'Content Writing Assistant',
            senderType: 'agent',
            content: '您好！我是内容写作助手，可以帮您撰写和编辑各类文档。请告诉我您需要什么帮助？',
            contentType: 'text',
            timestamp: new Date(Date.now() - 7200000).toISOString(), // 2小时前
            isRead: true
          },
          updatedAt: new Date(Date.now() - 7200000).toISOString(),
          isActive: true,
          unreadCount: 0,
        },
        {
          id: '4',
          title: 'Data Analysis Expert',
          participants: [
            {
              id: 'user-1',
              name: 'You',
              type: 'user',
              status: 'online'
            },
            {
              id: 'agent-4',
              name: 'Data Analysis Expert',
              type: 'agent',
              status: 'busy',
              capabilities: ['data-analysis', 'statistics', 'visualization']
            }
          ],
          lastMessage: {
            id: 'msg-4-5',
            conversationId: '4',
            senderId: 'agent-4',
            senderName: 'Data Analysis Expert',
            senderType: 'agent',
            content: '数据分析报告已生成完成，请查看附件中的详细图表和建议。',
            contentType: 'text',
            timestamp: new Date(Date.now() - 86400000).toISOString(), // 1天前
            isRead: true
          },
          updatedAt: new Date(Date.now() - 86400000).toISOString(),
          isActive: true,
          unreadCount: 1,
        },
        {
          id: '5',
          title: 'AI Team Collaboration',
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
            },
            {
              id: 'agent-2',
              name: 'Design Review Agent',
              type: 'agent',
              status: 'online',
              capabilities: ['design', 'ui/ux', 'feedback']
            }
          ],
          lastMessage: {
            id: 'msg-5-3',
            conversationId: '5',
            senderId: 'agent-2',
            senderName: 'Design Review Agent',
            senderType: 'agent',
            content: '@AI Programming Assistant 这个交互设计看起来不错，你觉得技术实现上有什么建议吗？',
            contentType: 'text',
            timestamp: new Date(Date.now() - 1800000).toISOString(), // 30分钟前
            isRead: false,
            metadata: {
              mentions: ['agent-1']
            }
          },
          updatedAt: new Date(Date.now() - 1800000).toISOString(),
          isActive: true,
          unreadCount: 3,
        },
        {
          id: '6',
          title: 'Product Strategy Group',
          participants: [
            {
              id: 'user-1',
              name: 'You',
              type: 'user',
              status: 'online'
            },
            {
              id: 'agent-5',
              name: 'Product Manager AI',
              type: 'agent',
              status: 'online',
              capabilities: ['product-strategy', 'market-analysis', 'user-research']
            },
            {
              id: 'agent-6',
              name: 'Business Analyst',
              type: 'agent',
              status: 'busy',
              capabilities: ['business-analysis', 'requirements', 'documentation']
            },
            {
              id: 'agent-7',
              name: 'UX Research Agent',
              type: 'agent',
              status: 'online',
              capabilities: ['ux-research', 'user-testing', 'interviews']
            }
          ],
          lastMessage: {
            id: 'msg-6-7',
            conversationId: '6',
            senderId: 'agent-5',
            senderName: 'Product Manager AI',
            senderType: 'agent',
            content: '基于用户反馈，我们需要重新评估核心功能的优先级。@UX Research Agent 能否分享最新的用户调研结果？',
            contentType: 'text',
            timestamp: new Date(Date.now() - 600000).toISOString(), // 10分钟前
            isRead: false,
            metadata: {
              mentions: ['agent-7']
            }
          },
          updatedAt: new Date(Date.now() - 600000).toISOString(),
          isActive: true,
          unreadCount: 5,
        },
        {
          id: '7',
          title: 'Development Sprint Team',
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
            },
            {
              id: 'agent-8',
              name: 'DevOps Specialist',
              type: 'agent',
              status: 'online',
              capabilities: ['devops', 'deployment', 'monitoring']
            },
            {
              id: 'agent-9',
              name: 'QA Testing Agent',
              type: 'agent',
              status: 'offline',
              capabilities: ['testing', 'quality-assurance', 'automation']
            },
            {
              id: 'agent-10',
              name: 'Tech Lead AI',
              type: 'agent',
              status: 'busy',
              capabilities: ['technical-leadership', 'architecture', 'code-review']
            }
          ],
          lastMessage: {
            id: 'msg-7-12',
            conversationId: '7',
            senderId: 'agent-8',
            senderName: 'DevOps Specialist',
            senderType: 'agent',
            content: 'CI/CD 流水线已更新完成，现在支持自动化测试和部署。@QA Testing Agent 请确认测试环境是否正常工作。',
            contentType: 'text',
            timestamp: new Date(Date.now() - 3600000).toISOString(), // 1小时前
            isRead: true,
            metadata: {
              mentions: ['agent-9']
            }
          },
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
      
      // Mock messages for now - different messages based on conversation
      let mockMessages: Message[] = []
      
      if (conversationId === '5') {
        // AI Team Collaboration group messages
        mockMessages = [
          {
            id: 'msg-5-1',
            conversationId,
            senderId: 'agent-1',
            senderName: 'AI Programming Assistant',
            senderType: 'agent',
            content: '大家好！我们来讨论一下这个新项目的技术架构吧。',
            contentType: 'text',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            isRead: true,
          },
          {
            id: 'msg-5-2',
            conversationId,
            senderId: 'agent-2',
            senderName: 'Design Review Agent',
            senderType: 'agent',
            content: '从设计角度看，我们需要确保用户界面的一致性。我已经准备了一些设计原型。',
            contentType: 'text',
            timestamp: new Date(Date.now() - 3000000).toISOString(),
            isRead: true,
          },
          {
            id: 'msg-5-3',
            conversationId,
            senderId: 'user-1',
            senderName: 'You',
            senderType: 'user',
            content: '很好！@AI Programming Assistant 你觉得我们应该使用什么技术栈？',
            contentType: 'text',
            timestamp: new Date(Date.now() - 2400000).toISOString(),
            isRead: true,
            metadata: {
              mentions: ['agent-1']
            }
          },
          {
            id: 'msg-5-4',
            conversationId,
            senderId: 'agent-2',
            senderName: 'Design Review Agent',
            senderType: 'agent',
            content: '@AI Programming Assistant 这个交互设计看起来不错，你觉得技术实现上有什么建议吗？',
            contentType: 'text',
            timestamp: new Date(Date.now() - 1800000).toISOString(),
            isRead: false,
            metadata: {
              mentions: ['agent-1']
            }
          }
        ]
      } else {
        // Default individual conversation messages
        mockMessages = [
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
      }
      
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

  // New conversation management functions
  pinConversation: (conversationId) => {
    set((state) => ({
      conversations: state.conversations.map(conv =>
        conv.id === conversationId ? { ...conv, isPinned: true } : conv
      )
    }))
  },

  unpinConversation: (conversationId) => {
    set((state) => ({
      conversations: state.conversations.map(conv =>
        conv.id === conversationId ? { ...conv, isPinned: false } : conv
      )
    }))
  },

  exportConversation: async (conversationId) => {
    try {
      const { conversations, messages } = get()
      const conversation = conversations.find(conv => conv.id === conversationId)
      const conversationMessages = messages[conversationId] || []

      if (!conversation) {
        throw new Error('Conversation not found')
      }

      // Generate markdown content
      let markdown = `# ${conversation.title}\n\n`
      markdown += `**Participants**: ${conversation.participants.map(p => p.name).join(', ')}\n`
      markdown += `**Date**: ${new Date(conversation.updatedAt).toLocaleDateString()}\n\n`
      markdown += `---\n\n`

      conversationMessages.forEach(message => {
        const timestamp = new Date(message.timestamp).toLocaleString()
        markdown += `## ${message.senderName} - ${timestamp}\n\n`
        markdown += `${message.content}\n\n`
        if (message.metadata?.mentions) {
          markdown += `*Mentions: ${message.metadata.mentions.join(', ')}*\n\n`
        }
        markdown += `---\n\n`
      })

      // Download the file
      const blob = new Blob([markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${conversation.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_conversation.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      return markdown
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Failed to export conversation' })
      throw error
    }
  },
})

export default createChatSlice
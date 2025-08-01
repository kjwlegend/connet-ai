# Data Flow & State Management Architecture - Connet.AI

## 数据流架构原则

### 1. 单向数据流 (Unidirectional Data Flow)
- **可预测性**: 数据变化路径清晰，便于调试和维护
- **可追溯性**: 所有状态变更都有明确的触发源
- **一致性**: 避免双向绑定带来的复杂性和不一致性
- **测试友好**: 纯函数和明确的输入输出便于单元测试

### 2. 状态分层管理
- **本地状态**: 组件内部的临时状态
- **全局状态**: 跨组件共享的应用状态  
- **服务端状态**: 来自 API 的远程数据
- **实时状态**: WebSocket 推送的动态数据

### 3. 数据同步策略
- **乐观更新**: 提升用户体验的即时反馈
- **悲观更新**: 关键操作的安全保障
- **冲突解决**: 多客户端数据冲突处理
- **缓存策略**: 智能缓存提升性能

## 整体数据流架构

```
Data Flow Architecture
│
├── 🎯 User Interactions (用户交互)
│   ├── UI Events (界面事件)
│   ├── Form Submissions (表单提交)
│   ├── Navigation (路由导航)
│   └── Keyboard/Mouse Actions (键鼠操作)
│
├── 🎪 Event Handlers (事件处理层)
│   ├── Component Event Handlers (组件事件处理)
│   ├── Custom Hook Handlers (自定义Hook处理)
│   ├── Global Event Listeners (全局事件监听)
│   └── WebSocket Event Handlers (WebSocket事件处理)
│
├── 🏪 State Management (状态管理层)
│   ├── Zustand Global Store (全局状态存储)
│   │   ├── Auth Slice (认证状态切片)
│   │   ├── UI Slice (界面状态切片)
│   │   ├── Chat Slice (聊天状态切片)
│   │   └── Settings Slice (设置状态切片)
│   │
│   ├── React Query Cache (服务端状态缓存)
│   │   ├── Query Cache (查询缓存)
│   │   ├── Mutation Cache (变更缓存)
│   │   ├── Infinite Queries (无限查询)
│   │   └── Background Updates (后台更新)
│   │
│   ├── Component Local State (组件本地状态)
│   │   ├── Form State (表单状态)
│   │   ├── UI Temporary State (临时界面状态)
│   │   └── Component Lifecycle State (组件生命周期状态)
│   │
│   └── Context Providers (上下文提供者)
│       ├── Theme Context (主题上下文)
│       ├── I18n Context (国际化上下文)
│       └── Notification Context (通知上下文)
│
├── 🌐 Data Access Layer (数据访问层)
│   ├── API Services (API服务)
│   │   ├── HTTP Client (HTTP客户端)
│   │   ├── Request Interceptors (请求拦截器)
│   │   ├── Response Interceptors (响应拦截器)
│   │   └── Error Handlers (错误处理器)
│   │
│   ├── WebSocket Manager (WebSocket管理器)
│   │   ├── Connection Manager (连接管理)
│   │   ├── Event Dispatcher (事件分发器)
│   │   ├── Reconnection Logic (重连逻辑)
│   │   └── Message Queue (消息队列)
│   │
│   ├── Cache Manager (缓存管理器)
│   │   ├── Memory Cache (内存缓存)
│   │   ├── Local Storage (本地存储)
│   │   ├── Session Storage (会话存储)
│   │   └── IndexedDB (索引数据库)
│   │
│   └── Offline Manager (离线管理器)
│       ├── Offline Detection (离线检测)
│       ├── Request Queue (请求队列)
│       ├── Data Synchronization (数据同步)
│       └── Conflict Resolution (冲突解决)
│
└── 🖥️ UI Rendering (界面渲染层)
    ├── Component Re-rendering (组件重渲染)
    ├── Virtual DOM Updates (虚拟DOM更新)
    ├── Layout Calculations (布局计算)
    └── Browser Painting (浏览器绘制)
```

## Zustand 全局状态管理

### 1. Store 架构设计

#### 1.1 Store 分片设计
```typescript
// store/index.ts - 主 Store 配置
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

import { AuthSlice, createAuthSlice } from './slices/authSlice'
import { UISlice, createUISlice } from './slices/uiSlice'
import { ChatSlice, createChatSlice } from './slices/chatSlice'
import { SettingsSlice, createSettingsSlice } from './slices/settingsSlice'

// 组合所有状态片段的类型
export interface RootState extends AuthSlice, UISlice, ChatSlice, SettingsSlice {}

// 创建主 Store
export const useStore = create<RootState>()(
  devtools(
    persist(
      immer(
        (...args) => ({
          ...createAuthSlice(...args),
          ...createUISlice(...args),
          ...createChatSlice(...args),
          ...createSettingsSlice(...args),
        })
      ),
      {
        name: 'connet-ai-store',
        // 选择性持久化
        partialize: (state) => ({
          auth: {
            user: state.auth.user,
            preferences: state.auth.preferences
          },
          settings: state.settings,
          ui: {
            theme: state.ui.theme,
            language: state.ui.language,
            sidebarCollapsed: state.ui.sidebarCollapsed
          }
        })
      }
    ),
    {
      name: 'connet-ai-store',
      enabled: process.env.NODE_ENV === 'development'
    }
  )
)

// 选择器 Hooks
export const useAuth = () => useStore((state) => state.auth)
export const useUI = () => useStore((state) => state.ui)  
export const useChat = () => useStore((state) => state.chat)
export const useSettings = () => useStore((state) => state.settings)
```

#### 1.2 认证状态切片 (Auth Slice)
```typescript
// store/slices/authSlice.ts
import { StateCreator } from 'zustand'
import { User, AuthTokens, UserPreferences } from '@/types/auth'

export interface AuthState {
  // 状态数据
  user: User | null
  tokens: AuthTokens | null
  preferences: UserPreferences | null
  isLoading: boolean
  isAuthenticated: boolean
  lastActivity: Date | null
  sessionExpiry: Date | null
}

export interface AuthActions {
  // 认证操作
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  
  // 用户信息操作
  updateUser: (updates: Partial<User>) => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void
  
  // 会话管理
  updateActivity: () => void
  checkSession: () => boolean
  extendSession: () => void
  
  // 状态重置
  reset: () => void
}

export type AuthSlice = {
  auth: AuthState & AuthActions
}

const initialAuthState: AuthState = {
  user: null,
  tokens: null,
  preferences: null,
  isLoading: false,
  isAuthenticated: false,
  lastActivity: null,
  sessionExpiry: null
}

export const createAuthSlice: StateCreator<
  AuthSlice,
  [["zustand/immer", never], ["zustand/devtools", never], ["zustand/persist", unknown]],
  [],
  AuthSlice
> = (set, get) => ({
  auth: {
    ...initialAuthState,
    
    // 登录操作
    login: async (credentials) => {
      set((state) => {
        state.auth.isLoading = true
      })
      
      try {
        const response = await authApi.login(credentials)
        const { user, tokens } = response.data
        
        set((state) => {
          state.auth.user = user
          state.auth.tokens = tokens
          state.auth.isAuthenticated = true
          state.auth.isLoading = false
          state.auth.lastActivity = new Date()
          state.auth.sessionExpiry = new Date(Date.now() + tokens.expiresIn * 1000)
        })
        
        // 设置自动刷新令牌
        authTokenManager.scheduleRefresh(tokens.expiresIn)
        
      } catch (error) {
        set((state) => {
          state.auth.isLoading = false
        })
        throw error
      }
    },
    
    // 登出操作
    logout: async () => {
      const { tokens } = get().auth
      
      try {
        if (tokens) {
          await authApi.logout(tokens.refreshToken)
        }
      } finally {
        set((state) => {
          Object.assign(state.auth, initialAuthState)
        })
        
        // 清理令牌管理器
        authTokenManager.clearSchedule()
        
        // 清理其他相关状态
        get().chat.clearAll()
        get().ui.reset()
      }
    },
    
    // 刷新令牌
    refreshToken: async () => {
      const { tokens } = get().auth
      if (!tokens) throw new Error('No refresh token available')
      
      try {
        const response = await authApi.refreshToken(tokens.refreshToken)  
        const newTokens = response.data.tokens
        
        set((state) => {
          state.auth.tokens = newTokens
          state.auth.sessionExpiry = new Date(Date.now() + newTokens.expiresIn * 1000)
        })
        
        authTokenManager.scheduleRefresh(newTokens.expiresIn)
        
      } catch (error) {
        // 刷新失败，执行登出
        await get().auth.logout()
        throw error
      }
    },
    
    // 更新用户信息
    updateUser: (updates) => {
      set((state) => {
        if (state.auth.user) {
          Object.assign(state.auth.user, updates)
        }
      })
    },
    
    // 更新用户偏好
    updatePreferences: (preferences) => {
      set((state) => {
        if (state.auth.preferences) {
          Object.assign(state.auth.preferences, preferences)
        } else {
          state.auth.preferences = preferences as UserPreferences
        }
      })
    },
    
    // 更新活动时间
    updateActivity: () => {
      set((state) => {
        state.auth.lastActivity = new Date()
      })
    },
    
    // 检查会话有效性
    checkSession: () => {
      const { sessionExpiry, isAuthenticated } = get().auth
      if (!isAuthenticated || !sessionExpiry) return false
      
      const now = new Date()
      const isExpired = now >= sessionExpiry
      
      if (isExpired) {
        // 会话过期，尝试刷新或登出
        get().auth.refreshToken().catch(() => {
          get().auth.logout()
        })
        return false
      }
      
      return true
    },
    
    // 延长会话
    extendSession: () => {
      const sessionExtension = 30 * 60 * 1000 // 30分钟
      
      set((state) => {
        if (state.auth.sessionExpiry) {
          state.auth.sessionExpiry = new Date(
            state.auth.sessionExpiry.getTime() + sessionExtension
          )
        }
      })
    },
    
    // 重置状态
    reset: () => {
      set((state) => {
        Object.assign(state.auth, initialAuthState)
      })
    }
  }
})
```

#### 1.3 聊天状态切片 (Chat Slice)
```typescript
// store/slices/chatSlice.ts
import { StateCreator } from 'zustand'
import { Conversation, Message, Agent } from '@/types/chat'

export interface ChatState {
  // 对话数据
  conversations: Record<string, Conversation>
  conversationList: string[] // 排序后的对话ID列表
  activeConversationId: string | null
  
  // 消息数据 
  messages: Record<string, Message> // 按消息ID存储
  conversationMessages: Record<string, string[]> // 按对话ID存储消息ID列表
  
  // 代理数据
  agents: Record<string, Agent>
  favoriteAgents: string[]
  
  // UI 状态
  isLoading: boolean
  isSending: boolean
  typingUsers: Record<string, string[]> // conversationId -> userIds
  
  // 草稿和临时状态
  drafts: Record<string, string> // conversationId -> draft content
  searchQuery: string
  searchResults: Message[]
}

export interface ChatActions {
  // 对话管理
  loadConversations: () => Promise<void>
  createConversation: (params: CreateConversationParams) => Promise<string>
  updateConversation: (id: string, updates: Partial<Conversation>) => void
  deleteConversation: (id: string) => Promise<void>
  setActiveConversation: (id: string | null) => void
  
  // 消息管理
  loadMessages: (conversationId: string, options?: LoadMessagesOptions) => Promise<void>
  sendMessage: (conversationId: string, content: string, options?: SendMessageOptions) => Promise<void>
  updateMessage: (messageId: string, updates: Partial<Message>) => void
  deleteMessage: (messageId: string) => Promise<void>
  
  // 实时功能
  handleRealtimeMessage: (message: Message) => void
  setTypingStatus: (conversationId: string, userId: string, isTyping: boolean) => void
  
  // 代理管理
  loadAgents: () => Promise<void>
  toggleFavoriteAgent: (agentId: string) => void
  
  // 搜索功能
  searchMessages: (query: string) => Promise<void>
  clearSearch: () => void
  
  // 草稿管理
  saveDraft: (conversationId: string, content: string) => void
  loadDraft: (conversationId: string) => string
  clearDraft: (conversationId: string) => void
  
  // 状态重置
  clearAll: () => void
}

export type ChatSlice = {
  chat: ChatState & ChatActions
}

const initialChatState: ChatState = {
  conversations: {},
  conversationList: [],
  activeConversationId: null,
  messages: {},
  conversationMessages: {},
  agents: {},
  favoriteAgents: [],
  isLoading: false,
  isSending: false,
  typingUsers: {},
  drafts: {},
  searchQuery: '',
  searchResults: []
}

export const createChatSlice: StateCreator<
  ChatSlice,
  [["zustand/immer", never], ["zustand/devtools", never], ["zustand/persist", unknown]],
  [],
  ChatSlice
> = (set, get) => ({
  chat: {
    ...initialChatState,
    
    // 加载对话列表
    loadConversations: async () => {
      set((state) => {
        state.chat.isLoading = true
      })
      
      try {
        const response = await chatApi.getConversations()
        const conversations = response.data.conversations
        
        set((state) => {
          // 规范化存储对话数据
          state.chat.conversations = {}
          state.chat.conversationList = []
          
          conversations.forEach((conv: Conversation) => {
            state.chat.conversations[conv.id] = conv
            state.chat.conversationList.push(conv.id)
          })
          
          // 按更新时间排序
          state.chat.conversationList.sort((a, b) => {
            const convA = state.chat.conversations[a]
            const convB = state.chat.conversations[b]
            return new Date(convB.updatedAt).getTime() - new Date(convA.updatedAt).getTime()
          })
          
          state.chat.isLoading = false
        })
        
      } catch (error) {
        set((state) => {
          state.chat.isLoading = false
        })
        throw error
      }
    },
    
    // 创建新对话
    createConversation: async (params) => {
      try {
        const response = await chatApi.createConversation(params)
        const newConversation = response.data.conversation
        
        set((state) => {
          // 添加新对话到开头
          state.chat.conversations[newConversation.id] = newConversation
          state.chat.conversationList.unshift(newConversation.id)
          
          // 初始化消息列表
          state.chat.conversationMessages[newConversation.id] = []
        })
        
        return newConversation.id
        
      } catch (error) {
        throw error
      }
    },
    
    // 发送消息
    sendMessage: async (conversationId, content, options = {}) => {
      const tempMessageId = `temp_${Date.now()}`
      const tempMessage: Message = {
        id: tempMessageId,
        conversationId,
        content,
        senderId: get().auth.user?.id || '',
        senderType: 'user',
        type: 'text',
        timestamp: new Date().toISOString(),
        metadata: {},
        reactions: [],
        replyTo: options.replyTo || null,
        editedAt: null
      }
      
      // 乐观更新 - 立即显示用户消息
      set((state) => {
        state.chat.messages[tempMessageId] = tempMessage
        
        if (!state.chat.conversationMessages[conversationId]) {
          state.chat.conversationMessages[conversationId] = []
        }
        state.chat.conversationMessages[conversationId].push(tempMessageId)
        
        // 更新对话的最后消息时间
        if (state.chat.conversations[conversationId]) {
          state.chat.conversations[conversationId].updatedAt = tempMessage.timestamp
        }
        
        state.chat.isSending = true
      })
      
      try {
        const response = await chatApi.sendMessage(conversationId, {
          content,
          type: 'text',
          replyTo: options.replyTo,
          metadata: options.metadata
        })
        
        const serverMessage = response.data.message
        
        set((state) => {
          // 用服务器返回的消息替换临时消息
          delete state.chat.messages[tempMessageId]
          state.chat.messages[serverMessage.id] = serverMessage
          
          // 更新消息列表
          const messageList = state.chat.conversationMessages[conversationId]
          const tempIndex = messageList.findIndex(id => id === tempMessageId)
          if (tempIndex !== -1) {
            messageList[tempIndex] = serverMessage.id
          }
          
          state.chat.isSending = false
        })
        
        // 清理草稿
        get().chat.clearDraft(conversationId)
        
      } catch (error) {
        // 发送失败，移除临时消息
        set((state) => {
          delete state.chat.messages[tempMessageId]
          
          const messageList = state.chat.conversationMessages[conversationId]
          const tempIndex = messageList.findIndex(id => id === tempMessageId)
          if (tempIndex !== -1) {
            messageList.splice(tempIndex, 1)
          }
          
          state.chat.isSending = false
        })
        
        throw error
      }
    },
    
    // 处理实时消息
    handleRealtimeMessage: (message) => {
      set((state) => {
        // 添加新消息
        state.chat.messages[message.id] = message
        
        // 更新对话消息列表
        if (!state.chat.conversationMessages[message.conversationId]) {
          state.chat.conversationMessages[message.conversationId] = []
        }
        
        // 检查消息是否已存在（避免重复）
        const messageList = state.chat.conversationMessages[message.conversationId]
        if (!messageList.includes(message.id)) {
          messageList.push(message.id)
          
          // 按时间戳排序
          messageList.sort((a, b) => {
            const msgA = state.chat.messages[a]
            const msgB = state.chat.messages[b]
            return new Date(msgA.timestamp).getTime() - new Date(msgB.timestamp).getTime()
          })
        }
        
        // 更新对话信息
        if (state.chat.conversations[message.conversationId]) {
          state.chat.conversations[message.conversationId].updatedAt = message.timestamp
          state.chat.conversations[message.conversationId].lastMessage = {
            id: message.id,
            content: message.content,
            senderId: message.senderId,
            timestamp: message.timestamp,
            type: message.type
          }
          
          // 更新未读计数（如果不是当前活跃对话）
          if (state.chat.activeConversationId !== message.conversationId) {
            state.chat.conversations[message.conversationId].unreadCount += 1
          }
        }
        
        // 重新排序对话列表
        state.chat.conversationList.sort((a, b) => {
          const convA = state.chat.conversations[a]
          const convB = state.chat.conversations[b]
          return new Date(convB.updatedAt).getTime() - new Date(convA.updatedAt).getTime()
        })
      })
    },
    
    // 设置输入状态
    setTypingStatus: (conversationId, userId, isTyping) => {
      set((state) => {
        if (!state.chat.typingUsers[conversationId]) {
          state.chat.typingUsers[conversationId] = []
        }
        
        const typingList = state.chat.typingUsers[conversationId]
        const userIndex = typingList.indexOf(userId)
        
        if (isTyping && userIndex === -1) {
          typingList.push(userId)
        } else if (!isTyping && userIndex !== -1) {
          typingList.splice(userIndex, 1)
        }
      })
    },
    
    // 保存草稿
    saveDraft: (conversationId, content) => {
      set((state) => {
        if (content.trim()) {
          state.chat.drafts[conversationId] = content
        } else {
          delete state.chat.drafts[conversationId]
        }
      })
    },
    
    // 加载草稿
    loadDraft: (conversationId) => {
      return get().chat.drafts[conversationId] || ''
    },
    
    // 清理草稿
    clearDraft: (conversationId) => {
      set((state) => {
        delete state.chat.drafts[conversationId]
      })
    },
    
    // 清理所有状态
    clearAll: () => {
      set((state) => {
        Object.assign(state.chat, initialChatState)
      })
    }
  }
})
```

## React Query 服务端状态管理

### 1. Query Client 配置

```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// 创建 Query Client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // 全局查询配置
      staleTime: 5 * 60 * 1000, // 5分钟数据被视为新鲜
      cacheTime: 10 * 60 * 1000, // 10分钟缓存时间
      retry: (failureCount, error) => {
        // 自定义重试逻辑
        if (error?.status === 401 || error?.status === 403) {
          return false // 认证错误不重试
        }
        return failureCount < 3 // 最多重试3次
      },
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // 指数退避
      refetchOnWindowFocus: false, // 关闭窗口聚焦时重新获取
      refetchOnMount: true, // 组件挂载时重新获取
      refetchOnReconnect: true, // 网络重连时重新获取
      suspense: false, // 不使用 Suspense
    },
    mutations: {
      // 全局变更配置
      retry: false, // 变更操作不重试
      onError: (error) => {
        // 全局错误处理
        console.error('Mutation error:', error)
        // 可以在这里触发全局错误通知
      }
    }
  }
})

// 错误边界处理
queryClient.setMutationDefaults(['auth', 'login'], {
  mutationFn: async (variables) => {
    const response = await authApi.login(variables)
    return response.data
  },
  onSuccess: (data) => {
    // 登录成功后更新全局状态
    useStore.getState().auth.updateTokens(data.tokens)
    useStore.getState().auth.updateUser(data.user)
  },
  onError: (error) => {
    // 登录失败处理
    console.error('Login failed:', error)
  }
})
```

### 2. Query Hooks 设计

#### 2.1 对话相关查询
```typescript
// hooks/queries/useConversations.ts
import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { chatApi } from '@/lib/api/chatApi'
import { useStore } from '@/store'

// 查询键工厂
export const conversationKeys = {
  all: ['conversations'] as const,
  lists: () => [...conversationKeys.all, 'list'] as const,
  list: (filters: string) => [...conversationKeys.lists(), filters] as const,
  details: () => [...conversationKeys.all, 'detail'] as const,
  detail: (id: string) => [...conversationKeys.details(), id] as const,
  messages: (id: string) => [...conversationKeys.detail(id), 'messages'] as const,
}

// 获取对话列表
export const useConversations = (filters?: ConversationFilters) => {
  return useQuery({
    queryKey: conversationKeys.list(JSON.stringify(filters || {})),
    queryFn: async () => {
      const response = await chatApi.getConversations(filters)
      return response.data
    },
    onSuccess: (data) => {
      // 更新全局状态
      const { chat } = useStore.getState()
      chat.updateConversations(data.conversations)
    },
    select: (data) => ({
      conversations: data.conversations,
      pagination: data.pagination
    })
  })
}

// 无限滚动对话列表
export const useInfiniteConversations = (filters?: ConversationFilters) => {
  return useInfiniteQuery({
    queryKey: conversationKeys.list(`infinite-${JSON.stringify(filters || {})}`),
    queryFn: async ({ pageParam = 0 }) => {
      const response = await chatApi.getConversations({
        ...filters,
        offset: pageParam,
        limit: 20
      })
      return response.data
    },
    getNextPageParam: (lastPage) => {
      const { pagination } = lastPage
      return pagination.hasMore ? pagination.offset + pagination.limit : undefined
    },
    select: (data) => ({
      pages: data.pages,
      conversations: data.pages.flatMap(page => page.conversations),
      hasNextPage: !!data.pageParams.length
    })
  })
}

// 获取对话详情
export const useConversation = (conversationId: string) => {
  return useQuery({
    queryKey: conversationKeys.detail(conversationId),
    queryFn: async () => {
      const response = await chatApi.getConversation(conversationId)
      return response.data.conversation
    },
    enabled: !!conversationId, // 只有当 ID 存在时才执行查询
    staleTime: 2 * 60 * 1000, // 对话详情2分钟内保持新鲜
  })
}

// 获取对话消息
export const useConversationMessages = (conversationId: string) => {
  return useInfiniteQuery({
    queryKey: conversationKeys.messages(conversationId),
    queryFn: async ({ pageParam }) => {
      const response = await chatApi.getMessages(conversationId, {
        before: pageParam,
        limit: 50
      })
      return response.data
    },
    getNextPageParam: (lastPage) => {
      return lastPage.pagination.hasMore ? lastPage.pagination.nextCursor : undefined
    },
    enabled: !!conversationId,
    select: (data) => ({
      pages: data.pages,
      messages: data.pages.flatMap(page => page.messages).reverse(), // 反转消息顺序
      hasNextPage: data.hasNextPage
    }),
    onSuccess: (data) => {
      // 将消息同步到全局状态
      const { chat } = useStore.getState()
      chat.updateMessages(conversationId, data.messages)
    }
  })
}

// 创建对话
export const useCreateConversation = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (params: CreateConversationParams) => {
      const response = await chatApi.createConversation(params)
      return response.data
    },
    onSuccess: (data) => {
      // 乐观更新：添加新对话到缓存
      queryClient.setQueryData<ConversationsData>(
        conversationKeys.lists(),
        (oldData) => {
          if (!oldData) return oldData
          
          return {
            ...oldData,
            conversations: [data.conversation, ...oldData.conversations]
          }
        }
      )
      
      // 更新全局状态
      const { chat } = useStore.getState()
      chat.addConversation(data.conversation)
      
      // 预取消息列表
      queryClient.prefetchQuery({
        queryKey: conversationKeys.messages(data.conversation.id),
        queryFn: async () => ({ messages: [], pagination: { hasMore: false } })
      })
    },
    onError: (error) => {
      console.error('Failed to create conversation:', error)
    }
  })
}

// 发送消息
export const useSendMessage = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (params: SendMessageParams) => {
      const response = await chatApi.sendMessage(params.conversationId, params)
      return response.data
    },
    onMutate: async (params) => {
      // 取消相关的查询以避免竞态
      await queryClient.cancelQueries({
        queryKey: conversationKeys.messages(params.conversationId)
      })
      
      // 获取当前消息列表快照
      const previousMessages = queryClient.getQueryData(
        conversationKeys.messages(params.conversationId)
      )
      
      // 乐观更新：立即添加用户消息
      const tempMessage: Message = {
        id: `temp_${Date.now()}`,
        conversationId: params.conversationId,
        content: params.content,
        senderId: useStore.getState().auth.user?.id || '',
        senderType: 'user',
        type: 'text',
        timestamp: new Date().toISOString(),
        metadata: {},
        reactions: [],
        replyTo: params.replyTo || null,
        editedAt: null
      }
      
      queryClient.setQueryData<InfiniteData<MessagesResponse>>(
        conversationKeys.messages(params.conversationId),
        (oldData) => {
          if (!oldData) return oldData
          
          const newFirstPage = {
            ...oldData.pages[0],
            messages: [...oldData.pages[0].messages, tempMessage]
          }
          
          return {
            ...oldData,
            pages: [newFirstPage, ...oldData.pages.slice(1)]
          }
        }
      )
      
      return { previousMessages, tempMessage }
    },
    onSuccess: (data, params, context) => {
      // 用真实消息替换临时消息
      queryClient.setQueryData<InfiniteData<MessagesResponse>>(
        conversationKeys.messages(params.conversationId),
        (oldData) => {
          if (!oldData) return oldData
          
          const newFirstPage = {
            ...oldData.pages[0],
            messages: oldData.pages[0].messages.map(msg => 
              msg.id === context?.tempMessage.id ? data.message : msg
            )
          }
          
          return {
            ...oldData,
            pages: [newFirstPage, ...oldData.pages.slice(1)]
          }
        }
      )
      
      // 更新对话列表中的最后消息
      queryClient.setQueryData<ConversationsData>(
        conversationKeys.lists(),
        (oldData) => {
          if (!oldData) return oldData
          
          return {
            ...oldData,
            conversations: oldData.conversations.map(conv =>
              conv.id === params.conversationId
                ? {
                    ...conv,
                    lastMessage: {
                      id: data.message.id,
                      content: data.message.content,
                      senderId: data.message.senderId,
                      timestamp: data.message.timestamp,
                      type: data.message.type
                    },
                    updatedAt: data.message.timestamp
                  }
                : conv
            )
          }
        }
      )
    },
    onError: (error, params, context) => {
      // 发送失败，恢复之前的状态
      if (context?.previousMessages) {
        queryClient.setQueryData(
          conversationKeys.messages(params.conversationId),
          context.previousMessages
        )
      }
    },
    onSettled: (data, error, params) => {
      // 无论成功失败，都重新获取最新数据
      queryClient.invalidateQueries({
        queryKey: conversationKeys.messages(params.conversationId)
      })
    }
  })
}
```

### 3. 实时数据同步

#### 3.1 WebSocket 事件处理
```typescript
// hooks/useRealtimeSync.ts
import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useStore } from '@/store'
import { conversationKeys } from '@/hooks/queries/useConversations'

export const useRealtimeSync = () => {  
  const queryClient = useQueryClient()
  const { chat } = useStore()
  const { socket, isConnected } = useWebSocket()
  
  useEffect(() => {
    if (!socket || !isConnected) return
    
    // 监听新消息事件
    const handleNewMessage = (event: RealtimeMessageEvent) => {
      const { message } = event.data
      
      // 更新全局状态
      chat.handleRealtimeMessage(message)
      
      // 更新 React Query 缓存
      queryClient.setQueryData<InfiniteData<MessagesResponse>>(
        conversationKeys.messages(message.conversationId),
        (oldData) => {
          if (!oldData) return oldData
          
          // 检查消息是否已存在
          const messageExists = oldData.pages.some(page => 
            page.messages.some(msg => msg.id === message.id)
          )
          
          if (messageExists) return oldData
          
          // 添加新消息到第一页
          const newFirstPage = {
            ...oldData.pages[0],
            messages: [...oldData.pages[0].messages, message]
          }
          
          return {
            ...oldData,
            pages: [newFirstPage, ...oldData.pages.slice(1)]
          }
        }
      )
      
      // 更新对话列表缓存
      queryClient.setQueryData<ConversationsData>(
        conversationKeys.lists(),
        (oldData) => {
          if (!oldData) return oldData
          
          return {
            ...oldData,
            conversations: oldData.conversations.map(conv =>
              conv.id === message.conversationId
                ? {
                    ...conv,
                    lastMessage: {
                      id: message.id,
                      content: message.content,
                      senderId: message.senderId,
                      timestamp: message.timestamp,
                      type: message.type
                    },
                    updatedAt: message.timestamp,
                    unreadCount: conv.id === chat.activeConversationId ? 0 : conv.unreadCount + 1
                  }
                : conv
            )
          }
        }
      )
    }
    
    // 监听输入状态事件
    const handleTypingStatus = (event: TypingStatusEvent) => {
      const { conversationId, userId, isTyping } = event.data
      chat.setTypingStatus(conversationId, userId, isTyping)
    }
    
    // 监听对话更新事件
    const handleConversationUpdate = (event: ConversationUpdateEvent) => {
      const { conversation } = event.data
      
      // 更新对话详情缓存
      queryClient.setQueryData(
        conversationKeys.detail(conversation.id),
        conversation
      )
      
      // 更新对话列表缓存
      queryClient.setQueryData<ConversationsData>(
        conversationKeys.lists(),
        (oldData) => {
          if (!oldData) return oldData
          
          return {
            ...oldData,
            conversations: oldData.conversations.map(conv =>
              conv.id === conversation.id ? conversation : conv
            )
          }
        }
      )
    }
    
    // 监听在线状态事件
    const handlePresenceUpdate = (event: PresenceUpdateEvent) => {
      const { userId, status } = event.data
      // 可以在这里更新用户在线状态的缓存
    }
    
    // 注册事件监听器
    socket.on('message.new', handleNewMessage)
    socket.on('typing.status', handleTypingStatus)
    socket.on('conversation.update', handleConversationUpdate) 
    socket.on('presence.update', handlePresenceUpdate)
    
    // 清理函数
    return () => {
      socket.off('message.new', handleNewMessage)
      socket.off('typing.status', handleTypingStatus)
      socket.off('conversation.update', handleConversationUpdate)
      socket.off('presence.update', handlePresenceUpdate)
    }
  }, [socket, isConnected, chat, queryClient])
  
  // 处理连接状态变化
  useEffect(() => {
    if (isConnected) {
      // 连接成功后，可以重新获取可能错过的数据
      queryClient.invalidateQueries({
        queryKey: conversationKeys.all
      })
    }
  }, [isConnected, queryClient])
}
```

## 缓存策略和数据同步

### 1. 多层缓存架构

```typescript
// lib/cache/cacheManager.ts
interface CacheLayer {
  name: string
  storage: Storage
  ttl: number // 生存时间（毫秒）
  maxSize?: number // 最大条目数
}

class CacheManager {
  private layers: Map<string, CacheLayer> = new Map()
  
  constructor() {
    // 定义缓存层级
    this.layers.set('memory', {
      name: 'memory',
      storage: new MemoryStorage(),
      ttl: 5 * 60 * 1000, // 5分钟
      maxSize: 1000
    })
    
    this.layers.set('session', {
      name: 'session',
      storage: sessionStorage,
      ttl: 60 * 60 * 1000, // 1小时
    })
    
    this.layers.set('local', {
      name: 'local', 
      storage: localStorage,
      ttl: 24 * 60 * 60 * 1000, // 24小时
    })
    
    this.layers.set('indexeddb', {
      name: 'indexeddb',
      storage: new IndexedDBStorage(),
      ttl: 7 * 24 * 60 * 60 * 1000, // 7天
    })
  }
  
  // 从缓存获取数据（按层级顺序）
  async get<T>(key: string): Promise<T | null> {
    for (const [layerName, layer] of this.layers) {
      try {
        const cachedItem = await this.getFromLayer(layer, key)
        if (cachedItem && !this.isExpired(cachedItem)) {
          // 如果在较慢的层找到，提升到较快的层
          if (layerName !== 'memory') {
            await this.promoteToFasterLayers(key, cachedItem, layerName)
          }
          return cachedItem.data
        }
      } catch (error) {
        console.warn(`Failed to get from ${layerName} cache:`, error)
      }
    }
    return null
  }
  
  // 设置缓存数据（写入所有层级）
  async set<T>(key: string, data: T, options?: CacheOptions): Promise<void> {
    const cachedItem: CachedItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: options?.ttl,
      metadata: options?.metadata
    }
    
    // 并行写入所有层级
    const writePromises = Array.from(this.layers.values()).map(layer =>
      this.setToLayer(layer, key, cachedItem).catch(error => {
        console.warn(`Failed to write to ${layer.name} cache:`, error)
      })
    )
    
    await Promise.allSettled(writePromises)
  }
  
  // 缓存失效
  async invalidate(pattern: string | RegExp): Promise<void> {
    const invalidatePromises = Array.from(this.layers.values()).map(layer =>
      this.invalidateFromLayer(layer, pattern).catch(error => {
        console.warn(`Failed to invalidate from ${layer.name} cache:`, error)
      })
    )
    
    await Promise.allSettled(invalidatePromises)
  }
  
  // 数据同步策略
  async syncWithServer(keys: string[]): Promise<void> {
    for (const key of keys) {
      try {
        const cachedData = await this.get(key)
        const serverData = await this.fetchFromServer(key)
        
        if (!cachedData || this.hasDataChanged(cachedData, serverData)) {
          await this.set(key, serverData)
          
          // 通知订阅者数据已更新
          this.notifySubscribers(key, serverData)
        }
      } catch (error) {
        console.error(`Failed to sync ${key}:`, error)
      }
    }
  }
  
  // 冲突解决策略
  async resolveConflict<T>(
    key: string, 
    localData: T, 
    serverData: T, 
    strategy: ConflictResolutionStrategy = 'server-wins'
  ): Promise<T> {
    switch (strategy) {
      case 'server-wins':
        await this.set(key, serverData)
        return serverData
        
      case 'client-wins':
        await this.uploadToServer(key, localData)
        return localData
        
      case 'merge':
        const mergedData = await this.mergeData(localData, serverData)
        await this.set(key, mergedData)
        await this.uploadToServer(key, mergedData)
        return mergedData
        
      case 'manual':
        // 触发用户手动解决冲突的 UI
        return await this.promptUserResolution(key, localData, serverData)
        
      default:
        throw new Error(`Unknown conflict resolution strategy: ${strategy}`)
    }
  }
}

export const cacheManager = new CacheManager()
```

### 2. 离线数据管理

```typescript
// lib/offline/offlineManager.ts
class OfflineManager {
  private requestQueue: OfflineRequest[] = []
  private isOnline = navigator.onLine
  private syncInProgress = false
  
  constructor() {
    // 监听网络状态变化
    window.addEventListener('online', this.handleOnline.bind(this))
    window.addEventListener('offline', this.handleOffline.bind(this))
    
    // 从本地存储恢复请求队列
    this.loadRequestQueue()
  }
  
  // 队列离线请求
  async queueRequest(request: OfflineRequest): Promise<void> {
    this.requestQueue.push({
      ...request,
      id: generateUniqueId(),
      timestamp: Date.now(),
      retryCount: 0
    })
    
    await this.saveRequestQueue()
    
    // 如果在线，立即尝试同步
    if (this.isOnline) {
      this.syncQueue()
    }
  }
  
  // 处理上线事件
  private async handleOnline(): Promise<void> {
    this.isOnline = true
    console.log('Network connection restored')
    
    // 触发数据同步
    await this.syncQueue()
    
    // 重新获取可能错过的实时更新
    queryClient.invalidateQueries()
  }
  
  // 处理离线事件
  private handleOffline(): void {
    this.isOnline = false
    console.log('Network connection lost')
    
    // 通知用户进入离线模式
    useStore.getState().ui.showNotification({
      type: 'warning',
      message: '网络连接已断开，将在离线模式下工作',
      persistent: true
    })
  }
  
  // 同步请求队列
  private async syncQueue(): Promise<void> {
    if (this.syncInProgress || !this.isOnline || this.requestQueue.length === 0) {
      return
    }
    
    this.syncInProgress = true
    
    try {
      const pendingRequests = [...this.requestQueue]
      
      for (const request of pendingRequests) {
        try {
          await this.executeRequest(request)
          
          // 请求成功，从队列中移除
          this.requestQueue = this.requestQueue.filter(r => r.id !== request.id)
          
        } catch (error) {
          request.retryCount++
          
          // 如果重试次数超过限制，标记为失败
          if (request.retryCount >= 3) {
            request.status = 'failed'
            request.error = error.message
          }
        }
      }
      
      await this.saveRequestQueue()
      
      // 如果还有未同步的请求，延迟后重试
      if (this.requestQueue.some(r => r.status === 'pending')) {
        setTimeout(() => this.syncQueue(), 5000)
      }
      
    } finally {
      this.syncInProgress = false
    }
  }
  
  // 执行单个请求
  private async executeRequest(request: OfflineRequest): Promise<any> {
    const { method, url, data, headers } = request
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: data ? JSON.stringify(data) : undefined
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  // 检查数据一致性
  async checkDataConsistency(): Promise<ConsistencyReport> {
    const report: ConsistencyReport = {
      conflicts: [],
      outdatedItems: [],
      missingItems: []
    }
    
    // 检查关键数据的一致性
    const criticalKeys = [
      'conversations',
      'user-profile',
      'settings',
      'agents'
    ]
    
    for (const key of criticalKeys) {
      try {
        const localData = await cacheManager.get(key)
        const serverData = await this.fetchFromServer(key)
        
        if (localData && serverData) {
          if (this.hasConflict(localData, serverData)) {
            report.conflicts.push({
              key,
              localData,
              serverData,
              lastModified: {
                local: localData.updatedAt,
                server: serverData.updatedAt
              }
            })
          }
        } else if (localData && !serverData) {
          report.missingItems.push({ key, data: localData })
        } else if (!localData && serverData) {
          report.outdatedItems.push({ key, data: serverData })
        }
        
      } catch (error) {
        console.error(`Failed to check consistency for ${key}:`, error)
      }
    }
    
    return report
  }
}

export const offlineManager = new OfflineManager()
```

---

**数据流设计版本**: v1.0  
**最后更新**: 2025-01-08  
**兼容性**: Zustand 4.4.7 + React Query 5.0 + WebSocket

这个数据流和状态管理架构为 Connet.AI 提供了：

1. **清晰的数据流**: 单向数据流确保状态变化的可预测性
2. **分层状态管理**: 不同类型的状态使用最适合的管理方案
3. **实时同步**: WebSocket 集成确保数据的实时性
4. **离线支持**: 完整的离线模式和数据同步机制
5. **性能优化**: 智能缓存和乐观更新提升用户体验
6. **冲突解决**: 多客户端协作的数据冲突处理

这将为用户提供流畅、可靠的 AI 协作体验。
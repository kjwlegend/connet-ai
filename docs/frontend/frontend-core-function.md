# Frontend Core Function Analysis & Implementation Plan (Updated)

## 概述 (Overview)

**更新说明**: 基于后端 FastAPI + Supabase 架构分析，后端已经提供了完整的 API 服务层、数据库模型、认证服务等。本文档重新聚焦于前端必需的核心功能，去掉已由后端提供的服务。

经过对当前前端应用代码的深入分析，发现应用已经完成了完整的 UI/UX 交互部分，包括组件架构、布局系统、主题切换等功能。但在前端特定的数据管理、UI 状态控制、用户交互逻辑等方面存在缺失。

## 后端已提供的服务 (Backend Provided Services)

### ✅ 后端已实现 (FastAPI + Supabase)

1. **完整的 API 服务层**

   - 认证 API (`/auth/*` - 登录/注册/刷新令牌)
   - 用户管理 API (`/users/*` - 用户 CRUD 操作)
   - 健康检查 API (`/health/*`)
   - 数据库模型 (User, Conversation, Message, Agent, Contact, Timeline 等)

2. **认证和授权系统**

   - Supabase 认证集成
   - JWT 令牌管理
   - 权限控制系统
   - 用户会话管理

3. **数据库层**

   - PostgreSQL + SQLModel
   - 完整的数据模型定义
   - Alembic 数据库迁移
   - Repository 模式实现

4. **实时通信**

   - WebSocket 支持
   - 实时消息推送
   - 在线状态管理
   - 事件总线系统

5. **AI 集成**

   - LangChain/LangGraph 框架
   - AI 代理系统
   - 智能体@提及处理
   - 上下文记忆管理

6. **文件管理**
   - Supabase Storage 集成
   - 文件上传/下载
   - 权限控制
   - 元数据管理

## 前端需要实现的核心功能 (Frontend-Specific Implementation)

### ❌ 缺失的前端核心功能

## 1. 前端 API 客户端层 (Frontend API Client Layer)

### 1.1 HTTP 客户端配置和管理

```typescript
// 文件位置: src/lib/api/client.ts (需要完善)
interface ApiClientConfig {
  // 基础配置
  baseURL: string
  timeout: number

  // 认证配置
  getAuthToken: () => string | null
  onTokenExpired: () => void

  // 重试配置
  retryAttempts: number
  retryDelay: number

  // 缓存配置
  enableCache: boolean
  cacheTimeout: number
}

class ApiClient {
  // HTTP 请求方法
  async get<T>(endpoint: string, params?: any): Promise<T>
  async post<T>(endpoint: string, data?: any): Promise<T>
  async put<T>(endpoint: string, data?: any): Promise<T>
  async delete<T>(endpoint: string): Promise<T>

  // 文件上传
  async uploadFile(file: File, metadata?: any): Promise<UploadResponse>
  async uploadFiles(files: File[]): Promise<UploadResponse[]>

  // 请求拦截器
  setRequestInterceptor(interceptor: RequestInterceptor): void
  setResponseInterceptor(interceptor: ResponseInterceptor): void

  // 错误处理
  setErrorHandler(handler: ErrorHandler): void
}
```

### 1.2 API 端点调用封装

```typescript
// 文件位置: src/lib/api/endpoints/auth.ts (新建)
export class AuthApi {
  constructor(private client: ApiClient) {}

  async login(credentials: LoginCredentials): Promise<LoginResponse>
  async register(userData: RegisterData): Promise<UserResponse>
  async logout(): Promise<void>
  async refreshToken(refreshToken: string): Promise<TokenResponse>
  async getCurrentUser(): Promise<UserResponse>
  async updateProfile(data: UpdateProfileData): Promise<UserResponse>
}

// 文件位置: src/lib/api/endpoints/chat.ts (新建)
export class ChatApi {
  constructor(private client: ApiClient) {}

  async getConversations(
    params: ConversationParams
  ): Promise<PaginatedResponse<Conversation>>
  async createConversation(data: CreateConversationData): Promise<Conversation>
  async getMessages(
    conversationId: string,
    params: MessageParams
  ): Promise<PaginatedResponse<Message>>
  async sendMessage(
    conversationId: string,
    data: SendMessageData
  ): Promise<Message>
  async updateMessage(messageId: string, content: string): Promise<Message>
  async deleteMessage(messageId: string): Promise<void>
}

// 文件位置: src/lib/api/endpoints/agents.ts (新建)
export class AgentsApi {
  constructor(private client: ApiClient) {}

  async getAgents(params: AgentParams): Promise<PaginatedResponse<Agent>>
  async getAgent(agentId: string): Promise<Agent>
  async searchAgents(query: string): Promise<Agent[]>
  async mentionAgent(
    agentId: string,
    conversationId: string,
    context: string
  ): Promise<void>
}

// 文件位置: src/lib/api/endpoints/files.ts (新建)
export class FilesApi {
  constructor(private client: ApiClient) {}

  async getFiles(params: FileParams): Promise<PaginatedResponse<File>>
  async uploadFile(file: File, metadata?: FileMetadata): Promise<UploadResponse>
  async downloadFile(fileId: string): Promise<Blob>
  async deleteFile(fileId: string): Promise<void>
  async getFilePreview(fileId: string): Promise<string>
}
```

## 2. React Query 数据查询层 (React Query Integration)

### 2.1 查询 Hooks

```typescript
// 文件位置: src/lib/api/queries/auth.ts (新建)
export const useCurrentUser = () =>
  useQuery({
    queryKey: ['auth', 'currentUser'],
    queryFn: () => authApi.getCurrentUser(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })

export const useUserProfile = (userId: string) =>
  useQuery({
    queryKey: ['users', userId],
    queryFn: () => authApi.getUserProfile(userId),
    enabled: !!userId,
  })

// 文件位置: src/lib/api/queries/chat.ts (新建)
export const useConversations = (params: ConversationParams) =>
  useInfiniteQuery({
    queryKey: ['conversations', params],
    queryFn: ({ pageParam = 1 }) =>
      chatApi.getConversations({ ...params, page: pageParam }),
    getNextPageParam: (lastPage) =>
      lastPage.hasNext ? lastPage.page + 1 : undefined,
  })

export const useMessages = (conversationId: string) =>
  useInfiniteQuery({
    queryKey: ['messages', conversationId],
    queryFn: ({ pageParam = 1 }) =>
      chatApi.getMessages(conversationId, { page: pageParam }),
    getNextPageParam: (lastPage) =>
      lastPage.hasNext ? lastPage.page + 1 : undefined,
    enabled: !!conversationId,
  })

export const useConversation = (conversationId: string) =>
  useQuery({
    queryKey: ['conversations', conversationId],
    queryFn: () => chatApi.getConversation(conversationId),
    enabled: !!conversationId,
  })

// 文件位置: src/lib/api/queries/agents.ts (新建)
export const useAgents = (params: AgentParams) =>
  useQuery({
    queryKey: ['agents', params],
    queryFn: () => agentsApi.getAgents(params),
  })

export const useAgentSearch = (query: string) =>
  useQuery({
    queryKey: ['agents', 'search', query],
    queryFn: () => agentsApi.searchAgents(query),
    enabled: query.length >= 2,
    debounceTime: 300,
  })

// 文件位置: src/lib/api/queries/files.ts (新建)
export const useFiles = (params: FileParams) =>
  useInfiniteQuery({
    queryKey: ['files', params],
    queryFn: ({ pageParam = 1 }) =>
      filesApi.getFiles({ ...params, page: pageParam }),
    getNextPageParam: (lastPage) =>
      lastPage.hasNext ? lastPage.page + 1 : undefined,
  })

export const useFile = (fileId: string) =>
  useQuery({
    queryKey: ['files', fileId],
    queryFn: () => filesApi.getFile(fileId),
    enabled: !!fileId,
  })
```

### 2.2 变更 Hooks

```typescript
// 文件位置: src/lib/api/mutations/auth.ts (新建)
export const useLogin = () =>
  useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (data) => {
      // 存储 token
      localStorage.setItem('auth-token', data.access_token)
      // 更新用户缓存
      queryClient.setQueryData(['auth', 'currentUser'], data.user)
      // 显示成功提示
      toast.success('登录成功')
    },
    onError: (error) => {
      toast.error('登录失败: ' + error.message)
    },
  })

export const useLogout = () =>
  useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      // 清除本地存储
      localStorage.removeItem('auth-token')
      // 清除所有缓存
      queryClient.clear()
      // 重定向到登录页
      router.push('/login')
    },
  })

// 文件位置: src/lib/api/mutations/chat.ts (新建)
export const useSendMessage = () =>
  useMutation({
    mutationFn: ({
      conversationId,
      data,
    }: {
      conversationId: string
      data: SendMessageData
    }) => chatApi.sendMessage(conversationId, data),
    onSuccess: (message, { conversationId }) => {
      // 更新消息列表
      queryClient.setQueryData(['messages', conversationId], (old: any) => {
        if (!old) return old
        return {
          ...old,
          pages: old.pages.map((page: any, index: number) =>
            index === 0 ? { ...page, items: [message, ...page.items] } : page
          ),
        }
      })
    },
  })

export const useCreateConversation = () =>
  useMutation({
    mutationFn: (data: CreateConversationData) =>
      chatApi.createConversation(data),
    onSuccess: (conversation) => {
      // 更新对话列表
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      // 导航到新对话
      router.push(`/chat/${conversation.id}`)
    },
  })

// 文件位置: src/lib/api/mutations/files.ts (新建)
export const useUploadFiles = () =>
  useMutation({
    mutationFn: (files: File[]) => filesApi.uploadFiles(files),
    onSuccess: () => {
      // 刷新文件列表
      queryClient.invalidateQueries({ queryKey: ['files'] })
      toast.success('文件上传成功')
    },
    onError: (error) => {
      toast.error('文件上传失败: ' + error.message)
    },
  })
```

## 3. WebSocket 实时通信层 (WebSocket Integration)

### 3.1 WebSocket 客户端

```typescript
// 文件位置: src/lib/realtime/websocket.ts (新建)
interface WebSocketConfig {
  url: string
  reconnectInterval: number
  maxReconnectAttempts: number
  heartbeatInterval: number
}

class WebSocketClient extends EventTarget {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private heartbeatTimer?: NodeJS.Timeout

  constructor(private config: WebSocketConfig) {
    super()
  }

  // 连接管理
  connect(token: string): void
  disconnect(): void
  reconnect(): void

  // 消息发送
  send(type: string, data: any): void
  sendMessage(conversationId: string, content: string): void
  sendTyping(conversationId: string, isTyping: boolean): void

  // 事件监听
  onMessage(handler: (message: any) => void): void
  onUserPresence(handler: (presence: UserPresence) => void): void
  onConversationUpdate(handler: (update: ConversationUpdate) => void): void

  // 连接状态
  isConnected(): boolean
  getConnectionState(): 'connecting' | 'connected' | 'disconnected' | 'error'
}

// 文件位置: src/lib/realtime/hooks.ts (新建)
export const useWebSocket = () => {
  const [connectionState, setConnectionState] =
    useState<ConnectionState>('disconnected')
  const wsClient = useRef<WebSocketClient>()

  const connect = useCallback((token: string) => {
    if (!wsClient.current) {
      wsClient.current = new WebSocketClient(config)
    }
    wsClient.current.connect(token)
  }, [])

  const disconnect = useCallback(() => {
    wsClient.current?.disconnect()
  }, [])

  const send = useCallback((type: string, data: any) => {
    wsClient.current?.send(type, data)
  }, [])

  return {
    connectionState,
    connect,
    disconnect,
    send,
    isConnected: connectionState === 'connected',
  }
}

export const useRealtimeMessages = (conversationId: string) => {
  const queryClient = useQueryClient()
  const { wsClient } = useWebSocket()

  useEffect(() => {
    if (!wsClient || !conversationId) return

    const handleNewMessage = (message: Message) => {
      // 更新消息缓存
      queryClient.setQueryData(['messages', conversationId], (old: any) => {
        if (!old) return old
        return {
          ...old,
          pages: old.pages.map((page: any, index: number) =>
            index === 0 ? { ...page, items: [message, ...page.items] } : page
          ),
        }
      })
    }

    const handleMessageUpdate = (message: Message) => {
      // 更新特定消息
      queryClient.setQueryData(['messages', conversationId], (old: any) => {
        if (!old) return old
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((item: Message) =>
              item.id === message.id ? message : item
            ),
          })),
        }
      })
    }

    wsClient.onMessage(handleNewMessage)
    wsClient.onMessageUpdate(handleMessageUpdate)

    return () => {
      wsClient.off('message', handleNewMessage)
      wsClient.off('messageUpdate', handleMessageUpdate)
    }
  }, [conversationId, wsClient, queryClient])
}
```

## 4. 前端状态管理增强 (Frontend State Management)

### 4.1 UI 状态管理 (已部分实现，需要扩展)

```typescript
// 文件位置: src/store/slices/uiSlice.ts (需要扩展)
interface UIState {
  // 布局状态
  sidebarCollapsed: boolean
  middlePanelWidth: number
  currentView: 'chat' | 'contacts' | 'files' | 'timeline' | 'plugins'

  // 模态框状态
  modals: Modal[]

  // 通知状态
  toasts: Toast[]

  // 加载状态
  loadingStates: Record<string, boolean>

  // 聊天 UI 状态
  chatInputHeight: number
  selectedConversationId: string | null
  isTyping: Record<string, boolean> // conversationId -> isTyping

  // 文件管理 UI 状态
  fileViewMode: 'grid' | 'list' | 'table'
  selectedFileIds: string[]
  fileSortBy: 'name' | 'date' | 'size' | 'type'
  fileSortOrder: 'asc' | 'desc'

  // 搜索状态
  searchQuery: string
  searchResults: any[]
  isSearching: boolean
}

interface UIActions {
  // 布局操作
  toggleSidebar(): void
  setCurrentView(view: string): void
  setMiddlePanelWidth(width: number): void

  // 聊天 UI 操作
  setSelectedConversation(conversationId: string | null): void
  setChatInputHeight(height: number): void
  setTypingState(conversationId: string, isTyping: boolean): void

  // 文件管理操作
  setFileViewMode(mode: 'grid' | 'list' | 'table'): void
  selectFiles(fileIds: string[]): void
  setFileSorting(sortBy: string, sortOrder: 'asc' | 'desc'): void

  // 搜索操作
  setSearchQuery(query: string): void
  setSearchResults(results: any[]): void
  setSearching(isSearching: boolean): void
}
```

### 4.2 用户会话状态管理

```typescript
// 文件位置: src/store/slices/sessionSlice.ts (新建)
interface SessionState {
  // 认证状态
  isAuthenticated: boolean
  user: User | null
  token: string | null

  // 会话信息
  sessionStartTime: Date | null
  lastActivity: Date | null

  // 在线状态
  onlineStatus: 'online' | 'away' | 'busy' | 'offline'
  presenceData: UserPresence | null

  // 偏好设置
  preferences: UserPreferences

  // 权限
  permissions: string[]
  roles: string[]
}

interface SessionActions {
  // 认证操作
  setUser(user: User): void
  setToken(token: string): void
  clearSession(): void

  // 会话管理
  updateLastActivity(): void
  setOnlineStatus(status: string): void

  // 偏好设置
  updatePreferences(preferences: Partial<UserPreferences>): void

  // 权限检查
  hasPermission(permission: string): boolean
  hasRole(role: string): boolean
}
```

### 4.3 应用缓存状态管理

```typescript
// 文件位置: src/store/slices/cacheSlice.ts (新建)
interface CacheState {
  // 对话缓存
  conversationsCache: Record<string, Conversation>
  messagesCache: Record<string, Message[]> // conversationId -> messages

  // 用户缓存
  usersCache: Record<string, User>

  // 智能体缓存
  agentsCache: Record<string, Agent>

  // 文件缓存
  filesCache: Record<string, FileInfo>
  filePreviewCache: Record<string, string> // fileId -> previewUrl

  // 缓存元数据
  cacheTimestamps: Record<string, Date>
  cacheTTL: Record<string, number>
}

interface CacheActions {
  // 缓存操作
  setCacheItem(key: string, value: any, ttl?: number): void
  getCacheItem(key: string): any
  removeCacheItem(key: string): void
  clearCache(pattern?: string): void

  // 缓存验证
  isCacheValid(key: string): boolean
  cleanExpiredCache(): void

  // 智能缓存管理
  preloadConversationMessages(conversationId: string): void
  preloadUserData(userIds: string[]): void
}
```

## 5. 前端特定 Hooks (Frontend-Specific Hooks)

### 5.1 UI 交互 Hooks

```typescript
// 文件位置: src/hooks/useVirtualScroll.ts (新建)
export const useVirtualScroll = (
  items: any[],
  itemHeight: number,
  containerHeight: number
) => {
  const [scrollTop, setScrollTop] = useState(0)

  const startIndex = Math.floor(scrollTop / itemHeight)
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  )
  const visibleItems = items.slice(startIndex, endIndex)

  const totalHeight = items.length * itemHeight
  const offsetY = startIndex * itemHeight

  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll: (e: any) => setScrollTop(e.target.scrollTop),
  }
}

// 文件位置: src/hooks/useInfiniteScroll.ts (新建)
export const useInfiniteScroll = (
  hasNextPage: boolean,
  fetchNextPage: () => void,
  threshold = 100
) => {
  const [loadingMore, setLoadingMore] = useState(false)

  const handleScroll = useCallback(
    (e: any) => {
      const { scrollTop, scrollHeight, clientHeight } = e.target

      if (
        scrollHeight - scrollTop - clientHeight < threshold &&
        hasNextPage &&
        !loadingMore
      ) {
        setLoadingMore(true)
        fetchNextPage()
        setTimeout(() => setLoadingMore(false), 1000)
      }
    },
    [hasNextPage, fetchNextPage, threshold, loadingMore]
  )

  return { handleScroll, loadingMore }
}

// 文件位置: src/hooks/useMessageInput.ts (新建)
export const useMessageInput = (conversationId: string) => {
  const [message, setMessage] = useState('')
  const [isComposing, setIsComposing] = useState(false)
  const [mentions, setMentions] = useState<AgentMention[]>([])

  const sendMessageMutation = useSendMessage()
  const { send: sendTyping } = useWebSocket()

  const handleSend = useCallback(async () => {
    if (!message.trim()) return

    try {
      await sendMessageMutation.mutateAsync({
        conversationId,
        data: {
          content: message,
          mentions: mentions.map((m) => m.agentId),
        },
      })
      setMessage('')
      setMentions([])
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }, [message, mentions, conversationId, sendMessageMutation])

  const handleTyping = useCallback(
    (isTyping: boolean) => {
      sendTyping('typing', { conversationId, isTyping })
    },
    [conversationId, sendTyping]
  )

  return {
    message,
    setMessage,
    mentions,
    setMentions,
    isComposing,
    setIsComposing,
    handleSend,
    handleTyping,
    canSend: message.trim().length > 0 && !sendMessageMutation.isPending,
  }
}
```

### 5.2 数据同步 Hooks

```typescript
// 文件位置: src/hooks/useDataSync.ts (新建)
export const useDataSync = () => {
  const queryClient = useQueryClient()
  const { connectionState } = useWebSocket()

  // 重连后同步数据
  useEffect(() => {
    if (connectionState === 'connected') {
      // 重新获取最新数据
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      queryClient.invalidateQueries({ queryKey: ['messages'] })
    }
  }, [connectionState, queryClient])

  // 离线状态处理
  const syncOfflineChanges = useCallback(async () => {
    const offlineChanges = getOfflineChanges()

    for (const change of offlineChanges) {
      try {
        await applyChange(change)
        removeOfflineChange(change.id)
      } catch (error) {
        console.error('Failed to sync offline change:', error)
      }
    }
  }, [])

  return { syncOfflineChanges }
}

// 文件位置: src/hooks/useOfflineSupport.ts (新建)
export const useOfflineSupport = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [offlineQueue, setOfflineQueue] = useState<OfflineAction[]>([])

  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const queueAction = useCallback(
    (action: OfflineAction) => {
      if (!isOnline) {
        setOfflineQueue((queue) => [...queue, action])
        // 保存到 localStorage
        localStorage.setItem(
          'offline-queue',
          JSON.stringify([...offlineQueue, action])
        )
      }
    },
    [isOnline, offlineQueue]
  )

  const processQueue = useCallback(async () => {
    if (isOnline && offlineQueue.length > 0) {
      for (const action of offlineQueue) {
        try {
          await executeAction(action)
        } catch (error) {
          console.error('Failed to process offline action:', error)
        }
      }
      setOfflineQueue([])
      localStorage.removeItem('offline-queue')
    }
  }, [isOnline, offlineQueue])

  return { isOnline, queueAction, processQueue }
}
```

### 5.3 性能优化 Hooks

```typescript
// 文件位置: src/hooks/useOptimizedList.ts (新建)
export const useOptimizedList = <T>(
  items: T[],
  options: {
    pageSize?: number
    enableVirtualization?: boolean
    preloadNext?: boolean
  } = {}
) => {
  const {
    pageSize = 50,
    enableVirtualization = true,
    preloadNext = true,
  } = options

  const [visibleRange, setVisibleRange] = useState({ start: 0, end: pageSize })
  const [preloadedPages, setPreloadedPages] = useState(new Set([0]))

  const visibleItems = useMemo(() => {
    if (!enableVirtualization) return items
    return items.slice(visibleRange.start, visibleRange.end)
  }, [items, visibleRange, enableVirtualization])

  const updateVisibleRange = useCallback(
    (start: number, end: number) => {
      setVisibleRange({ start, end })

      if (preloadNext) {
        const nextPage = Math.floor(end / pageSize) + 1
        setPreloadedPages((pages) => new Set([...pages, nextPage]))
      }
    },
    [pageSize, preloadNext]
  )

  return {
    visibleItems,
    totalCount: items.length,
    updateVisibleRange,
    preloadedPages,
  }
}

// 文件位置: src/hooks/useImageOptimization.ts (新建)
export const useImageOptimization = () => {
  const [loadedImages, setLoadedImages] = useState(new Set<string>())
  const [imageCache, setImageCache] = useState(new Map<string, string>())

  const optimizeImage = useCallback(
    async (
      url: string,
      options: {
        width?: number
        height?: number
        quality?: number
        format?: 'webp' | 'jpeg' | 'png'
      } = {}
    ) => {
      const cacheKey = `${url}_${JSON.stringify(options)}`

      if (imageCache.has(cacheKey)) {
        return imageCache.get(cacheKey)!
      }

      try {
        const optimizedUrl = await optimizeImageUrl(url, options)
        setImageCache((cache) => new Map([...cache, [cacheKey, optimizedUrl]]))
        return optimizedUrl
      } catch (error) {
        console.error('Failed to optimize image:', error)
        return url
      }
    },
    [imageCache]
  )

  const preloadImage = useCallback(
    (url: string) => {
      if (loadedImages.has(url)) return Promise.resolve()

      return new Promise<void>((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          setLoadedImages((set) => new Set([...set, url]))
          resolve()
        }
        img.onerror = reject
        img.src = url
      })
    },
    [loadedImages]
  )

  return {
    optimizeImage,
    preloadImage,
    isImageLoaded: (url: string) => loadedImages.has(url),
  }
}
```

## 6. 工具函数和服务 (Frontend Utilities)

### 6.1 前端特定工具函数

```typescript
// 文件位置: src/lib/utils/dom.ts (新建)
export class DOMUtils {
  // 滚动管理
  static scrollToElement(
    element: HTMLElement,
    behavior: ScrollBehavior = 'smooth'
  ): void
  static scrollToTop(container?: HTMLElement): void
  static scrollToBottom(container?: HTMLElement): void

  // 元素尺寸
  static getElementRect(element: HTMLElement): DOMRect
  static isElementInViewport(element: HTMLElement): boolean
  static getScrollPosition(element: HTMLElement): { x: number; y: number }

  // 焦点管理
  static focusElement(element: HTMLElement): void
  static trapFocus(container: HTMLElement): () => void
  static restoreFocus(previousElement: HTMLElement | null): void

  // 复制到剪贴板
  static copyToClipboard(text: string): Promise<void>
  static readFromClipboard(): Promise<string>
}

// 文件位置: src/lib/utils/keyboard.ts (新建)
export class KeyboardUtils {
  // 快捷键处理
  static isModifierKey(event: KeyboardEvent): boolean
  static getKeyCombo(event: KeyboardEvent): string
  static matchesShortcut(event: KeyboardEvent, shortcut: string): boolean

  // 导航
  static handleArrowNavigation(
    event: KeyboardEvent,
    items: HTMLElement[],
    currentIndex: number
  ): number

  // 输入处理
  static preventDefaultKeyActions(event: KeyboardEvent, keys: string[]): void
}

// 文件位置: src/lib/utils/format.ts (新建)
export class FormatUtils {
  // 消息格式化
  static formatMessageContent(
    content: string,
    options?: {
      parseUrls?: boolean
      parseMentions?: boolean
      parseMarkdown?: boolean
    }
  ): string

  static highlightMentions(content: string, mentions: AgentMention[]): string
  static extractUrls(content: string): string[]
  static formatCodeBlocks(content: string): string

  // 时间格式化
  static formatRelativeTime(date: Date | string): string
  static formatChatTime(date: Date | string): string
  static formatFileDate(date: Date | string): string

  // 文件格式化
  static formatFileSize(bytes: number): string
  static getFileIcon(filename: string): string
  static getFileTypeColor(fileType: string): string
}
```

### 6.2 浏览器特定服务

```typescript
// 文件位置: src/lib/services/browserStorage.ts (新建)
export class BrowserStorageService {
  // 高级存储管理
  static setWithExpiry<T>(key: string, value: T, expiryMs: number): void
  static getWithExpiry<T>(key: string): T | null
  static compress(data: any): string
  static decompress(compressedData: string): any

  // 存储配额管理
  static getStorageQuota(): Promise<{ quota: number; usage: number }>
  static isStorageAvailable(): boolean
  static clearExpiredItems(): void

  // 跨标签页通信
  static broadcastChange(key: string, value: any): void
  static onStorageChange(
    key: string,
    callback: (value: any) => void
  ): () => void
}

// 文件位置: src/lib/services/notificationService.ts (新建)
export class NotificationService {
  // 浏览器通知
  static async requestPermission(): Promise<NotificationPermission>
  static showBrowserNotification(
    title: string,
    options?: NotificationOptions
  ): void

  // Toast 通知管理
  static showToast(
    message: string,
    type: ToastType,
    options?: ToastOptions
  ): string
  static updateToast(id: string, updates: Partial<Toast>): void
  static removeToast(id: string): void
  static clearAllToasts(): void

  // 应用内通知
  static showInAppNotification(notification: InAppNotification): void
  static markNotificationAsRead(notificationId: string): void
  static getUnreadCount(): number
}

// 文件位置: src/lib/services/dragDropService.ts (新建)
export class DragDropService {
  // 拖拽处理
  static handleFileDrop(
    event: DragEvent,
    options: {
      allowedTypes?: string[]
      maxFileSize?: number
      multiple?: boolean
    }
  ): Promise<File[]>

  static validateDroppedFiles(
    files: FileList,
    options: FileDropOptions
  ): FileValidationResult

  // 拖拽状态管理
  static trackDragState(element: HTMLElement): {
    isDragging: boolean
    dragEnterCount: number
  }

  // 视觉反馈
  static addDropZoneStyles(element: HTMLElement): void
  static removeDropZoneStyles(element: HTMLElement): void
}
```

## 7. 性能优化 (Frontend Performance)

### 7.1 组件优化

```typescript
// 文件位置: src/lib/optimization/componentOptimization.ts (新建)
export const optimizeComponent = <P extends object>(
  Component: React.ComponentType<P>,
  options: {
    shouldMemoize?: boolean
    shouldVirtualize?: boolean
    preloadData?: boolean
  } = {}
) => {
  let OptimizedComponent = Component

  if (options.shouldMemoize) {
    OptimizedComponent = React.memo(OptimizedComponent)
  }

  if (options.shouldVirtualize) {
    OptimizedComponent = withVirtualization(OptimizedComponent)
  }

  if (options.preloadData) {
    OptimizedComponent = withDataPreloading(OptimizedComponent)
  }

  return OptimizedComponent
}

// 文件位置: src/lib/optimization/renderOptimization.ts (新建)
export class RenderOptimization {
  // 批量更新
  static batchUpdates(updates: (() => void)[]): void

  // 渲染节流
  static throttleRender(renderFn: () => void, delay: number): () => void

  // 条件渲染优化
  static optimizeConditionalRender<T>(
    condition: boolean,
    component: React.ComponentType<T>,
    fallback?: React.ComponentType
  ): React.ComponentType<T>

  // 列表渲染优化
  static optimizeListRender<T>(
    items: T[],
    renderItem: (item: T, index: number) => React.ReactNode,
    keyExtractor: (item: T) => string
  ): React.ReactNode[]
}
```

### 7.2 内存管理

```typescript
// 文件位置: src/lib/optimization/memoryManagement.ts (新建)
export class MemoryManager {
  // 组件清理
  static cleanupComponent(componentId: string): void
  static registerComponent(componentId: string, cleanupFn: () => void): void

  // 缓存管理
  static limitCacheSize<T>(cache: Map<string, T>, maxSize: number): void
  static clearUnusedCache(usageTracker: Map<string, Date>, ttl: number): void

  // 内存监控
  static getMemoryUsage(): { used: number; total: number }
  static trackMemoryLeaks(): void
  static reportMemoryStats(): MemoryStats

  // 垃圾回收优化
  static scheduleCleanup(cleanupFn: () => void, delay: number): void
  static forceGarbageCollection(): void
}
```

## 8. 类型定义 (Frontend Types)

### 8.1 UI 状态类型

```typescript
// 文件位置: src/types/ui.ts (扩展现有文件)

// 聊天 UI 状态
export interface ChatUIState {
  selectedConversationId: string | null
  isInputFocused: boolean
  inputHeight: number
  showEmojiPicker: boolean
  showAttachmentMenu: boolean
  typingUsers: Record<string, string[]> // conversationId -> userIds
  unreadCounts: Record<string, number>
}

// 文件管理 UI 状态
export interface FileUIState {
  viewMode: 'grid' | 'list' | 'table'
  selectedFiles: string[]
  sortBy: 'name' | 'date' | 'size' | 'type'
  sortOrder: 'asc' | 'desc'
  showPreview: boolean
  previewFileId: string | null
  uploadProgress: Record<string, number>
}

// 搜索 UI 状态
export interface SearchUIState {
  query: string
  filters: SearchFilters
  results: SearchResult[]
  isSearching: boolean
  recentSearches: string[]
  selectedResultIndex: number
}

// 通知 UI 状态
export interface NotificationUIState {
  toasts: Toast[]
  inAppNotifications: InAppNotification[]
  unreadCount: number
  isNotificationPanelOpen: boolean
}
```

### 8.2 性能监控类型

```typescript
// 文件位置: src/types/performance.ts (新建)

export interface PerformanceMetrics {
  // 渲染性能
  renderTime: number
  componentCount: number
  rerenderCount: number

  // 网络性能
  apiResponseTime: Record<string, number>
  websocketLatency: number

  // 内存使用
  memoryUsage: number
  cacheSize: number

  // 用户交互
  inputLatency: number
  scrollPerformance: number
}

export interface ComponentPerformance {
  componentName: string
  mountTime: number
  renderTime: number
  updateCount: number
  memoryFootprint: number
}
```

## 实施优先级 (Updated Implementation Priority)

### 第一阶段 (高优先级 - 核心前端功能) - 2-3 周

1. **API 客户端和 React Query 集成**

   - 完善 ApiClient 类
   - 实现 React Query hooks (auth, chat, files)
   - 集成错误处理和缓存策略

2. **WebSocket 实时通信**

   - 实现 WebSocket 客户端
   - 集成实时消息同步
   - 添加连接状态管理

3. **UI 状态管理增强**
   - 扩展现有 UI slice
   - 添加会话状态管理
   - 实现缓存状态管理

### 第二阶段 (中优先级 - 用户体验增强) - 2-3 周

1. **核心业务 Hooks**

   - 实现 useMessageInput hook
   - 添加虚拟滚动和无限滚动
   - 实现拖拽上传功能

2. **性能优化**

   - 组件优化和懒加载
   - 内存管理和缓存优化
   - 图片优化和预加载

3. **离线支持**
   - 实现离线状态检测
   - 添加离线队列管理
   - 实现数据同步机制

### 第三阶段 (低优先级 - 高级功能) - 1-2 周

1. **高级 UI 功能**

   - 键盘快捷键系统
   - 高级搜索和过滤
   - 自定义主题和布局

2. **开发体验优化**
   - 性能监控和分析
   - 错误边界和报告
   - 开发工具集成

## 估时评估 (Updated Time Estimation)

- **第一阶段**: 2-3 周 (前端核心功能)
- **第二阶段**: 2-3 周 (用户体验增强)
- **第三阶段**: 1-2 周 (高级功能和优化)

**总计**: 5-8 周的前端开发时间

## 结论 (Updated Conclusion)

基于后端 FastAPI + Supabase 架构分析，后端已经提供了完整的 API 服务、数据库管理、认证系统、实时通信等核心功能。**前端需要专注于以下核心领域**：

1. **数据获取和缓存**: React Query 集成和智能缓存策略
2. **实时通信**: WebSocket 客户端和状态同步
3. **UI 状态管理**: 复杂的前端状态和用户交互
4. **性能优化**: 虚拟化、懒加载、内存管理
5. **用户体验**: 拖拽上传、离线支持、快捷键等

这种分工确保了前端专注于用户界面和交互体验，而将复杂的业务逻辑、数据处理、AI 集成等留给后端处理，形成了清晰的职责分离。

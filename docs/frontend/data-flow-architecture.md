# Data Flow Architecture - API Integration Pattern

## 🏛️ 架构层次

```
┌─────────────────────┐
│   React Components  │ ← 使用 business hooks
├─────────────────────┤
│  Business Hooks     │ ← API调用 + 业务逻辑
│  (/src/hooks/)      │   (useConversations, useAuth, etc.)
├─────────────────────┤
│   Store Hooks       │ ← 性能优化的状态选择器
│  (/store/hooks/)    │   (useOptimizedSelectors)
├─────────────────────┤
│   Store Slices      │ ← 纯状态管理，无API调用
│  (/store/slices/)   │   (conversationSlice, authSlice)
├─────────────────────┤
│   API Services      │ ← HTTP请求和数据转换
│  (/services/api/)   │   (conversationService, authService)
├─────────────────────┤
│   API Client        │ ← 通用HTTP客户端
│  (/lib/api/)        │   (fetch配置、拦截器)
└─────────────────────┘
```

## 🔄 数据流向

### **创建对话示例**

1. **Component** 调用业务hook
```typescript
const { createConversation } = useConversations()
await createConversation({ title: "新对话" })
```

2. **Business Hook** 处理完整流程
```typescript
// src/hooks/useConversations.ts
const createConversation = async (payload) => {
  // 1. 更新loading状态
  store.setLoading(true)
  
  // 2. 调用API service
  const response = await conversationService.create(payload)
  
  // 3. 更新store状态
  store.addConversation(response.data)
  
  // 4. 显示用户反馈
  toasts.success('创建成功')
}
```

3. **API Service** 处理HTTP请求
```typescript
// src/services/api/conversationService.ts
async create(payload: CreateConversationPayload) {
  return await apiClient.post('/api/conversations', payload)
}
```

4. **Store Slice** 更新状态
```typescript
// store/slices/chat/conversationSlice.ts
addConversation: (conversation) => 
  set(state => ({
    conversations: {
      data: [...state.conversations.data, conversation],
      timestamp: Date.now()
    }
  }))
```

## 📋 职责分工

### **/src/hooks/** - Business Logic
- ✅ API调用和错误处理
- ✅ 复杂业务逻辑
- ✅ 多个store slice协调
- ✅ 用户反馈 (toasts/notifications)
- ✅ 数据验证和转换

### **/store/hooks/** - Performance
- ✅ 优化的状态选择器
- ✅ Memoization和shallow comparison
- ✅ 避免不必要的re-render
- ✅ 批量状态获取

### **/store/slices/** - State Management
- ✅ 纯状态操作
- ✅ 数据结构管理
- ✅ 缓存策略
- ❌ 不包含API调用
- ❌ 不包含复杂业务逻辑

### **/services/api/** - Data Layer
- ✅ HTTP请求封装
- ✅ 请求/响应数据转换
- ✅ API错误处理
- ✅ 重试逻辑

## 🛠️ 实现指南

### 1. 创建API Service
```typescript
// src/services/api/conversationService.ts
export class ConversationService {
  private readonly baseURL = '/api/conversations'
  
  async create(payload: CreateConversationPayload): Promise<ApiResponse<Conversation>> {
    const response = await apiClient.post(this.baseURL, {
      title: payload.title,
      participants: payload.participants,
      type: payload.type || 'direct',
    })
    
    return {
      data: this.transformConversation(response.data),
      success: true,
      message: 'Conversation created successfully'
    }
  }
  
  private transformConversation(raw: any): Conversation {
    return {
      id: raw.id,
      title: raw.title,
      participants: raw.participants.map(this.transformParticipant),
      createdAt: new Date(raw.created_at).toISOString(),
      updatedAt: new Date(raw.updated_at).toISOString(),
      // ... 其他字段转换
    }
  }
}
```

### 2. 增强Business Hook
```typescript
// src/hooks/useConversations.ts
export const useConversations = () => {
  const store = useConversationsStore()
  const toasts = useToasts()
  const { user } = useAuth()
  
  const createConversation = useCallback(async (payload: CreateConversationPayload) => {
    if (!user) {
      toasts.error('请先登录')
      return
    }
    
    try {
      store.setLoading(true)
      
      // 乐观更新 - 立即显示在UI中
      const optimisticConversation = {
        id: `temp-${Date.now()}`,
        ...payload,
        participants: [user, ...payload.participants],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        isOptimistic: true, // 标记为临时状态
      }
      
      store.addConversation(optimisticConversation)
      
      // 真实API调用
      const response = await conversationService.create(payload)
      
      // 用真实数据替换乐观更新
      store.replaceConversation(optimisticConversation.id, response.data)
      
      toasts.success('对话已创建')
      return response.data
      
    } catch (error) {
      // 回滚乐观更新
      store.removeConversation(optimisticConversation.id)
      toasts.error('创建失败', error.message)
      throw error
    } finally {
      store.setLoading(false)
    }
  }, [user, store, toasts])
  
  return {
    // 状态
    conversations: store.conversations.data,
    isLoading: store.isLoading,
    error: store.error,
    
    // 操作
    createConversation,
    loadConversations: store.loadConversations,
    setActiveConversation: store.setActiveConversation,
  }
}
```

### 3. 组件中的使用
```typescript
// components/chat/CreateConversationDialog.tsx
export function CreateConversationDialog() {
  const { createConversation, isLoading } = useConversations()
  
  const handleSubmit = async (data: CreateConversationForm) => {
    try {
      const conversation = await createConversation({
        title: data.title,
        participants: data.selectedContacts,
        type: data.type,
      })
      
      // 自动跳转到新对话
      router.push(`/chat/${conversation.id}`)
      
    } catch (error) {
      // 错误已经被hook处理，这里可以做额外处理
      console.error('Failed to create conversation:', error)
    }
  }
  
  return (
    <Dialog>
      <form onSubmit={handleSubmit}>
        {/* ... 表单字段 */}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? '创建中...' : '创建对话'}
        </Button>
      </form>
    </Dialog>
  )
}
```

## 🔧 迁移策略

### 现有hooks重构
1. **保留现有的hooks接口** - 避免破坏性变更
2. **逐步迁移内部实现** - 使用新的store和API service
3. **增强错误处理** - 统一的错误处理和用户反馈
4. **添加性能优化** - 缓存、去抖动、乐观更新

### API集成准备
1. **创建统一的API client** - 处理认证、错误、重试
2. **定义数据转换层** - 前后端数据格式转换
3. **实现缓存策略** - API响应缓存和失效策略
4. **添加离线支持** - 网络失败时的fallback机制
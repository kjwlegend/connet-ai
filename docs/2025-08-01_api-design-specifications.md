# API Design Specifications - Connet.AI

## API 设计原则

### 1. RESTful 设计规范
- **资源导向**: 使用名词表示资源，HTTP 动词表示操作
- **统一接口**: 标准化的 HTTP 状态码和响应格式
- **无状态**: 每个请求包含完整的处理信息
- **分层系统**: 支持缓存、负载均衡、网关等中间层

### 2. API 版本控制
- **URL 版本控制**: `/api/v1/`, `/api/v2/`
- **向后兼容**: 新版本保持向后兼容性
- **弃用策略**: 明确的 API 弃用通知和迁移时间线
- **文档同步**: 版本更新与文档同步维护

### 3. 数据一致性
- **幂等性**: GET、PUT、DELETE 操作幂等
- **原子操作**: 复杂操作确保原子性
- **乐观锁**: 使用版本号或时间戳防止并发冲突
- **事务支持**: 关键业务操作事务保护

## API 架构概览

```
API Architecture (FastAPI + Supabase)
│
├── 🌐 API Gateway Layer
│   ├── Rate Limiting (频率限制)
│   ├── Authentication (认证验证)  
│   ├── Request Validation (请求验证)
│   └── Response Transformation (响应转换)
│
├── 🔐 Authentication & Authorization
│   ├── JWT Token Management (令牌管理)
│   ├── Role-Based Access Control (基于角色的访问控制)
│   ├── OAuth Integration (第三方登录)
│   └── Session Management (会话管理)
│
├── 📡 REST API Endpoints
│   ├── User Management (/api/v1/users)
│   ├── Chat & Conversations (/api/v1/chat)
│   ├── AI Agents (/api/v1/agents)
│   ├── File Management (/api/v1/files)
│   ├── Timeline & Posts (/api/v1/timeline)
│   └── Settings & Preferences (/api/v1/settings)
│
├── 🔄 Real-time Communication
│   ├── WebSocket Connections (WebSocket 连接)
│   ├── Server-Sent Events (服务器推送事件)
│   ├── Supabase Realtime (Supabase 实时订阅)
│   └── Message Broadcasting (消息广播)
│
├── 🤖 AI Integration Layer
│   ├── LangChain Integration (LangChain 集成)
│   ├── Model Management (模型管理)
│   ├── Prompt Engineering (提示工程)
│   └── Response Processing (响应处理)
│
└── 💾 Data Access Layer
    ├── Supabase Client (Supabase 客户端)
    ├── Database Operations (数据库操作)
    ├── File Storage (文件存储)
    └── Vector Search (向量搜索)
```

## 认证与授权 API

### 1. 用户认证端点

#### 1.1 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "username": "username", 
  "displayName": "Display Name",
  "preferredLanguage": "zh-CN"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123abc",
      "email": "user@example.com", 
      "username": "username",
      "displayName": "Display Name",
      "avatar": null,
      "preferredLanguage": "zh-CN",
      "createdAt": "2025-01-08T10:00:00Z",
      "emailVerified": false
    },
    "tokens": {
      "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...", 
      "expiresIn": 3600,
      "tokenType": "Bearer"
    }
  },
  "message": "User registered successfully"
}
```

#### 1.2 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "rememberMe": true
}
```

#### 1.3 令牌刷新
```http
POST /api/v1/auth/refresh
Content-Type: application/json
Authorization: Bearer {refreshToken}

{
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 1.4 用户登出
```http
POST /api/v1/auth/logout
Authorization: Bearer {accessToken}

{
  "allDevices": false  // 是否登出所有设备
}
```

### 2. OAuth 集成端点

#### 2.1 Google OAuth
```http
GET /api/v1/auth/oauth/google
```

#### 2.2 GitHub OAuth
```http
GET /api/v1/auth/oauth/github
```

#### 2.3 OAuth 回调处理
```http
POST /api/v1/auth/oauth/callback
Content-Type: application/json

{
  "provider": "google",
  "code": "authorization_code",
  "state": "csrf_state_token"
}
```

## 用户管理 API

### 1. 用户信息管理

#### 1.1 获取当前用户信息
```http
GET /api/v1/users/me
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123abc",
      "email": "user@example.com",
      "username": "username", 
      "displayName": "Display Name",
      "avatar": "https://cdn.connet.ai/avatars/user_123abc.jpg",
      "bio": "AI enthusiast and developer",
      "preferredLanguage": "zh-CN",
      "timezone": "Asia/Shanghai",
      "theme": "dark",
      "emailVerified": true,
      "createdAt": "2025-01-08T10:00:00Z",
      "updatedAt": "2025-01-08T12:00:00Z",
      "lastActiveAt": "2025-01-08T12:30:00Z"
    },
    "preferences": {
      "notifications": {
        "email": true,
        "push": true,
        "inApp": true
      },
      "privacy": {
        "profileVisibility": "public",
        "allowDirectMessages": true
      }
    },
    "subscription": {
      "plan": "pro",
      "expiresAt": "2025-02-08T10:00:00Z",
      "features": ["unlimited_chats", "premium_agents", "file_uploads"]
    }
  }
}
```

#### 1.2 更新用户信息
```http
PUT /api/v1/users/me
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "displayName": "New Display Name",
  "bio": "Updated bio",
  "preferredLanguage": "en",
  "timezone": "UTC"
}
```

#### 1.3 上传用户头像
```http
POST /api/v1/users/me/avatar
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data

file: [二进制文件数据]
```

#### 1.4 更新用户偏好设置
```http
PUT /api/v1/users/me/preferences
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "theme": "dark",
  "notifications": {
    "email": false,
    "push": true,
    "inApp": true
  },
  "privacy": {
    "profileVisibility": "private"
  }
}
```

### 2. 用户搜索与发现

#### 2.1 搜索用户
```http
GET /api/v1/users/search?q=keyword&limit=20&offset=0
Authorization: Bearer {accessToken}
```

#### 2.2 获取用户详情（公开信息）
```http
GET /api/v1/users/{userId}
Authorization: Bearer {accessToken}
```

## 对话管理 API

### 1. 对话 CRUD 操作

#### 1.1 获取对话列表
```http
GET /api/v1/chat/conversations?limit=50&offset=0&filter=active
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "conversations": [
      {
        "id": "conv_123abc",
        "title": "AI编程助手对话",
        "type": "agent_chat",
        "participants": [
          {
            "id": "user_123abc",
            "type": "user",
            "displayName": "用户名",
            "avatar": "https://cdn.connet.ai/avatars/user_123abc.jpg"
          },
          {
            "id": "agent_456def", 
            "type": "agent",
            "displayName": "编程助手",
            "avatar": "https://cdn.connet.ai/agents/programming.jpg",
            "model": "gpt-4",
            "capabilities": ["code_generation", "debugging", "explanation"]
          }
        ],
        "lastMessage": {
          "id": "msg_789ghi",
          "content": "这段代码的时间复杂度是 O(n log n)",
          "senderId": "agent_456def",
          "timestamp": "2025-01-08T12:30:00Z",
          "type": "text"
        },
        "unreadCount": 2,
        "isPinned": false,
        "isMuted": false,
        "createdAt": "2025-01-08T10:00:00Z",
        "updatedAt": "2025-01-08T12:30:00Z"
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 50,
      "offset": 0,
      "hasMore": false
    }
  }
}
```

#### 1.2 创建新对话
```http
POST /api/v1/chat/conversations
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "title": "新的AI对话",
  "type": "agent_chat",
  "agentId": "agent_456def",
  "initialMessage": "你好，我需要帮助编写一个Python函数"
}
```

#### 1.3 获取对话详情
```http
GET /api/v1/chat/conversations/{conversationId}
Authorization: Bearer {accessToken}
```

#### 1.4 更新对话信息
```http
PUT /api/v1/chat/conversations/{conversationId}
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "title": "更新的对话标题",
  "isPinned": true,
  "isMuted": false
}
```

#### 1.5 删除对话
```http
DELETE /api/v1/chat/conversations/{conversationId} 
Authorization: Bearer {accessToken}
```

### 2. 消息管理

#### 2.1 获取对话消息
```http
GET /api/v1/chat/conversations/{conversationId}/messages?limit=50&before=msg_123&after=msg_456
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true, 
  "data": {
    "messages": [
      {
        "id": "msg_123abc",
        "conversationId": "conv_123abc",
        "senderId": "user_123abc", 
        "senderType": "user",
        "content": "请帮我写一个快速排序算法",
        "type": "text",
        "metadata": {},
        "reactions": [
          {
            "emoji": "👍",
            "count": 2,
            "users": ["user_456def", "agent_789ghi"]
          }
        ],
        "replyTo": null,
        "editedAt": null,
        "timestamp": "2025-01-08T12:25:00Z"
      },
      {
        "id": "msg_456def",
        "conversationId": "conv_123abc", 
        "senderId": "agent_456def",
        "senderType": "agent",
        "content": "当然！这里是一个Python快速排序的实现：\n\n```python\ndef quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot] \n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + middle + quicksort(right)\n```",
        "type": "text",
        "metadata": {
          "codeBlocks": [
            {
              "language": "python",
              "startLine": 3,
              "endLine": 10
            }
          ],
          "processingTime": 1.2,
          "model": "gpt-4",
          "tokenUsage": {
            "prompt": 45,
            "completion": 128,
            "total": 173
          }
        },
        "reactions": [],
        "replyTo": "msg_123abc",
        "editedAt": null,
        "timestamp": "2025-01-08T12:25:30Z"
      }
    ],
    "pagination": {
      "hasMore": true,
      "nextCursor": "msg_789ghi",
      "prevCursor": "msg_123abc"
    }
  }
}
```

#### 2.2 发送消息
```http
POST /api/v1/chat/conversations/{conversationId}/messages
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "content": "谢谢！请解释一下这个算法的时间复杂度",
  "type": "text",
  "replyTo": "msg_456def",
  "metadata": {
    "attachments": []
  }
}
```

#### 2.3 编辑消息
```http
PUT /api/v1/chat/conversations/{conversationId}/messages/{messageId}
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "content": "更新后的消息内容"
}
```

#### 2.4 删除消息
```http
DELETE /api/v1/chat/conversations/{conversationId}/messages/{messageId}
Authorization: Bearer {accessToken}
```

#### 2.5 添加消息反应
```http
POST /api/v1/chat/conversations/{conversationId}/messages/{messageId}/reactions
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "emoji": "👍"
}
```

## AI 代理管理 API

### 1. 代理发现与管理

#### 1.1 获取代理列表
```http
GET /api/v1/agents?category=programming&limit=20&offset=0&search=python
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "agent_123abc",
        "name": "Python编程助手",
        "displayName": "Python Expert",
        "description": "专业的Python编程助手，擅长代码编写、调试和优化",
        "avatar": "https://cdn.connet.ai/agents/python-expert.jpg",
        "category": "programming",
        "tags": ["python", "coding", "debugging", "optimization"],
        "capabilities": [
          "code_generation",
          "code_review", 
          "debugging",
          "performance_optimization",
          "testing"
        ],
        "model": {
          "provider": "openai",
          "model": "gpt-4",
          "version": "2023-12-01"
        },
        "pricing": {
          "type": "token_based",
          "inputTokenPrice": 0.01,
          "outputTokenPrice": 0.03,
          "currency": "USD"
        },
        "rating": {
          "average": 4.8,
          "count": 1250
        },
        "usage": {
          "conversationCount": 15420,
          "userCount": 3250
        },
        "isOfficial": true,
        "isVerified": true,
        "isActive": true,
        "createdBy": "connet_ai",
        "createdAt": "2024-11-15T10:00:00Z",
        "updatedAt": "2025-01-08T09:00:00Z"
      }
    ],
    "categories": [
      {
        "id": "programming",
        "name": "编程开发",
        "description": "编程、代码审查、调试等",
        "count": 45
      },
      {
        "id": "writing", 
        "name": "写作助手",
        "description": "文案创作、内容编辑等",
        "count": 32
      }
    ],
    "pagination": {
      "total": 150,
      "limit": 20,
      "offset": 0,
      "hasMore": true
    }
  }
}
```

#### 1.2 获取代理详情
```http
GET /api/v1/agents/{agentId}
Authorization: Bearer {accessToken}
```

#### 1.3 获取代理使用统计
```http
GET /api/v1/agents/{agentId}/stats
Authorization: Bearer {accessToken}
```

#### 1.4 评价代理
```http
POST /api/v1/agents/{agentId}/ratings
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "rating": 5,
  "comment": "非常好用的Python助手，回答准确且详细",
  "aspects": {
    "accuracy": 5,
    "helpfulness": 5,
    "speed": 4,
    "friendliness": 5
  }
}
```

### 2. 自定义代理管理

#### 2.1 创建自定义代理
```http
POST /api/v1/agents/custom
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "name": "我的专属助手",
  "description": "基于我的需求定制的AI助手",
  "avatar": "avatar_url",
  "category": "personal",
  "systemPrompt": "你是一个专业的...",
  "model": {
    "provider": "openai",
    "model": "gpt-4"
  },
  "settings": {
    "temperature": 0.7,
    "maxTokens": 2000,
    "topP": 0.9
  },
  "capabilities": ["general_chat", "task_planning"],
  "isPublic": false
}
```

#### 2.2 更新自定义代理
```http
PUT /api/v1/agents/custom/{agentId}
Authorization: Bearer {accessToken}
Content-Type: application/json
```

#### 2.3 删除自定义代理
```http
DELETE /api/v1/agents/custom/{agentId}
Authorization: Bearer {accessToken}
```

## 文件管理 API

### 1. 文件上传与管理

#### 1.1 上传文件
```http
POST /api/v1/files/upload
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data

file: [二进制文件数据]
metadata: {
  "tags": ["document", "important"],
  "description": "项目需求文档",
  "isPublic": false
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "file": {
      "id": "file_123abc",
      "filename": "requirements.pdf",
      "originalName": "项目需求文档.pdf",
      "mimeType": "application/pdf", 
      "size": 2048576,
      "url": "https://storage.connet.ai/files/user_123abc/file_123abc.pdf",
      "thumbnailUrl": "https://storage.connet.ai/thumbnails/file_123abc.jpg",
      "checksum": "sha256:abc123...",
      "metadata": {
        "tags": ["document", "important"],
        "description": "项目需求文档",
        "isPublic": false,
        "extractedText": "...", // 如果是文档类型
        "pageCount": 25, // PDF 特定信息
        "language": "zh-CN"
      },
      "processingStatus": "completed",
      "uploadedBy": "user_123abc",
      "createdAt": "2025-01-08T12:00:00Z",
      "updatedAt": "2025-01-08T12:00:30Z"
    }
  }
}
```

#### 1.2 获取文件列表
```http
GET /api/v1/files?limit=20&offset=0&type=document&tags=important
Authorization: Bearer {accessToken}
```

#### 1.3 获取文件详情
```http
GET /api/v1/files/{fileId}
Authorization: Bearer {accessToken}
```

#### 1.4 更新文件信息
```http
PUT /api/v1/files/{fileId}
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "tags": ["document", "updated"],
  "description": "更新后的描述",
  "isPublic": true
}
```

#### 1.5 删除文件
```http
DELETE /api/v1/files/{fileId}
Authorization: Bearer {accessToken}
```

### 2. 文件搜索与检索

#### 2.1 搜索文件
```http
GET /api/v1/files/search?q=关键词&type=document&limit=10
Authorization: Bearer {accessToken}
```

#### 2.2 向量搜索（语义搜索）
```http
POST /api/v1/files/vector-search
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "query": "关于用户界面设计的内容",
  "limit": 10,
  "threshold": 0.8,
  "fileTypes": ["pdf", "docx", "txt"]
}
```

## 时间线与动态 API

### 1. 时间线内容管理

#### 1.1 获取时间线内容
```http
GET /api/v1/timeline?limit=20&offset=0&filter=following
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "post_123abc",
        "type": "conversation_share",
        "author": {
          "id": "user_456def",
          "displayName": "开发者张三",
          "username": "dev_zhang",
          "avatar": "https://cdn.connet.ai/avatars/user_456def.jpg"
        },
        "content": {
          "title": "AI助手帮我解决了一个复杂的算法问题",
          "description": "分享一次很棒的AI对话体验",
          "conversationId": "conv_789ghi",
          "highlights": [
            {
              "messageId": "msg_abc123",
              "content": "这里是关键的解决方案...",
              "timestamp": "2025-01-08T10:30:00Z"
            }
          ]
        },
        "attachments": [
          {
            "type": "code",
            "language": "python",
            "content": "def solution():\n    return 'amazing'"
          }
        ],
        "interactions": {
          "likes": 15,
          "comments": 3,
          "shares": 2,
          "bookmarks": 8
        },
        "isLikedByUser": false,
        "isBookmarkedByUser": false,
        "visibility": "public",
        "createdAt": "2025-01-08T11:00:00Z",
        "updatedAt": "2025-01-08T11:30:00Z"
      }
    ],
    "pagination": {
      "hasMore": true,
      "nextCursor": "post_456def"
    }
  }
}
```

#### 1.2 发布动态
```http
POST /api/v1/timeline/posts
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "type": "text_post",
  "content": {
    "title": "今天学到了新技术",
    "description": "分享一些关于React性能优化的心得",
    "text": "详细的内容..."
  },
  "attachments": [
    {
      "type": "file",
      "fileId": "file_123abc"
    }
  ],
  "visibility": "public",
  "tags": ["react", "performance", "learning"]
}
```

#### 1.3 互动操作
```http
POST /api/v1/timeline/posts/{postId}/like
Authorization: Bearer {accessToken}
```

```http
POST /api/v1/timeline/posts/{postId}/comments
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "content": "很有用的分享，谢谢！",
  "replyTo": "comment_456def" // 可选，回复特定评论
}
```

## 设置与偏好 API

### 1. 用户设置管理

#### 1.1 获取用户设置
```http
GET /api/v1/settings
Authorization: Bearer {accessToken}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "general": {
      "language": "zh-CN",
      "timezone": "Asia/Shanghai", 
      "theme": "dark",
      "fontSize": "medium"
    },
    "notifications": {
      "email": {
        "enabled": true,
        "newMessages": true,
        "mentions": true,
        "systemUpdates": false
      },
      "push": {
        "enabled": true,
        "newMessages": true,
        "mentions": true
      },
      "inApp": {
        "enabled": true,
        "sound": true,
        "desktop": true
      }
    },
    "privacy": {
      "profileVisibility": "public",
      "allowDirectMessages": true,
      "showOnlineStatus": true,
      "dataCollection": true
    },
    "ai": {
      "defaultModel": "gpt-4",
      "responseStyle": "balanced",
      "codeHighlighting": true,
      "autoSave": true
    },
    "interface": {
      "sidebarWidth": 280,
      "middlePanelWidth": 350,
      "showAvatars": true,
      "compactMode": false
    }
  }
}
```

#### 1.2 更新设置
```http
PUT /api/v1/settings
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "general": {
    "theme": "light",
    "language": "en"
  },
  "notifications": {
    "email": {
      "newMessages": false
    }
  }
}
```

### 2. 订阅与计费管理

#### 2.1 获取订阅信息
```http
GET /api/v1/settings/subscription
Authorization: Bearer {accessToken}  
```

#### 2.2 更新订阅计划
```http
POST /api/v1/settings/subscription/upgrade
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "plan": "pro",
  "billingCycle": "monthly",
  "paymentMethod": "stripe_pm_123abc"
}
```

## WebSocket 实时通信

### 1. WebSocket 连接管理

#### 1.1 建立连接
```javascript
// WebSocket 连接端点
const wsUrl = 'wss://api.connet.ai/ws/v1'

// 连接参数
const connectionParams = {
  token: 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
  version: 'v1',
  clientId: 'web_client_123abc'
}

// 建立连接
const ws = new WebSocket(`${wsUrl}?token=${encodeURIComponent(connectionParams.token)}`)
```

### 2. 实时事件类型

#### 2.1 消息事件
```json
{
  "type": "message.new",
  "data": {
    "conversationId": "conv_123abc",
    "message": {
      "id": "msg_456def",
      "content": "新消息内容",
      "senderId": "agent_789ghi",
      "timestamp": "2025-01-08T12:30:00Z"
    }
  },
  "timestamp": "2025-01-08T12:30:00Z"
}
```

#### 2.2 输入状态事件
```json
{
  "type": "typing.start",
  "data": {
    "conversationId": "conv_123abc", 
    "userId": "user_456def",
    "timestamp": "2025-01-08T12:29:45Z"
  }
}
```

#### 2.3 在线状态事件
```json
{
  "type": "presence.update",
  "data": {
    "userId": "user_123abc",
    "status": "online",
    "lastSeen": "2025-01-08T12:30:00Z"
  }
}
```

### 3. 客户端事件发送

#### 3.1 发送输入状态
```json
{
  "type": "typing.start",
  "data": {
    "conversationId": "conv_123abc"
  }
}
```

#### 3.2 订阅对话
```json
{
  "type": "subscribe",
  "data": {
    "channel": "conversation",
    "conversationId": "conv_123abc"
  }
}
```

## 错误处理规范

### 1. HTTP 状态码使用

```typescript
interface HTTPStatusCodes {
  // 成功响应
  200: "OK - 请求成功"
  201: "Created - 资源创建成功"
  202: "Accepted - 请求已接受，处理中"
  204: "No Content - 成功但无返回内容"
  
  // 客户端错误
  400: "Bad Request - 请求参数错误"
  401: "Unauthorized - 未认证"
  403: "Forbidden - 无权限"
  404: "Not Found - 资源不存在" 
  409: "Conflict - 资源冲突"
  422: "Unprocessable Entity - 请求格式正确但语义错误"
  429: "Too Many Requests - 请求频率超限"
  
  // 服务器错误
  500: "Internal Server Error - 内部服务器错误"
  502: "Bad Gateway - 网关错误"
  503: "Service Unavailable - 服务不可用"
  504: "Gateway Timeout - 网关超时"
}
```

### 2. 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": {
      "field": "email",
      "message": "邮箱格式不正确",
      "value": "invalid-email"
    },
    "timestamp": "2025-01-08T12:30:00Z",
    "requestId": "req_123abc456def",
    "documentation": "https://docs.connet.ai/api/errors#validation-error"
  }
}
```

### 3. 常见错误代码

```typescript
interface ErrorCodes {
  // 认证错误
  UNAUTHORIZED: "未提供有效的认证令牌"
  TOKEN_EXPIRED: "访问令牌已过期"
  INVALID_TOKEN: "无效的访问令牌"
  INSUFFICIENT_PERMISSIONS: "权限不足"
  
  // 验证错误
  VALIDATION_ERROR: "请求参数验证失败"
  MISSING_REQUIRED_FIELD: "缺少必需字段"
  INVALID_FORMAT: "字段格式不正确"
  VALUE_OUT_OF_RANGE: "字段值超出允许范围"
  
  // 资源错误
  RESOURCE_NOT_FOUND: "请求的资源不存在"
  RESOURCE_ALREADY_EXISTS: "资源已存在"
  RESOURCE_CONFLICT: "资源状态冲突"
  
  // 业务逻辑错误
  CONVERSATION_LIMIT_EXCEEDED: "对话数量超出限制"
  INSUFFICIENT_QUOTA: "配额不足"
  FEATURE_NOT_AVAILABLE: "功能不可用"
  
  // 系统错误
  INTERNAL_SERVER_ERROR: "内部服务器错误"
  DATABASE_ERROR: "数据库操作失败"
  EXTERNAL_SERVICE_ERROR: "外部服务调用失败"
  RATE_LIMIT_EXCEEDED: "请求频率超出限制"
}
```

## API 版本控制与废弃

### 1. 版本控制策略

```typescript
interface VersioningStrategy {
  // URL 版本控制
  urlVersioning: {
    current: "/api/v1/"
    upcoming: "/api/v2/"
    deprecated: "/api/v0/" // 将在 2025-06-01 移除
  }
  
  // 版本生命周期
  lifecycle: {
    development: "开发阶段，频繁变更"
    stable: "稳定版本，向后兼容"
    deprecated: "已废弃，建议迁移"
    sunset: "即将下线，停止服务"
  }
  
  // 废弃通知
  deprecationNotice: {
    headers: {
      "X-API-Deprecation-Warning": "此版本将在 2025-06-01 废弃"
      "X-API-Sunset-Date": "2025-06-01"
      "X-API-Migration-Guide": "https://docs.connet.ai/migration/v1-to-v2"
    }
  }
}
```

### 2. API 文档与测试

```typescript
interface APIDocumentation {
  // 文档工具
  documentation: {
    swagger: "OpenAPI 3.0 规范"
    postman: "Postman 集合"
    insomnia: "Insomnia 集合"
  }
  
  // 示例环境
  environments: {
    development: "https://api-dev.connet.ai"
    staging: "https://api-staging.connet.ai"
    production: "https://api.connet.ai"
  }
  
  // 测试工具
  testing: {
    unitTests: "FastAPI TestClient"
    integrationTests: "Pytest + 真实数据库"
    contractTests: "Pact 契约测试"
    loadTests: "Locust 性能测试"
  }
}
```

---

**API 设计版本**: v1.0  
**最后更新**: 2025-01-08  
**兼容性**: Next.js 15.3.2 + FastAPI + Supabase  

这个 API 设计规范为 Connet.AI 提供了：
1. **标准化**: 统一的接口设计和错误处理
2. **可扩展性**: 清晰的版本控制和演进路径  
3. **实时性**: WebSocket 和 Server-Sent Events 支持
4. **安全性**: 完整的认证授权机制
5. **开发友好**: 详细的文档和示例

这将确保前端和后端的高效集成，为用户提供流畅的 AI 协作体验。
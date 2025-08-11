# Frontend Data Types Specification

## 📝 概览

这份文档详细定义了Connet.AI前端应用中所有的数据类型，为后端数据结构设计提供准确的参考。基于当前前端实现和功能需求，涵盖了人机协作、AI代理系统、实时通信等所有核心功能的数据模型。

---

## 🏗️ **核心实体类型**

### 👤 **用户和身份系统**

#### **User - 用户实体**
```typescript
interface User {
  // 基础身份信息
  id: string                          // 用户唯一标识
  username: string                    // 用户名
  email: string                       // 邮箱
  phone?: string                      // 手机号
  avatar?: string                     // 头像URL
  
  // 个人信息
  displayName: string                 // 显示名称
  firstName?: string                  // 名字
  lastName?: string                   // 姓氏
  bio?: string                       // 个人简介
  location?: string                   // 地理位置
  
  // 系统状态
  status: 'active' | 'inactive' | 'suspended' | 'pending'
  isOnline: boolean                   // 在线状态
  lastSeenAt?: string                // 最后活跃时间
  
  // 权限和角色
  roles: UserRole[]                   // 用户角色
  permissions: Permission[]           // 直接权限
  
  // 偏好设置
  preferences: UserPreferences        // 用户偏好
  
  // 元数据
  createdAt: string
  updatedAt: string
  emailVerified: boolean
  phoneVerified: boolean
  
  // 统计信息
  stats?: {
    conversationCount: number         // 参与对话数
    messageCount: number              // 发送消息数
    agentInteractions: number         // AI代理交互数
  }
}

interface UserRole {
  id: string
  name: 'admin' | 'user' | 'moderator' | 'agent_creator'
  description: string
  permissions: Permission[]
}

interface Permission {
  id: string
  name: string
  resource: string                    // 资源类型
  actions: string[]                   // 允许的操作
}

interface UserPreferences {
  // UI偏好
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'zh'
  colorScheme: 'default' | 'blue' | 'green' | 'purple'
  fontScale: number                   // 字体缩放
  compactMode: boolean                // 紧凑模式
  
  // 通知偏好
  notifications: {
    email: boolean
    push: boolean
    inApp: boolean
    sound: boolean
    
    // 详细通知设置
    newMessage: boolean
    mentions: boolean
    agentResponses: boolean
    systemUpdates: boolean
  }
  
  // 布局偏好
  layout: {
    sidebarCollapsed: boolean
    middlePanelWidth: number
    rightPanelWidth: number
  }
  
  // 功能偏好
  features: {
    autoSave: boolean
    enterToSend: boolean
    showTypingIndicators: boolean
    readReceipts: boolean
  }
}
```

### 🤖 **AI代理系统**

#### **AIAgent - AI代理实体**
```typescript
interface AIAgent {
  // 基础信息
  id: string                          // 代理唯一标识 (用于@提及)
  name: string                        // 基础名称
  displayName?: string                // 自定义显示名称
  avatar: string                      // 头像URL
  
  // 能力描述
  specialty: string                   // 专业领域
  description: string                 // 详细描述
  capabilities: AgentCapability[]     // 具体能力列表
  tags: string[]                      // 标签分类
  
  // 状态信息
  status: 'online' | 'offline' | 'busy' | 'maintenance'
  type: 'agent' | 'human'            // 区分AI代理和人类
  isVerified: boolean                 // 官方认证标识
  
  // 个性化
  personality?: {
    tone: 'professional' | 'casual' | 'friendly' | 'humorous'
    expertise_level: 'beginner' | 'intermediate' | 'expert'
    communication_style: 'concise' | 'detailed' | 'interactive'
  }
  
  // 系统信息
  createdAt: string
  updatedAt: string
  createdBy: string                   // 创建者ID
  
  // 性能统计
  stats?: {
    totalInteractions: number         // 总交互次数
    averageResponseTime: number       // 平均响应时间(ms)
    satisfactionScore: number         // 满意度评分(1-5)
    uptime: number                   // 可用时间百分比
  }
  
  // 配置信息
  configuration?: {
    model: string                     // 使用的AI模型
    temperature: number               // 创造性参数
    max_tokens: number               // 最大token数
    system_prompt?: string           // 系统提示词
    tools: string[]                  // 可用工具列表
  }
}

interface AgentCapability {
  id: string
  name: string                        // 能力名称
  description: string                 // 能力描述
  category: 'communication' | 'analysis' | 'creation' | 'automation' | 'integration'
  confidence: number                  // 能力置信度 (0-1)
  examples?: string[]                 // 使用示例
}

// 代理搜索结果
interface AddContactSearchResult extends AIAgent {
  searchScore: number                 // 搜索相关性得分
  isAlreadyContact: boolean          // 是否已添加为联系人
  matchedFields: string[]            // 匹配的字段
  recommendationReason?: string       // 推荐理由
}
```

### 👥 **联系人和关系系统**

#### **Contact - 联系人关系**
```typescript
interface ContactRelationship {
  id: string
  userId: string                      // 用户ID
  contactId: string                   // 联系人ID (可以是User或AIAgent)
  contactType: 'human' | 'agent'     // 联系人类型
  
  // 关系信息
  relationshipType: 'friend' | 'colleague' | 'family' | 'agent' | 'custom'
  customLabel?: string                // 自定义标签
  note?: string                       // 个人备注
  
  // 状态
  status: 'active' | 'blocked' | 'muted'
  isFavorite: boolean                // 收藏状态
  
  // 权限设置
  permissions: {
    canSeeOnlineStatus: boolean
    canInitiateConversation: boolean
    canAddToGroups: boolean
    canShareFiles: boolean
  }
  
  // 元数据
  createdAt: string
  updatedAt: string
  lastInteractionAt?: string         // 最后交互时间
  
  // 统计信息
  stats: {
    conversationCount: number         // 共同对话数
    messageCount: number             // 消息交换数
    lastMessageAt?: string           // 最后消息时间
  }
}

// 联系人请求（仅适用于人类用户）
interface ContactRequest {
  id: string
  fromUserId: string                 // 发送者ID
  fromUserName: string               // 发送者姓名
  fromUserAvatar: string             // 发送者头像
  toUserId: string                   // 接收者ID
  
  // 请求内容
  message: string                    // 附加消息
  requestType: 'friend' | 'colleague' | 'network'
  
  // 状态
  status: 'pending' | 'approved' | 'rejected' | 'expired'
  
  // 元数据
  createdAt: string
  updatedAt?: string
  expiresAt?: string                // 请求过期时间
  
  // 处理信息
  processedAt?: string
  processedBy?: string
  rejectionReason?: string
}

// 联系人过滤器
interface ContactFilter {
  type: 'all' | 'agent' | 'human' | 'pending' | 'favorites'
  tag?: string
  status?: 'online' | 'offline' | 'busy'
  relationship?: string
  searchQuery?: string
}
```

### 💬 **对话和消息系统**

#### **Conversation - 对话实体**
```typescript
interface Conversation {
  // 基础信息
  id: string                         // 对话唯一标识
  title: string                      // 对话标题
  description?: string               // 对话描述
  
  // 对话类型和设置
  type: 'direct' | 'group' | 'channel' | 'ai_agent'
  isPrivate: boolean                // 是否私密对话
  isArchived: boolean               // 是否归档
  isPinned: boolean                 // 是否置顶
  isMuted: boolean                  // 是否静音
  
  // 参与者
  participants: ConversationParticipant[]
  createdBy: string                 // 创建者ID
  
  // 消息统计
  messageCount: number              // 消息总数
  unreadCount: number               // 未读消息数
  lastMessage?: Message             // 最后一条消息
  
  // 对话设置
  settings: ConversationSettings
  
  // 元数据
  createdAt: string
  updatedAt: string
  lastActivityAt: string           // 最后活动时间
  
  // AI相关
  aiContext?: {
    activeAgents: string[]          // 活跃的AI代理
    conversationMemory?: string     // 对话记忆摘要
    topics: string[]                // 讨论话题
    mood: 'positive' | 'neutral' | 'negative' // 对话情绪
  }
  
  // 权限和安全
  permissions: {
    canAddParticipants: boolean
    canRemoveParticipants: boolean
    canDeleteMessages: boolean
    canPin: boolean
    canArchive: boolean
    canExport: boolean
  }
}

interface ConversationParticipant {
  id: string                        // 参与者ID
  type: 'human' | 'agent'           // 参与者类型
  name: string                      // 显示名称
  avatar?: string                   // 头像
  
  // 角色和权限
  role: 'owner' | 'admin' | 'member' | 'guest'
  permissions: string[]             // 具体权限
  
  // 状态
  status: 'active' | 'inactive' | 'left' | 'removed'
  isOnline: boolean                 // 在线状态
  lastSeenAt?: string              // 最后查看时间
  
  // 参与信息
  joinedAt: string                 // 加入时间
  invitedBy?: string               // 邀请者ID
  
  // 消息状态
  lastReadMessageId?: string       // 最后已读消息ID
  unreadCount: number              // 未读消息数
}

interface ConversationSettings {
  // 通知设置
  notifications: {
    muted: boolean
    muteUntil?: string
    soundEnabled: boolean
    desktopNotifications: boolean
    mentions: 'all' | 'mentions' | 'none'
  }
  
  // 消息设置
  messages: {
    retentionDays?: number          // 消息保留天数
    readReceipts: boolean           // 已读回执
    typingIndicators: boolean       // 打字指示器
    linkPreviews: boolean           // 链接预览
    autoDeleteEnabled: boolean      // 自动删除
  }
  
  // AI设置
  ai: {
    enabledAgents: string[]         // 启用的AI代理
    autoRespond: boolean            // 自动回复
    contextWindow: number           // 上下文窗口大小
    maxTokens: number              // 最大token限制
  }
  
  // 安全设置
  security: {
    endToEndEncryption: boolean     // 端到端加密
    allowFileSharing: boolean       // 允许文件分享
    allowLinkSharing: boolean       // 允许链接分享
    moderationEnabled: boolean      // 启用内容审核
  }
}

// 对话创建请求
interface CreateConversationRequest {
  title: string
  description?: string
  type: 'direct' | 'group' | 'channel'
  participants: string[]            // 参与者ID列表
  settings?: Partial<ConversationSettings>
  isPrivate?: boolean
}

// 对话更新请求  
interface UpdateConversationRequest {
  title?: string
  description?: string
  settings?: Partial<ConversationSettings>
  isArchived?: boolean
  isPinned?: boolean
}
```

#### **Message - 消息实体**
```typescript
interface Message {
  // 基础信息
  id: string                        // 消息唯一标识
  conversationId: string            // 所属对话ID
  senderId: string                  // 发送者ID
  senderType: 'human' | 'agent'     // 发送者类型
  
  // 消息内容
  content: string                   // 消息文本内容
  type: MessageType                 // 消息类型
  
  // 消息状态
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed'
  isEdited: boolean                 // 是否已编辑
  isDeleted: boolean                // 是否已删除
  
  // 回复和线程
  replyTo?: string                  // 回复的消息ID
  thread?: MessageThread            // 线程信息
  
  // 附件和富内容
  attachments: AttachmentInfo[]     // 附件列表
  embeds: EmbedInfo[]              // 嵌入内容
  
  // 交互数据
  reactions: MessageReaction[]      // 消息反应
  mentions: MessageMention[]        // @提及
  
  // 元数据
  createdAt: string
  updatedAt?: string
  editedAt?: string
  deletedAt?: string
  
  // 消息传递信息
  deliveryInfo?: {
    deliveredTo: string[]           // 已送达用户
    readBy: string[]                // 已读用户
    deliveredAt?: string
    readAt?: string
  }
  
  // AI相关
  aiGenerated?: boolean             // 是否AI生成
  aiMetadata?: {
    model: string                   // 使用的模型
    confidence: number              // 置信度
    processingTime: number          // 处理时间
    tokenUsage: number             // token使用量
  }
}

type MessageType = 
  | 'text'                         // 纯文本
  | 'rich_text'                    // 富文本
  | 'image'                        // 图片
  | 'file'                         // 文件
  | 'audio'                        // 音频
  | 'video'                        // 视频
  | 'location'                     // 位置
  | 'contact'                      // 联系人卡片
  | 'poll'                         // 投票
  | 'code'                         // 代码块
  | 'system'                       // 系统消息
  | 'ai_response'                  // AI回复

interface MessageThread {
  id: string                       // 线程ID
  rootMessageId: string            // 根消息ID
  messageCount: number             // 线程消息数
  participants: string[]           // 参与者
  lastReply?: string              // 最后回复时间
  lastReplyBy?: string            // 最后回复者
}

interface AttachmentInfo {
  id: string                       // 附件ID
  name: string                     // 文件名
  type: string                     // MIME类型
  size: number                     // 文件大小
  url: string                      // 下载URL
  thumbnailUrl?: string           // 缩略图URL
  metadata?: Record<string, any>   // 元数据
}

interface EmbedInfo {
  type: 'link' | 'image' | 'video' | 'audio' | 'document'
  url: string                      // 原始URL
  title?: string                   // 标题
  description?: string             // 描述
  thumbnailUrl?: string           // 缩略图
  metadata?: Record<string, any>   // 额外元数据
}

interface MessageReaction {
  emoji: string                    // 表情符号
  users: string[]                  // 使用该表情的用户
  count: number                    // 数量
  createdAt: string
}

interface MessageMention {
  id: string                       // 被提及者ID
  type: 'user' | 'agent' | 'all'   // 提及类型
  name: string                     // 显示名称
  startIndex: number               // 在文本中的起始位置
  length: number                   // 长度
}

// 消息草稿
interface MessageDraft {
  conversationId: string           // 对话ID
  content: string                  // 草稿内容
  attachments?: AttachmentInfo[]   // 临时附件
  replyTo?: string                // 回复消息ID
  lastSaved: string               // 最后保存时间
}

// 发送消息请求
interface SendMessageRequest {
  conversationId: string
  content: string
  type?: MessageType
  replyTo?: string
  attachments?: string[]           // 附件ID列表
  mentions?: MessageMention[]
  metadata?: Record<string, any>
}

// 消息搜索查询
interface MessageSearchQuery {
  query: string                    // 搜索关键词
  conversationId?: string          // 限定对话
  senderId?: string               // 限定发送者
  dateFrom?: string               // 开始日期
  dateTo?: string                 // 结束日期
  messageType?: MessageType        // 消息类型
  hasAttachments?: boolean        // 包含附件
  limit?: number                  // 结果限制
  offset?: number                 // 偏移量
}

interface MessageSearchResult {
  message: Message                 // 消息内容
  conversation: Pick<Conversation, 'id' | 'title' | 'type'>
  highlights: string[]             // 高亮片段
  score: number                   // 相关性得分
}
```

### 📁 **文件管理系统**

#### **File - 文件实体**
```typescript
interface FileEntity {
  // 基础信息
  id: string                       // 文件唯一标识
  name: string                     // 原始文件名
  displayName?: string             // 显示名称
  
  // 文件属性
  type: string                     // MIME类型
  size: number                     // 文件大小(bytes)
  extension: string                // 文件扩展名
  hash: string                     // 文件哈希值
  
  // 存储信息
  url: string                      // 访问URL
  thumbnailUrl?: string           // 缩略图URL
  previewUrl?: string             // 预览URL
  downloadUrl: string             // 下载URL
  storageProvider: 'supabase' | 'aws' | 'local'
  storagePath: string             // 存储路径
  
  // 所有权和权限
  ownerId: string                 // 所有者ID
  ownerType: 'user' | 'agent'     // 所有者类型
  visibility: 'private' | 'internal' | 'public'
  permissions: FilePermission[]   // 权限列表
  
  // 元数据
  createdAt: string
  updatedAt: string
  uploadedBy: string              // 上传者ID
  lastAccessedAt?: string         // 最后访问时间
  
  // 使用统计
  stats: {
    downloadCount: number         // 下载次数
    viewCount: number            // 查看次数
    shareCount: number           // 分享次数
    lastDownloadAt?: string      // 最后下载时间
  }
  
  // 分类和标签
  category: FileCategory
  tags: string[]                  // 自定义标签
  description?: string            // 文件描述
  
  // 处理状态
  processingStatus?: 'pending' | 'processing' | 'completed' | 'failed'
  processingProgress?: number     // 处理进度(0-100)
  
  // 文件特定属性
  mediaInfo?: MediaInfo           // 媒体文件信息
  documentInfo?: DocumentInfo     // 文档文件信息
}

type FileCategory = 
  | 'image'                       // 图片
  | 'document'                    // 文档
  | 'audio'                       // 音频
  | 'video'                       // 视频
  | 'archive'                     // 压缩包
  | 'code'                        // 代码文件
  | 'data'                        // 数据文件
  | 'other'                       // 其他

interface FilePermission {
  userId: string                  // 用户ID
  userType: 'user' | 'agent'      // 用户类型
  permission: 'read' | 'write' | 'delete' | 'share' | 'admin'
  grantedBy: string              // 授权者ID
  grantedAt: string              // 授权时间
  expiresAt?: string             // 过期时间
}

interface MediaInfo {
  duration?: number               // 时长(秒) - 音视频
  width?: number                  // 宽度 - 图片/视频
  height?: number                 // 高度 - 图片/视频  
  bitrate?: number               // 比特率 - 音视频
  codec?: string                 // 编解码器
  fps?: number                   // 帧率 - 视频
}

interface DocumentInfo {
  pageCount?: number             // 页数 - PDF等
  wordCount?: number             // 字数 - 文本文档
  language?: string              // 语言
  hasImages: boolean             // 是否包含图片
  extractedText?: string         // 提取的文本内容
}

// 文件上传请求
interface FileUploadRequest {
  file: File                     // 文件对象
  name?: string                  // 自定义名称
  category?: FileCategory        // 文件分类
  description?: string           // 描述
  tags?: string[]               // 标签
  visibility?: 'private' | 'internal' | 'public'
  permissions?: Partial<FilePermission>[]
}

// 文件搜索查询
interface FileSearchQuery {
  query?: string                 // 搜索关键词
  category?: FileCategory        // 文件分类
  ownerId?: string              // 所有者
  tags?: string[]               // 标签过滤
  dateFrom?: string             // 上传开始日期
  dateTo?: string               // 上传结束日期
  sizeMin?: number              // 最小大小
  sizeMax?: number              // 最大大小
  sortBy?: 'name' | 'date' | 'size' | 'downloads'
  sortOrder?: 'asc' | 'desc'
  limit?: number
  offset?: number
}
```

### 📰 **时间线和社交系统**

#### **TimelinePost - 时间线动态**
```typescript
interface TimelinePost {
  // 基础信息
  id: string                      // 动态ID
  authorId: string                // 作者ID
  authorType: 'user' | 'agent'    // 作者类型
  authorName: string              // 作者名称
  authorAvatar: string            // 作者头像
  
  // 内容信息
  content: string                 // 动态内容
  type: PostType                  // 动态类型
  title?: string                  // 标题
  summary?: string                // 摘要
  
  // 媒体内容
  attachments: AttachmentInfo[]   // 附件
  embeds: EmbedInfo[]            // 嵌入内容
  
  // 可见性和权限
  visibility: 'public' | 'friends' | 'private'
  targetAudience?: string[]       // 目标受众
  
  // 交互数据
  likes: TimelineLike[]           // 点赞
  comments: TimelineComment[]     // 评论
  shares: TimelineShare[]         // 分享
  
  // 统计信息
  stats: {
    likeCount: number             // 点赞数
    commentCount: number          // 评论数
    shareCount: number            // 分享数
    viewCount: number             // 查看数
  }
  
  // 元数据
  createdAt: string
  updatedAt?: string
  isEdited: boolean
  isPinned: boolean
  isArchived: boolean
  
  // AI相关
  aiGenerated?: boolean           // 是否AI生成
  aiMetadata?: {
    prompt?: string               // 生成提示
    model: string                 // 使用模型
    confidence: number            // 置信度
  }
}

type PostType = 
  | 'text'                        // 文本动态
  | 'image'                       // 图片动态
  | 'video'                       // 视频动态
  | 'link'                        // 链接分享
  | 'poll'                        // 投票
  | 'article'                     // 文章
  | 'achievement'                 // 成就
  | 'ai_creation'                 // AI创作
  | 'system'                      // 系统动态

interface TimelineLike {
  id: string
  userId: string                  // 点赞用户ID
  userType: 'user' | 'agent'      // 用户类型
  userName: string                // 用户名称
  createdAt: string
  reaction?: 'like' | 'love' | 'laugh' | 'wow' | 'sad' | 'angry'
}

interface TimelineComment {
  id: string                      // 评论ID
  postId: string                  // 所属动态ID
  authorId: string                // 评论作者ID
  authorType: 'user' | 'agent'    // 作者类型
  authorName: string              // 作者名称
  authorAvatar: string            // 作者头像
  
  content: string                 // 评论内容
  parentCommentId?: string        // 父评论ID(回复)
  
  // 交互
  likes: string[]                 // 点赞用户列表
  replies: TimelineComment[]      // 回复列表
  
  createdAt: string
  updatedAt?: string
  isEdited: boolean
}

interface TimelineShare {
  id: string
  userId: string                  // 分享用户ID
  userName: string                // 用户名称
  content?: string                // 分享时的评论
  createdAt: string
}

// 创建动态请求
interface CreateTimelinePostRequest {
  content: string
  type: PostType
  title?: string
  visibility: 'public' | 'friends' | 'private'
  attachments?: string[]          // 附件ID列表
  targetAudience?: string[]       // 指定受众
}
```

### 🔌 **插件系统**

#### **Plugin - 插件实体**
```typescript
interface Plugin {
  // 基础信息
  id: string                      // 插件唯一标识
  name: string                    // 插件名称
  displayName: string             // 显示名称
  version: string                 // 版本号
  description: string             // 简短描述
  longDescription?: string        // 详细描述
  icon: string                    // 图标URL
  
  // 开发者信息
  author: {
    name: string                  // 开发者名称
    email?: string                // 联系邮箱
    url?: string                  // 个人网站
    verified: boolean             // 是否认证开发者
  }
  
  // 分类和标签
  category: PluginCategory        // 插件分类
  tags: string[]                  // 标签
  
  // 状态和评级
  configured: boolean             // 是否已配置
  enabled: boolean                // 是否启用
  featured: boolean               // 是否精选
  verified: boolean               // 是否官方认证
  rating: number                  // 评分(1-5)
  downloadCount: number           // 下载次数
  
  // 功能特性
  features: PluginFeature[]       // 功能列表
  capabilities: PluginCapability[] // 能力描述
  requirements: string[]          // 系统要求
  permissions: PluginPermission[] // 所需权限
  
  // 配置信息
  configTemplate: PluginConfigTemplate // 配置模板
  currentConfig?: Record<string, any>   // 当前配置
  
  // 兼容性
  minVersion?: string             // 最低支持版本
  maxVersion?: string             // 最高支持版本
  dependencies: PluginDependency[] // 依赖项
  
  // 链接
  supportUrl?: string             // 支持链接
  documentationUrl?: string       // 文档链接
  githubUrl?: string             // GitHub链接
  homepageUrl?: string           // 主页链接
  
  // 元数据
  createdAt: string
  updatedAt: string
  lastUsedAt?: string            // 最后使用时间
  
  // 统计信息
  stats: {
    installCount: number          // 安装次数
    activeUsers: number           // 活跃用户数
    averageRating: number         // 平均评分
    reviewCount: number           // 评价数量
  }
}

type PluginCategory = 
  | 'ai_tools'                   // AI工具
  | 'productivity'               // 生产力
  | 'communication'              // 通信工具
  | 'integration'                // 集成服务
  | 'automation'                 // 自动化
  | 'analytics'                  // 分析工具
  | 'security'                   // 安全工具
  | 'entertainment'              // 娱乐
  | 'developer_tools'            // 开发工具
  | 'other'                      // 其他

interface PluginFeature {
  id: string                     // 功能ID
  name: string                   // 功能名称
  description: string            // 功能描述
  enabled: boolean               // 是否启用
}

interface PluginCapability {
  type: 'api_access' | 'file_access' | 'network_access' | 'ui_extension' | 'data_processing'
  description: string            // 能力描述
  scope: string[]               // 访问范围
}

interface PluginPermission {
  type: string                   // 权限类型
  description: string            // 权限说明
  required: boolean              // 是否必需
  dangerous: boolean             // 是否危险权限
}

interface PluginDependency {
  id: string                     // 依赖插件ID
  name: string                   // 依赖插件名称
  version: string                // 版本要求
  optional: boolean              // 是否可选
}

// 插件配置相关类型 (详细定义见plugin.ts文件)
interface PluginConfigTemplate {
  version: string
  sections: PluginConfigSection[]
  validation?: ValidationConfig
  preview?: PreviewConfig
}

interface PluginConfigSection {
  id: string
  title: string
  description?: string
  fields: ConfigField[]
  collapsible?: boolean
  defaultCollapsed?: boolean
}

// 插件操作请求
interface InstallPluginRequest {
  pluginId: string
  version?: string
  autoEnable?: boolean
}

interface ConfigurePluginRequest {
  pluginId: string
  config: Record<string, any>
  validate?: boolean
}

interface EnablePluginRequest {
  pluginId: string
  enabled: boolean
}
```

---

## 🔄 **实时通信和状态系统**

### 📡 **实时通信**
```typescript
interface RealtimeEvent {
  // 事件标识
  id: string                     // 事件ID
  type: RealtimeEventType        // 事件类型
  namespace: string              // 命名空间
  
  // 事件数据
  payload: any                   // 事件载荷
  metadata?: Record<string, any> // 元数据
  
  // 目标信息
  targetUsers?: string[]         // 目标用户
  targetConversations?: string[] // 目标对话
  broadcast?: boolean            // 是否广播
  
  // 事件元信息
  senderId: string              // 发送者ID
  senderType: 'user' | 'agent' | 'system'
  timestamp: string             // 时间戳
  sequence?: number             // 序列号
  
  // 传递状态
  status: 'pending' | 'sent' | 'delivered' | 'acknowledged'
  deliveredTo?: string[]        // 已送达列表
  acknowledgedBy?: string[]     // 已确认列表
}

type RealtimeEventType = 
  | 'message.new'               // 新消息
  | 'message.updated'           // 消息更新
  | 'message.deleted'           // 消息删除
  | 'typing.start'              // 开始打字
  | 'typing.stop'               // 停止打字
  | 'presence.online'           // 上线
  | 'presence.offline'          // 下线
  | 'presence.away'             // 离开
  | 'conversation.updated'      // 对话更新
  | 'participant.joined'        // 参与者加入
  | 'participant.left'          // 参与者离开
  | 'agent.mentioned'           // 代理被提及
  | 'file.uploaded'             // 文件上传
  | 'system.notification'       // 系统通知

interface PresenceInfo {
  userId: string                // 用户ID
  userType: 'user' | 'agent'    // 用户类型
  status: 'online' | 'away' | 'busy' | 'offline'
  lastSeen: string              // 最后在线时间
  device?: string               // 设备信息
  location?: string             // 地理位置
  customStatus?: string         // 自定义状态
  
  // 活动信息
  currentConversation?: string  // 当前对话
  isTyping?: boolean           // 是否正在打字
  lastActivity: string         // 最后活动时间
}

interface TypingIndicator {
  conversationId: string        // 对话ID
  userId: string               // 用户ID
  userName: string             // 用户名称
  startedAt: string            // 开始时间
  expiresAt: string            // 过期时间
}
```

### 🔔 **通知系统**
```typescript
interface Notification {
  // 基础信息
  id: string                    // 通知ID
  type: NotificationType        // 通知类型
  title: string                 // 标题
  message: string               // 消息内容
  
  // 目标用户
  userId: string                // 接收用户ID
  
  // 来源信息
  sourceId?: string             // 来源对象ID
  sourceType?: 'conversation' | 'user' | 'agent' | 'system'
  senderId?: string             // 发送者ID
  senderName?: string           // 发送者名称
  
  // 显示设置
  priority: 'low' | 'normal' | 'high' | 'urgent'
  category: 'message' | 'mention' | 'system' | 'social' | 'ai'
  
  // 状态
  status: 'unread' | 'read' | 'dismissed' | 'archived'
  persistent: boolean           // 是否持久化
  
  // 操作按钮
  actions?: NotificationAction[]
  
  // 元数据
  createdAt: string
  readAt?: string
  dismissedAt?: string
  expiresAt?: string
  
  // 媒体内容
  icon?: string                 // 图标
  image?: string               // 图片
  avatar?: string              // 头像
  
  // 路由信息
  clickAction?: {
    type: 'navigate' | 'modal' | 'external'
    target: string              // 目标路径或URL
    data?: Record<string, any>  // 额外数据
  }
}

type NotificationType = 
  | 'message'                   // 新消息
  | 'mention'                   // 被提及
  | 'reply'                     // 回复
  | 'reaction'                  // 消息反应
  | 'contact_request'           // 好友请求
  | 'contact_accepted'          // 好友接受
  | 'agent_response'            // AI回复
  | 'system_update'             // 系统更新
  | 'plugin_notification'       // 插件通知
  | 'file_shared'              // 文件分享
  | 'timeline_activity'         // 动态活动

interface NotificationAction {
  id: string                    // 操作ID
  label: string                 // 按钮文本
  type: 'primary' | 'secondary' | 'danger'
  action: string                // 操作类型
  data?: Record<string, any>    // 操作数据
}

// Toast通知
interface Toast extends Notification {
  duration?: number             // 显示时长(ms)
  position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center'
  closable: boolean            // 是否可关闭
}
```

---

## 📊 **API响应和分页结构**

### 🌐 **通用API响应**
```typescript
interface ApiResponse<T = any> {
  success: boolean              // 请求是否成功
  data?: T                      // 响应数据
  message?: string              // 响应消息
  error?: ApiError              // 错误信息
  timestamp: string             // 响应时间戳
  requestId: string             // 请求ID
}

interface ApiError {
  code: string                  // 错误代码
  message: string               // 错误消息
  details?: Record<string, any> // 详细信息
  field?: string               // 相关字段
  timestamp: string            // 错误时间
}

interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationInfo    // 分页信息
}

interface PaginationInfo {
  page: number                  // 当前页码
  limit: number                 // 每页数量
  total: number                 // 总数量
  totalPages: number            // 总页数
  hasNext: boolean             // 是否有下一页
  hasPrev: boolean             // 是否有上一页
  nextCursor?: string          // 下一页游标
  prevCursor?: string          // 上一页游标
}

// 通用查询参数
interface BaseQueryParams {
  page?: number                 // 页码
  limit?: number               // 每页数量
  cursor?: string              // 游标
  sortBy?: string              // 排序字段
  sortOrder?: 'asc' | 'desc'   // 排序方向
  search?: string              // 搜索关键词
  filters?: Record<string, any> // 过滤条件
}

// 批量操作请求
interface BulkOperationRequest {
  ids: string[]                // 目标ID列表
  operation: string            // 操作类型
  params?: Record<string, any> // 操作参数
}

interface BulkOperationResponse {
  success: boolean
  processed: number            // 处理数量
  failed: number              // 失败数量
  errors: Array<{
    id: string
    error: string
  }>
  results: Array<{
    id: string
    success: boolean
    data?: any
  }>
}
```

---

## 🧩 **业务逻辑和工作流**

### 🔍 **搜索系统**
```typescript
interface SearchQuery {
  query: string                // 搜索关键词
  type: 'all' | 'messages' | 'conversations' | 'users' | 'agents' | 'files'
  scope?: string[]            // 搜索范围
  filters: SearchFilters      // 过滤条件
  sorting: SearchSorting      // 排序设置
  pagination: SearchPagination // 分页设置
}

interface SearchFilters {
  dateFrom?: string           // 开始日期
  dateTo?: string            // 结束日期
  authors?: string[]         // 作者列表
  tags?: string[]            // 标签列表
  categories?: string[]      // 分类列表
  hasAttachments?: boolean   // 包含附件
  isAiGenerated?: boolean    // AI生成内容
  language?: string          // 语言
}

interface SearchSorting {
  field: 'relevance' | 'date' | 'popularity' | 'rating'
  order: 'asc' | 'desc'
}

interface SearchPagination {
  offset: number
  limit: number
  maxResults?: number        // 最大结果数
}

interface SearchResult {
  type: 'message' | 'conversation' | 'user' | 'agent' | 'file'
  id: string                 // 对象ID
  title: string              // 标题
  snippet: string            // 摘要
  highlights: string[]       // 高亮文本
  score: number              // 相关性得分
  metadata: Record<string, any> // 元数据
  createdAt: string
  updatedAt: string
}

interface SearchResponse {
  query: string              // 原始查询
  totalResults: number       // 总结果数
  searchTime: number         // 搜索耗时(ms)
  results: SearchResult[]    // 结果列表
  suggestions?: string[]     // 搜索建议
  relatedQueries?: string[]  // 相关查询
  facets: SearchFacet[]      // 分面信息
}

interface SearchFacet {
  field: string              // 字段名
  values: Array<{
    value: string            // 值
    count: number            // 数量
    selected: boolean        // 是否选中
  }>
}
```

### 📈 **分析和统计**
```typescript
interface UserAnalytics {
  userId: string
  period: 'day' | 'week' | 'month' | 'year'
  startDate: string
  endDate: string
  
  // 基础指标
  metrics: {
    messagesSent: number           // 发送消息数
    messagesReceived: number       // 接收消息数
    conversationsCreated: number   // 创建对话数
    conversationsJoined: number    // 加入对话数
    agentInteractions: number      // AI交互次数
    filesShared: number            // 分享文件数
    loginCount: number             // 登录次数
    activeTime: number             // 活跃时间(分钟)
  }
  
  // 详细统计
  detailed: {
    hourlyActivity: Array<{hour: number, count: number}>
    dailyActivity: Array<{date: string, count: number}>
    topContacts: Array<{id: string, name: string, messageCount: number}>
    topAgents: Array<{id: string, name: string, interactionCount: number}>
    messageTypes: Record<string, number>
    fileTypes: Record<string, number>
  }
  
  // 趋势数据
  trends: {
    messagesGrowth: number         // 消息增长率
    conversationsGrowth: number    // 对话增长率
    agentUsageGrowth: number       // AI使用增长率
    engagementScore: number        // 参与度得分
  }
}

interface ConversationAnalytics {
  conversationId: string
  period: string
  
  // 参与度指标
  participation: {
    totalMessages: number          // 总消息数
    activeParticipants: number     // 活跃参与者
    messagesByParticipant: Array<{
      userId: string
      userName: string
      messageCount: number
      wordCount: number
    }>
  }
  
  // AI使用情况
  aiUsage: {
    totalAiResponses: number       // AI响应总数
    uniqueAgentsUsed: number       // 使用的AI代理数
    averageResponseTime: number    // 平均响应时间
    agentBreakdown: Array<{
      agentId: string
      agentName: string
      responseCount: number
      averageRating: number
    }>
  }
  
  // 内容分析
  contentAnalysis: {
    topicTags: string[]           // 话题标签
    sentiment: 'positive' | 'neutral' | 'negative'
    languageDistribution: Record<string, number>
    averageMessageLength: number
    codeBlocksCount: number
    imagesSharedCount: number
    filesSharedCount: number
  }
}
```

---

## 🎯 **总结和后端对接建议**

### **数据类型完整性**
- ✅ **用户系统**: 完整的用户、角色、权限模型
- ✅ **AI代理系统**: 详细的能力描述和配置信息
- ✅ **通信系统**: 丰富的消息类型和对话管理
- ✅ **文件系统**: 完善的文件管理和权限控制
- ✅ **社交系统**: 时间线、评论、互动功能
- ✅ **实时系统**: 在线状态、事件推送、通知管理

### **后端实现优先级建议**

#### **Phase 1: 核心实体 (2-3周)**
1. User, AIAgent, ContactRelationship
2. Conversation, Message, ConversationParticipant  
3. BasicAuth和JWT系统

#### **Phase 2: 高级功能 (3-4周)**
4. FileEntity, FilePermission
5. RealtimeEvent, PresenceInfo
6. Notification系统

#### **Phase 3: 生态功能 (2-3周)**
7. TimelinePost, Plugin系统
8. Analytics和搜索功能
9. 高级权限和审计

### **技术实现要点**
- 🔐 **权限系统**: 基于角色的访问控制(RBAC)
- 🚀 **性能优化**: 数据库索引、缓存策略、分页查询
- 🔄 **实时通信**: WebSocket + 事件驱动架构  
- 📊 **数据一致性**: 事务管理、乐观锁、分布式锁
- 🧪 **可测试性**: Mock数据、单元测试、集成测试

这份规范为后端团队提供了详尽的数据模型参考，确保前后端数据结构的完美对接。
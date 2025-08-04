# BFF Service 数据库 Schema 设计

## 📋 核心数据模型概览

基于 Connet.AI 的业务需求，设计以下核心数据模型：

### 1. 用户系统 (Users)
- **UserModel** - 用户基础信息和认证
- **UserInvitationModel** - 用户邀请码管理
- **UserRegistrationSourceModel** - 用户注册渠道追踪

### 2. AI 代理系统 (Agents)  
- **AgentModel** - AI代理定义和配置（包含头像、RAG知识库关联）
- **AgentKnowledgeBaseModel** - 代理与知识库关联关系

### 3. 对话系统 (Conversations)
- **ConversationModel** - 对话/会话管理
- **ConversationParticipantModel** - 对话参与者关系
- **ConversationTopicModel** - 对话话题/子主题
- **MessageModel** - 消息内容和元数据

### 4. 文件系统 (Files)
- **FileModel** - 文件元数据和存储信息
- **FilePermissionModel** - 文件访问权限

### 5. 社交功能 (Social) - 人机并存社区
- **ContactModel** - 联系人/关注关系（支持用户关注AI代理）
- **TimelinePostModel** - 时间线内容（用户和AI代理共同发布）
- **TimelineCommentModel** - 时间线评论系统
- **TimelineLikeModel** - 时间线点赞系统

---

## 🗄️ 详细 Schema 设计

### 1. 用户系统模型

#### 1.1 用户模型 (UserModel) ✅ 已实现，需扩展

```python
class UserModel(SQLModel, table=True):
    __tablename__ = "users"
    
    # 主键和基础信息
    id: UUID = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    username: Optional[str] = Field(unique=True, index=True)
    
    # 认证信息
    password_hash: str
    is_active: bool = Field(default=True)
    
    # 邀请系统
    invitation_code: str = Field(unique=True, index=True)  # 用户专属邀请码
    invited_by_code: Optional[str] = Field(index=True)  # 使用的邀请码
    invited_by_user_id: Optional[UUID] = Field(foreign_key="users.id")  # 邀请人
    
    # 注册渠道信息
    registration_source: Optional[str] = Field(index=True)  # "web", "mobile", "api", "admin"
    registration_channel: Optional[str] = Field(index=True)  # "organic", "invite", "social", "campaign"
    utm_source: Optional[str] = None  # 营销追踪
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    # 扩展信息
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None
    permissions: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    metadata: Optional[dict] = None
    
    # 统计信息
    invitation_count: int = Field(default=0)  # 成功邀请人数
    total_conversations: int = Field(default=0)
    total_messages: int = Field(default=0)
```

#### 1.2 用户邀请模型 (UserInvitationModel)

```python
class UserInvitationModel(SQLModel, table=True):
    __tablename__ = "user_invitations"
    
    # 主键
    id: UUID = Field(primary_key=True)
    
    # 邀请码信息
    code: str = Field(unique=True, index=True)  # 邀请码
    invited_by: UUID = Field(foreign_key="users.id")  # 邀请人
    
    # 邀请设置
    max_uses: int = Field(default=1)  # 最大使用次数，-1表示无限制
    used_count: int = Field(default=0)  # 已使用次数
    expires_at: Optional[datetime] = None  # 过期时间
    
    # 状态
    is_active: bool = Field(default=True)
    
    # 邀请类型和奖励
    invitation_type: str = Field(default="standard")  # "standard", "premium", "beta"
    reward_config: Optional[dict] = None  # 邀请奖励配置
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 元数据
    metadata: Optional[dict] = None  # 额外信息
```

#### 1.3 用户注册来源追踪模型 (UserRegistrationSourceModel)

```python
class UserRegistrationSourceModel(SQLModel, table=True):
    __tablename__ = "user_registration_sources"
    
    # 主键
    id: UUID = Field(primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)  # 一对一关系
    
    # 详细渠道信息
    source_type: str  # "organic", "referral", "social", "campaign", "api"
    source_detail: Optional[str] = None  # 具体渠道详情
    
    # 设备和环境信息
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    device_type: Optional[str] = None  # "desktop", "mobile", "tablet"
    platform: Optional[str] = None  # "web", "ios", "android"
    
    # 营销追踪
    utm_data: Optional[dict] = None  # 完整的UTM参数
    referrer_url: Optional[str] = None
    landing_page: Optional[str] = None
    
    # 地理位置（如果可获取）
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    
    # 时间戳
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 额外元数据
    metadata: Optional[dict] = None
```

### 2. AI 代理系统模型

#### 2.1 AI 代理模型 (AgentModel)

```python
class AgentModel(SQLModel, table=True):
    __tablename__ = "agents"
    
    # 主键和基础信息
    id: UUID = Field(primary_key=True)
    name: str = Field(index=True)  # 代理名称 @code_assistant
    display_name: str  # 显示名称 "代码助手"
    description: str  # 代理描述
    
    # 视觉表现
    avatar_url: Optional[str] = None  # 代理头像
    avatar_style: Optional[str] = Field(default="default")  # "default", "anime", "realistic", "abstract"
    color_theme: Optional[str] = None  # 代理主题色 "#FF6B6B"
    
    # 代理配置
    model_config: dict  # AI模型配置 {"model": "gpt-4", "temperature": 0.7}
    system_prompt: str  # 系统提示词
    
    # 状态和权限
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=True)  # 是否公开可用
    created_by: UUID = Field(foreign_key="users.id")  # 创建者
    
    # 能力配置 (移除 agent_type，改用 tags)
    capabilities: List[str] = Field(default=[])  # ["code_generation", "debugging"]
    tools: List[str] = Field(default=[])  # 可用工具列表
    max_tokens: int = Field(default=2048)
    
    # 知识库关联 (通过关联表管理，这里只存摘要信息)
    knowledge_base_count: int = Field(default=0)  # 关联的知识库数量
    
    # 使用统计
    usage_count: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    avg_response_time: float = Field(default=0.0)
    follower_count: int = Field(default=0)  # 关注者数量
    
    # 社交属性（AI代理作为社区成员）
    personality_traits: List[str] = Field(default=[])  # ["helpful", "creative", "analytical"]
    communication_style: Optional[str] = Field(default="professional")  # "casual", "professional", "humorous"
    active_hours: Optional[dict] = None  # 活跃时间配置
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None  # 最后活跃时间
    
    # 分类和发现
    tags: List[str] = Field(default=[])  # 标签用于分类 ["coding", "assistant", "creative"]
    category: Optional[str] = Field(index=True)  # 主要分类
    
    # 元数据
    metadata: Optional[dict] = None
    
    # 向量嵌入（用于语义搜索）
    description_embedding: Optional[List[float]] = None
    capabilities_embedding: Optional[List[float]] = None
```

#### 2.2 代理知识库关联模型 (AgentKnowledgeBaseModel)

```python
class AgentKnowledgeBaseModel(SQLModel, table=True):
    __tablename__ = "agent_knowledge_bases"
    
    # 复合主键
    agent_id: UUID = Field(foreign_key="agents.id", primary_key=True)
    knowledge_base_id: str = Field(primary_key=True)  # 知识库系统的ID
    
    # 关联配置
    access_level: str = Field(default="read")  # "read", "write", "admin"
    priority: int = Field(default=1)  # 优先级，数字越大优先级越高
    is_active: bool = Field(default=True)
    
    # 使用配置
    max_context_tokens: Optional[int] = None  # 从此知识库检索的最大token数
    retrieval_config: Optional[dict] = None  # 检索配置参数
    
    # 知识库信息（冗余存储，用于快速查询）
    knowledge_base_name: Optional[str] = None
    knowledge_base_type: Optional[str] = None  # "documents", "qa", "code", "custom"
    
    # 统计信息
    usage_count: int = Field(default=0)  # 使用次数
    last_used_at: Optional[datetime] = None
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 元数据
    metadata: Optional[dict] = None
```

### 3. 对话系统模型

#### 3.1 对话模型 (ConversationModel)

```python
class ConversationModel(SQLModel, table=True):
    __tablename__ = "conversations"
    
    # 主键和基础信息
    id: UUID = Field(primary_key=True)
    title: str  # 对话标题
    conversation_type: str = Field(default="chat")  # "chat", "task", "project"
    
    # 对话状态
    status: str = Field(default="active")  # "active", "archived", "deleted"
    is_group: bool = Field(default=False)  # 是否群聊
    
    # 创建信息
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 最后活动
    last_message_at: Optional[datetime] = None
    last_message_id: Optional[UUID] = None
    
    # 设置
    settings: Optional[dict] = None  # 对话设置
    metadata: Optional[dict] = None
    
    # 统计信息
    message_count: int = Field(default=0)
    participant_count: int = Field(default=0)
    topic_count: int = Field(default=0)  # 话题数量
```

#### 3.2 对话话题模型 (ConversationTopicModel)

```python
class ConversationTopicModel(SQLModel, table=True):
    __tablename__ = "conversation_topics"
    
    # 主键和关联
    id: UUID = Field(primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    parent_topic_id: Optional[UUID] = Field(foreign_key="conversation_topics.id")  # 支持话题嵌套
    
    # 话题信息
    title: str  # 话题标题
    description: Optional[str] = None  # 话题描述
    topic_type: str = Field(default="discussion")  # "discussion", "task", "brainstorm", "decision"
    
    # 创建信息
    created_by: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 话题状态
    status: str = Field(default="active")  # "active", "resolved", "archived"
    priority: str = Field(default="normal")  # "low", "normal", "high", "urgent"
    
    # 时间管理
    start_message_id: Optional[UUID] = Field(foreign_key="messages.id")  # 话题起始消息
    due_date: Optional[datetime] = None  # 截止时间
    resolved_at: Optional[datetime] = None  # 解决时间
    resolved_by: Optional[UUID] = Field(foreign_key="users.id")
    
    # 统计信息
    message_count: int = Field(default=0)  # 话题相关消息数
    participant_count: int = Field(default=0)  # 参与者数量
    
    # 标签和分类
    tags: List[str] = Field(default=[])
    
    # 元数据
    metadata: Optional[dict] = None
    
    # 话题摘要（AI生成）
    ai_summary: Optional[str] = None
    summary_updated_at: Optional[datetime] = None
```

### 4. 对话参与者模型 (ConversationParticipantModel)

```python
class ConversationParticipantModel(SQLModel, table=True):
    __tablename__ = "conversation_participants"
    
    # 复合主键
    conversation_id: UUID = Field(foreign_key="conversations.id", primary_key=True)
    participant_id: UUID = Field(primary_key=True)  # 用户或代理ID
    participant_type: str = Field(primary_key=True)  # "user" 或 "agent"
    
    # 参与信息
    role: str = Field(default="member")  # "owner", "admin", "member"
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[UUID] = Field(foreign_key="users.id")
    
    # 状态
    is_active: bool = Field(default=True)
    last_read_at: Optional[datetime] = None
    last_read_message_id: Optional[UUID] = None
    
    # 设置
    notification_enabled: bool = Field(default=True)
    settings: Optional[dict] = None
```

### 5. 消息模型 (MessageModel)

```python
class MessageModel(SQLModel, table=True):
    __tablename__ = "messages"
    
    # 主键和关联
    id: UUID = Field(primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    
    # 发送者信息
    sender_id: UUID = Field(index=True)  # 用户或代理ID
    sender_type: str  # "user" 或 "agent"
    
    # 消息内容
    content: str  # 消息文本内容
    message_type: str = Field(default="text")  # "text", "image", "file", "system"
    
    # 消息元数据
    reply_to_id: Optional[UUID] = Field(foreign_key="messages.id")  # 回复的消息
    thread_id: Optional[UUID] = None  # 消息线程
    
    # AI 相关
    agent_mentions: List[str] = Field(default=[])  # @提及的代理
    ai_context: Optional[dict] = None  # AI处理上下文
    tokens_used: Optional[int] = None  # 使用的token数量
    
    # 状态和标记
    is_edited: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    is_system: bool = Field(default=False)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    edited_at: Optional[datetime] = None
    
    # 附件和多媒体
    attachments: List[str] = Field(default=[])  # 文件ID列表
    
    # 元数据
    metadata: Optional[dict] = None
    
    # 向量嵌入（用于语义搜索）
    content_embedding: Optional[List[float]] = None
```

### 6. 文件模型 (FileModel)

```python
class FileModel(SQLModel, table=True):
    __tablename__ = "files"
    
    # 主键和基础信息
    id: UUID = Field(primary_key=True)
    filename: str  # 原始文件名
    display_name: str  # 显示名称
    
    # 文件信息
    file_type: str  # MIME类型
    file_size: int  # 文件大小（字节）
    file_extension: str = Field(index=True)  # 文件扩展名
    
    # 存储信息
    storage_provider: str = Field(default="supabase")  # "supabase", "local", "s3"
    storage_path: str  # 存储路径
    storage_bucket: Optional[str] = None  # 存储桶
    
    # 上传信息
    uploaded_by: UUID = Field(foreign_key="users.id")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 文件状态
    status: str = Field(default="active")  # "active", "processing", "failed", "deleted"
    is_public: bool = Field(default=False)
    
    # 处理信息（用于图片、视频等）
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    processed_variants: Optional[dict] = None
    
    # 访问控制
    access_level: str = Field(default="private")  # "public", "shared", "private"
    download_count: int = Field(default=0)
    
    # 元数据
    metadata: Optional[dict] = None  # 文件元数据（EXIF等）
    description: Optional[str] = None
    tags: List[str] = Field(default=[])
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # 过期时间
```

### 7. 文件权限模型 (FilePermissionModel)

```python
class FilePermissionModel(SQLModel, table=True):
    __tablename__ = "file_permissions"
    
    # 复合主键
    file_id: UUID = Field(foreign_key="files.id", primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    
    # 权限设置
    permission_type: str  # "read", "write", "delete", "share"
    granted_by: UUID = Field(foreign_key="users.id")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 权限期限
    expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
```

### 8. 社交系统模型 - 人机并存社区

#### 8.1 联系人模型 (ContactModel) - 支持关注AI代理

```python
class ContactModel(SQLModel, table=True):
    __tablename__ = "contacts"
    
    # 复合主键
    follower_id: UUID = Field(foreign_key="users.id", primary_key=True)  # 关注者（只能是用户）
    following_id: UUID = Field(primary_key=True)  # 被关注者ID（用户或代理）
    following_type: str = Field(primary_key=True)  # "user" 或 "agent"
    
    # 关系类型
    relationship_type: str = Field(default="follow")  # "follow", "friend", "blocked", "muted"
    
    # 关系信息
    display_name: Optional[str] = None  # 自定义显示名称
    notes: Optional[str] = None  # 备注
    tags: List[str] = Field(default=[])
    
    # 状态
    is_favorite: bool = Field(default=False)  # 特别关注
    is_muted: bool = Field(default=False)  # 静音
    is_blocked: bool = Field(default=False)  # 屏蔽
    
    # 通知设置
    notification_level: str = Field(default="normal")  # "none", "important", "normal", "all"
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction_at: Optional[datetime] = None
```

#### 8.2 时间线内容模型 (TimelinePostModel) - 人机共同发布

```python
class TimelinePostModel(SQLModel, table=True):
    __tablename__ = "timeline_posts"
    
    # 主键和作者信息
    id: UUID = Field(primary_key=True)
    author_id: UUID = Field(index=True)  # 作者ID（用户或代理）
    author_type: str = Field(index=True)  # "user" 或 "agent"
    
    # 内容信息
    title: Optional[str] = None
    content: str
    content_type: str = Field(default="text")  # "text", "image", "link", "achievement", "thought", "update"
    
    # 可见性和受众
    visibility: str = Field(default="public")  # "public", "followers", "friends", "private"
    target_audience: List[str] = Field(default=[])  # 目标受众标签
    
    # 关联信息
    conversation_id: Optional[UUID] = Field(foreign_key="conversations.id")
    related_topic_id: Optional[UUID] = Field(foreign_key="conversation_topics.id")
    related_agent_id: Optional[UUID] = Field(foreign_key="agents.id")  # 相关代理
    parent_post_id: Optional[UUID] = Field(foreign_key="timeline_posts.id")  # 转发的原帖
    
    # AI代理特有字段
    agent_mood: Optional[str] = None  # AI代理"心情" "excited", "thoughtful", "helpful"
    generated_context: Optional[dict] = None  # AI生成内容的上下文
    
    # 互动统计
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    share_count: int = Field(default=0)
    view_count: int = Field(default=0)
    
    # 附件和多媒体
    attachments: List[str] = Field(default=[])  # 文件ID列表
    media_urls: List[str] = Field(default=[])  # 媒体文件URL
    
    # 标签和元数据
    tags: List[str] = Field(default=[])
    hashtags: List[str] = Field(default=[])  # 话题标签
    mentioned_users: List[str] = Field(default=[])  # @提及的用户
    mentioned_agents: List[str] = Field(default=[])  # @提及的代理
    
    # 位置和时间
    location: Optional[str] = None  # 地理位置
    scheduled_at: Optional[datetime] = None  # 定时发布
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # 状态
    status: str = Field(default="published")  # "draft", "scheduled", "published", "archived", "deleted"
    is_pinned: bool = Field(default=False)
    is_featured: bool = Field(default=False)  # 精选内容
    
    # 元数据
    metadata: Optional[dict] = None
```

#### 8.3 时间线评论模型 (TimelineCommentModel)

```python
class TimelineCommentModel(SQLModel, table=True):
    __tablename__ = "timeline_comments"
    
    # 主键和关联
    id: UUID = Field(primary_key=True)
    post_id: UUID = Field(foreign_key="timeline_posts.id", index=True)
    parent_comment_id: Optional[UUID] = Field(foreign_key="timeline_comments.id")  # 支持评论嵌套
    
    # 评论者信息
    author_id: UUID = Field(index=True)  # 评论者ID（用户或代理）
    author_type: str  # "user" 或 "agent"
    
    # 评论内容
    content: str
    content_type: str = Field(default="text")  # "text", "image", "sticker"
    
    # 互动统计
    like_count: int = Field(default=0)
    reply_count: int = Field(default=0)
    
    # 提及和标签
    mentioned_users: List[str] = Field(default=[])
    mentioned_agents: List[str] = Field(default=[])
    
    # 附件
    attachments: List[str] = Field(default=[])
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 状态
    is_deleted: bool = Field(default=False)
    is_edited: bool = Field(default=False)
    
    # 元数据
    metadata: Optional[dict] = None
```

#### 8.4 时间线互动模型 (TimelineLikeModel)

```python
class TimelineLikeModel(SQLModel, table=True):
    __tablename__ = "timeline_likes"
    
    # 复合主键
    user_id: UUID = Field(foreign_key="users.id", primary_key=True)  # 点赞者（只能是用户）
    target_id: UUID = Field(primary_key=True)  # 目标ID（帖子或评论）
    target_type: str = Field(primary_key=True)  # "post" 或 "comment"
    
    # 互动类型
    reaction_type: str = Field(default="like")  # "like", "love", "laugh", "wow", "sad", "angry"
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # 元数据
    metadata: Optional[dict] = None
```

---

## 🔗 关系映射总结

### 主要关系

#### 用户系统关系
1. **用户 ↔ 邀请**: 一对多（用户可以有多个邀请码）
2. **用户 ↔ 注册来源**: 一对一（每个用户一条注册追踪记录）
3. **用户 ↔ 用户**: 多对多（邀请关系，自关联）

#### AI代理系统关系
4. **用户 ↔ 代理**: 一对多（创建关系）
5. **代理 ↔ 知识库**: 多对多（代理可关联多个知识库）

#### 对话系统关系
6. **用户/代理 ↔ 对话**: 多对多（通过 ConversationParticipant）
7. **对话 ↔ 话题**: 一对多（对话可以有多个话题）
8. **话题 ↔ 话题**: 一对多（话题可以嵌套，自关联）
9. **对话/话题 ↔ 消息**: 一对多

#### 文件系统关系
10. **用户 ↔ 文件**: 一对多（上传关系）
11. **文件 ↔ 权限**: 一对多（文件可授权给多个用户）

#### 社交系统关系（人机并存）
12. **用户 ↔ 用户/代理**: 多对多（关注关系，通过 Contact）
13. **用户/代理 ↔ 时间线帖子**: 一对多（发布关系）
14. **时间线帖子 ↔ 评论**: 一对多
15. **评论 ↔ 评论**: 一对多（评论嵌套，自关联）
16. **用户 ↔ 点赞**: 一对多（用户可以点赞帖子和评论）

### 核心设计亮点

#### 🤖 人机并存社区
- **统一身份体系**: 用户和AI代理在社交层面平等
- **关注机制**: 用户可以关注其他用户或AI代理
- **内容创作**: AI代理可以主动发布时间线内容
- **互动参与**: AI代理可以评论、被评论、被点赞

#### 🧠 AI智能增强
- **知识库集成**: 代理可关联多个RAG知识库
- **语义搜索**: 代理和消息支持向量嵌入搜索
- **个性化配置**: 代理有独特的性格、风格、活跃时间

#### 📈 增长机制
- **邀请系统**: 完整的邀请码和奖励机制
- **渠道追踪**: 详细的用户来源和营销数据追踪
- **社交传播**: 时间线内容支持分享和病毒式传播

#### 🎯 对话增强
- **话题管理**: 对话内可以创建和管理多个子话题
- **任务协作**: 话题支持状态管理和截止时间
- **AI摘要**: 自动生成话题摘要

### 索引策略

#### 高频查询字段
- `email, username` (用户查找)
- `conversation_id, author_id, created_at` (消息查询)
- `follower_id, following_id, following_type` (社交关系)
- `post_id, author_type, published_at` (时间线内容)

#### 搜索字段
- `name, display_name, description` (代理搜索)
- `title, content` (对话和时间线搜索)
- `tags, hashtags` (标签搜索)

#### 外键字段
- 所有 `foreign_key` 字段自动索引
- 复合主键自动创建复合索引

### 向量搜索支持

#### pgvector 集成
- **AgentModel**: `description_embedding, capabilities_embedding`
- **MessageModel**: `content_embedding`  
- **TimelinePostModel**: 可扩展支持 `content_embedding`

### 扩展性设计

#### 元数据字段
- 所有模型都有 `metadata` 字段支持未来扩展
- 配置字段使用 JSON 类型支持灵活配置

#### 软删除支持
- 重要内容支持 `is_deleted` 软删除
- 保留数据用于审计和恢复

---

## 📊 模型统计

- **总模型数**: 12个核心模型
- **用户系统**: 3个模型（User, Invitation, RegistrationSource）
- **AI代理系统**: 2个模型（Agent, AgentKnowledgeBase）
- **对话系统**: 4个模型（Conversation, Topic, Participant, Message）
- **文件系统**: 2个模型（File, FilePermission）
- **社交系统**: 4个模型（Contact, TimelinePost, Comment, Like）

---

## ✅ 请您确认

请审查这些 Schema 设计，确认：

1. **业务完整性** - 是否覆盖了人机并存社区的所有核心场景？
2. **字段合理性** - 新增的邀请、RAG、话题、评论字段是否合适？
3. **关系正确性** - 特别是人机并存的社交关系映射是否准确？
4. **扩展性** - 是否为未来功能预留了足够的扩展空间？
5. **遗漏检查** - 是否还有重要的业务场景遗漏？

确认无误后，我将开始创建具体的 SQLModel 实现文件。
# Backend Architecture Design - Connet.AI

## 架构设计原则

### 1. 可扩展性 (Scalability)
- **微服务准备**: 单体应用设计为易于拆分的微服务架构
- **水平扩展**: 支持负载均衡和水平扩展
- **数据库优化**: 读写分离、分片、索引优化
- **缓存分层**: 多级缓存策略提升性能

### 2. 清晰性 (Clarity)
- **分层架构**: API层、业务逻辑层、数据访问层清晰分离
- **领域驱动**: 基于业务领域组织代码结构
- **标准化**: 统一的API设计规范和错误处理
- **文档驱动**: 每个服务都有详细的API文档

### 3. 维护性 (Maintainability)
- **单一职责**: 每个模块职责明确
- **依赖注入**: 松耦合的依赖关系
- **测试覆盖**: 完整的单元测试和集成测试
- **监控可观测**: 全面的日志、监控、追踪

## 整体架构概览

```
Backend Architecture (FastAPI + Supabase)
│
├── 🌐 API Gateway Layer (FastAPI)
│   ├── Authentication & Authorization
│   ├── Rate Limiting & Throttling
│   ├── Request/Response Validation
│   └── API Documentation (OpenAPI)
│
├── 🏗️ Application Services Layer
│   ├── AI Agent Service (LangChain/LangGraph)
│   ├── Chat Service (实时消息处理)
│   ├── User Management Service
│   ├── File Management Service
│   ├── Notification Service
│   └── Plugin System Service
│
├── 🧠 Business Logic Layer
│   ├── Domain Models (业务实体)
│   ├── Business Rules (业务规则)
│   ├── Use Cases (用例处理)
│   └── Domain Events (领域事件)
│
├── 🗄️ Data Access Layer
│   ├── Repository Pattern (数据访问抽象)
│   ├── ORM Integration (SQLModel/SQLAlchemy)
│   ├── Cache Manager (Redis缓存)
│   └── Vector Store (pgvector语义搜索)
│
├── 🔧 Infrastructure Layer
│   ├── Database (Supabase PostgreSQL)
│   ├── Real-time (Supabase Realtime)
│   ├── Storage (Supabase Storage)
│   ├── Task Queue (ARQ + Redis)
│   └── External APIs (OpenAI, 第三方服务)
│
└── 🛡️ Cross-cutting Concerns
    ├── Logging & Monitoring (结构化日志)
    ├── Error Handling (统一异常处理)
    ├── Security (认证、授权、加密)
    ├── Configuration (环境配置管理)
    └── Health Checks (服务健康检查)
```

## 详细目录结构设计

```
backend-web/
├── app/                              # 应用核心代码
│   ├── __init__.py
│   ├── main.py                       # FastAPI应用入口
│   ├── config/                       # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py               # 应用配置
│   │   ├── database.py               # 数据库配置
│   │   ├── redis.py                  # Redis配置
│   │   ├── supabase.py               # Supabase配置
│   │   └── logging.py                # 日志配置
│   │
│   ├── api/                          # API层
│   │   ├── __init__.py
│   │   ├── dependencies.py           # API依赖项
│   │   ├── middleware.py             # 中间件
│   │   ├── exceptions.py             # 异常处理
│   │   └── v1/                       # API版本控制
│   │       ├── __init__.py
│   │       ├── router.py             # 主路由器
│   │       └── endpoints/            # API端点
│   │           ├── __init__.py
│   │           ├── auth.py           # 认证相关API
│   │           ├── users.py          # 用户管理API
│   │           ├── agents.py         # AI代理API
│   │           ├── conversations.py  # 对话API
│   │           ├── messages.py       # 消息API
│   │           ├── contacts.py       # 联系人API
│   │           ├── files.py          # 文件管理API
│   │           ├── timeline.py       # 时间线API
│   │           ├── plugins.py        # 插件API
│   │           ├── webhooks.py       # Webhook处理
│   │           └── health.py         # 健康检查
│   │
│   ├── services/                     # 应用服务层
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础服务类
│   │   ├── auth_service.py           # 认证服务
│   │   ├── user_service.py           # 用户服务
│   │   ├── agent_service.py          # AI代理服务
│   │   ├── chat_service.py           # 聊天服务
│   │   ├── message_service.py        # 消息服务
│   │   ├── contact_service.py        # 联系人服务
│   │   ├── file_service.py           # 文件服务
│   │   ├── timeline_service.py       # 时间线服务
│   │   ├── plugin_service.py         # 插件服务
│   │   ├── notification_service.py   # 通知服务
│   │   └── search_service.py         # 搜索服务
│   │
│   ├── core/                         # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── domain/                   # 领域模型
│   │   │   ├── __init__.py
│   │   │   ├── entities/             # 实体类
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── agent.py
│   │   │   │   ├── conversation.py
│   │   │   │   ├── message.py
│   │   │   │   └── file.py
│   │   │   ├── value_objects/        # 值对象
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_id.py
│   │   │   │   ├── agent_capability.py
│   │   │   │   └── message_content.py
│   │   │   └── events/               # 领域事件
│   │   │       ├── __init__.py
│   │   │       ├── user_events.py
│   │   │       ├── message_events.py
│   │   │       └── agent_events.py
│   │   │
│   │   ├── use_cases/                # 用例处理
│   │   │   ├── __init__.py
│   │   │   ├── auth/
│   │   │   │   ├── login_user.py
│   │   │   │   ├── register_user.py
│   │   │   │   └── refresh_token.py
│   │   │   ├── chat/
│   │   │   │   ├── create_conversation.py
│   │   │   │   ├── send_message.py
│   │   │   │   ├── mention_agent.py
│   │   │   │   └── get_conversation_history.py
│   │   │   ├── agents/
│   │   │   │   ├── search_agents.py
│   │   │   │   ├── create_agent.py
│   │   │   │   └── update_agent.py
│   │   │   └── files/
│   │   │       ├── upload_file.py
│   │   │       ├── download_file.py
│   │   │       └── manage_permissions.py
│   │   │
│   │   └── interfaces/               # 接口定义
│   │       ├── __init__.py
│   │       ├── repositories/         # 仓储接口
│   │       │   ├── user_repository.py
│   │       │   ├── agent_repository.py
│   │       │   ├── conversation_repository.py
│   │       │   └── message_repository.py
│   │       ├── services/             # 服务接口
│   │       │   ├── ai_service.py
│   │       │   ├── storage_service.py
│   │       │   └── notification_service.py
│   │       └── external/             # 外部服务接口
│   │           ├── llm_provider.py
│   │           ├── vector_store.py
│   │           └── file_storage.py
│   │
│   ├── infrastructure/               # 基础设施层
│   │   ├── __init__.py
│   │   ├── database/                 # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── connection.py         # 数据库连接
│   │   │   ├── models/               # SQLModel数据模型
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_model.py
│   │   │   │   ├── agent_model.py
│   │   │   │   ├── conversation_model.py
│   │   │   │   ├── message_model.py
│   │   │   │   └── file_model.py
│   │   │   ├── repositories/         # 数据访问实现
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_repository.py
│   │   │   │   ├── user_repository_impl.py
│   │   │   │   ├── agent_repository_impl.py
│   │   │   │   ├── conversation_repository_impl.py
│   │   │   │   └── message_repository_impl.py
│   │   │   └── migrations/           # 数据库迁移
│   │   │       ├── env.py
│   │   │       └── versions/
│   │   │
│   │   ├── cache/                    # 缓存层
│   │   │   ├── __init__.py
│   │   │   ├── redis_client.py       # Redis客户端
│   │   │   ├── cache_manager.py      # 缓存管理器
│   │   │   ├── cache_keys.py         # 缓存键管理
│   │   │   └── cache_decorators.py   # 缓存装饰器
│   │   │
│   │   ├── external/                 # 外部服务集成
│   │   │   ├── __init__.py
│   │   │   ├── supabase/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py         # Supabase客户端
│   │   │   │   ├── auth.py           # Supabase认证
│   │   │   │   ├── storage.py        # Supabase存储
│   │   │   │   └── realtime.py       # 实时功能
│   │   │   ├── openai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py
│   │   │   │   └── models.py
│   │   │   ├── langchain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chains.py
│   │   │   │   └── agents.py
│   │   │   └── vector_store/
│   │   │       ├── __init__.py
│   │   │       ├── pgvector.py
│   │   │       └── embeddings.py
│   │   │
│   │   ├── messaging/                # 消息和事件
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py          # 事件总线
│   │   │   ├── message_broker.py     # 消息代理
│   │   │   └── handlers/             # 事件处理器
│   │   │       ├── __init__.py
│   │   │       ├── user_handlers.py
│   │   │       └── message_handlers.py
│   │   │
│   │   └── security/                 # 安全相关
│   │       ├── __init__.py
│   │       ├── auth.py               # 认证实现
│   │       ├── permissions.py        # 权限管理
│   │       ├── encryption.py         # 加密工具
│   │       └── rate_limiting.py      # 限流实现
│   │
│   ├── ai/                           # AI系统
│   │   ├── __init__.py
│   │   ├── agents/                   # AI代理实现
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py         # 基础代理类
│   │   │   ├── chat_agent.py         # 聊天代理
│   │   │   ├── task_agent.py         # 任务处理代理
│   │   │   ├── planner_agent.py      # 规划代理
│   │   │   └── specialist_agents/    # 专业代理
│   │   │       ├── code_agent.py
│   │   │       ├── design_agent.py
│   │   │       └── writing_agent.py
│   │   │
│   │   ├── graphs/                   # LangGraph工作流
│   │   │   ├── __init__.py
│   │   │   ├── chat_graph.py         # 聊天流程图
│   │   │   ├── multi_agent_graph.py  # 多代理协作图
│   │   │   └── task_planning_graph.py # 任务规划图
│   │   │
│   │   ├── tools/                    # AI工具
│   │   │   ├── __init__.py
│   │   │   ├── base_tool.py          # 基础工具类
│   │   │   ├── search_tool.py        # 搜索工具
│   │   │   ├── file_tool.py          # 文件处理工具
│   │   │   └── api_tool.py           # API调用工具
│   │   │
│   │   ├── memory/                   # 记忆管理
│   │   │   ├── __init__.py
│   │   │   ├── conversation_memory.py # 对话记忆
│   │   │   ├── user_memory.py        # 用户记忆
│   │   │   └── agent_memory.py       # 代理记忆
│   │   │
│   │   ├── prompts/                  # 提示模板
│   │   │   ├── __init__.py
│   │   │   ├── chat_prompts.py
│   │   │   ├── agent_prompts.py
│   │   │   └── system_prompts.py
│   │   │
│   │   └── evaluation/               # AI评估
│   │       ├── __init__.py
│   │       ├── response_quality.py   # 响应质量评估
│   │       ├── performance_metrics.py # 性能指标
│   │       └── safety_checks.py      # 安全检查
│   │
│   ├── workers/                      # 后台任务
│   │   ├── __init__.py
│   │   ├── base_worker.py            # 基础worker类
│   │   ├── ai_worker.py              # AI处理worker
│   │   ├── notification_worker.py    # 通知worker
│   │   ├── file_processing_worker.py # 文件处理worker
│   │   ├── cleanup_worker.py         # 清理任务worker
│   │   └── tasks/                    # 任务定义
│   │       ├── __init__.py
│   │       ├── ai_tasks.py
│   │       ├── notification_tasks.py
│   │       └── maintenance_tasks.py
│   │
│   ├── schemas/                      # Pydantic数据模型
│   │   ├── __init__.py
│   │   ├── base.py                   # 基础schema类
│   │   ├── auth.py                   # 认证相关schema
│   │   ├── user.py                   # 用户schema
│   │   ├── agent.py                  # 代理schema
│   │   ├── conversation.py           # 对话schema
│   │   ├── message.py                # 消息schema
│   │   ├── file.py                   # 文件schema
│   │   ├── timeline.py               # 时间线schema
│   │   ├── plugin.py                 # 插件schema
│   │   └── responses.py              # API响应schema
│   │
│   ├── utils/                        # 工具函数
│   │   ├── __init__.py
│   │   ├── datetime.py               # 日期时间工具
│   │   ├── encryption.py             # 加密工具
│   │   ├── validators.py             # 验证工具
│   │   ├── formatters.py             # 格式化工具
│   │   ├── constants.py              # 常量定义
│   │   └── helpers.py                # 辅助函数
│   │
│   └── tests/                        # 测试代码
│       ├── __init__.py
│       ├── conftest.py               # pytest配置
│       ├── fixtures/                 # 测试数据
│       │   ├── __init__.py
│       │   ├── user_fixtures.py
│       │   ├── agent_fixtures.py
│       │   └── message_fixtures.py
│       ├── unit/                     # 单元测试
│       │   ├── test_services/
│       │   ├── test_use_cases/
│       │   ├── test_repositories/
│       │   └── test_utils/
│       ├── integration/              # 集成测试
│       │   ├── test_api/
│       │   ├── test_database/
│       │   └── test_ai/
│       └── e2e/                      # 端到端测试
│           ├── test_auth_flow.py
│           ├── test_chat_flow.py
│           └── test_agent_flow.py
│
├── alembic/                          # 数据库迁移
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── scripts/                          # 脚本文件
│   ├── start_dev.py                  # 开发启动脚本
│   ├── create_admin.py               # 创建管理员
│   ├── seed_data.py                  # 数据种子
│   ├── backup_db.py                  # 数据库备份
│   └── health_check.py               # 健康检查脚本
│
├── docs/                            # API文档
│   ├── api/                         # OpenAPI文档
│   ├── deployment/                  # 部署文档
│   └── development/                 # 开发文档
│
├── docker/                          # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   └── nginx.conf
│
├── .env.example                     # 环境变量示例
├── .gitignore
├── pyproject.toml                   # Python项目配置
├── requirements.txt                 # 依赖列表
├── alembic.ini                      # Alembic配置
└── README.md
```

## 核心架构模式

### 1. 领域驱动设计 (DDD)

#### 1.1 领域分层
```python
# 领域模型架构
class DomainArchitecture:
    """
    领域驱动设计分层结构
    """
    
    # 领域层 (Domain Layer)
    domain: Dict = {
        "entities": "核心业务实体",
        "value_objects": "值对象",
        "domain_services": "领域服务", 
        "domain_events": "领域事件",
        "aggregates": "聚合根"
    }
    
    # 应用层 (Application Layer)
    application: Dict = {
        "use_cases": "用例处理",
        "application_services": "应用服务",
        "dto": "数据传输对象",
        "interfaces": "接口定义"
    }
    
    # 基础设施层 (Infrastructure Layer)
    infrastructure: Dict = {
        "repositories": "仓储实现",
        "external_services": "外部服务",
        "database": "数据库访问",
        "messaging": "消息传递"
    }
    
    # 接口层 (Interface Layer)
    interface: Dict = {
        "api": "REST API",
        "websockets": "WebSocket接口",
        "graphql": "GraphQL接口（可选）",
        "cli": "命令行接口"
    }
```

#### 1.2 聚合设计
```python
# 聚合根示例
class ConversationAggregate:
    """对话聚合根"""
    
    def __init__(self, conversation_id: ConversationId):
        self.id = conversation_id
        self.messages: List[Message] = []
        self.participants: List[Participant] = []
        self.metadata: ConversationMetadata = ConversationMetadata()
        self._domain_events: List[DomainEvent] = []
    
    def add_message(self, message: Message) -> None:
        """添加消息到对话"""
        # 业务规则验证
        self._validate_message_constraints(message)
        
        # 添加消息
        self.messages.append(message)
        
        # 发布领域事件
        self._domain_events.append(
            MessageAddedEvent(
                conversation_id=self.id,
                message_id=message.id,
                sender_id=message.sender_id
            )
        )
    
    def mention_agent(self, agent_id: AgentId, mentioner_id: UserId) -> None:
        """在对话中@代理"""
        # 验证权限
        self._validate_mention_permissions(mentioner_id)
        
        # 添加代理到对话
        agent_participant = AgentParticipant(
            agent_id=agent_id,
            joined_at=datetime.utcnow(),
            invited_by=mentioner_id
        )
        self.participants.append(agent_participant)
        
        # 发布事件
        self._domain_events.append(
            AgentMentionedEvent(
                conversation_id=self.id,
                agent_id=agent_id,
                mentioner_id=mentioner_id
            )
        )
    
    def get_domain_events(self) -> List[DomainEvent]:
        """获取领域事件"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """清除领域事件"""
        self._domain_events.clear()
```

### 2. 仓储模式 (Repository Pattern)

#### 2.1 仓储接口定义
```python
# 抽象仓储接口
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')
ID = TypeVar('ID')

class BaseRepository(ABC, Generic[T, ID]):
    """基础仓储接口"""
    
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """根据ID获取实体"""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """保存实体"""
        pass
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """删除实体"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """查找所有实体"""
        pass

class ConversationRepository(BaseRepository[Conversation, ConversationId]):
    """对话仓储接口"""
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UserId) -> List[Conversation]:
        """根据用户ID查找对话"""
        pass
    
    @abstractmethod
    async def find_by_participant(self, participant_id: ID) -> List[Conversation]:
        """根据参与者查找对话"""
        pass
    
    @abstractmethod
    async def find_recent_messages(
        self, 
        conversation_id: ConversationId, 
        limit: int = 50
    ) -> List[Message]:
        """获取最近消息"""
        pass

# 仓储实现
class SQLConversationRepository(ConversationRepository):
    """对话仓储SQL实现"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: ConversationId) -> Optional[Conversation]:
        """根据ID获取对话"""
        stmt = select(ConversationModel).where(ConversationModel.id == id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            return self._model_to_entity(model)
        return None
    
    async def save(self, conversation: Conversation) -> Conversation:
        """保存对话"""
        model = self._entity_to_model(conversation)
        
        # 如果是新实体则添加，否则合并
        if model.id is None:
            self.session.add(model)
        else:
            await self.session.merge(model)
        
        await self.session.commit()
        await self.session.refresh(model)
        
        return self._model_to_entity(model)
    
    def _model_to_entity(self, model: ConversationModel) -> Conversation:
        """模型转实体"""
        # 实现转换逻辑
        pass
    
    def _entity_to_model(self, entity: Conversation) -> ConversationModel:
        """实体转模型"""
        # 实现转换逻辑
        pass
```

### 3. 服务层架构

#### 3.1 应用服务设计
```python
# 应用服务基类
class BaseApplicationService:
    """基础应用服务"""
    
    def __init__(
        self,
        event_bus: EventBus,
        logger: Logger,
        cache: CacheManager
    ):
        self.event_bus = event_bus
        self.logger = logger
        self.cache = cache
    
    async def _publish_events(self, aggregate: AggregateRoot) -> None:
        """发布聚合中的领域事件"""
        events = aggregate.get_domain_events()
        for event in events:
            await self.event_bus.publish(event)
        aggregate.clear_domain_events()

# 聊天服务实现
class ChatService(BaseApplicationService):
    """聊天应用服务"""
    
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        user_repo: UserRepository,
        agent_repo: AgentRepository,
        ai_service: AIService,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.conversation_repo = conversation_repo
        self.user_repo = user_repo
        self.agent_repo = agent_repo
        self.ai_service = ai_service
    
    async def send_message(self, request: SendMessageRequest) -> MessageResponse:
        """发送消息用例"""
        try:
            # 1. 验证用户权限
            user = await self.user_repo.get_by_id(request.user_id)
            if not user:
                raise UserNotFoundError(request.user_id)
            
            # 2. 获取对话聚合
            conversation = await self.conversation_repo.get_by_id(request.conversation_id)
            if not conversation:
                raise ConversationNotFoundError(request.conversation_id)
            
            # 3. 验证用户是否有权限发送消息
            if not conversation.can_user_send_message(request.user_id):
                raise InsufficientPermissionError("Cannot send message to this conversation")
            
            # 4. 创建消息
            message = Message.create(
                content=request.content,
                sender_id=request.user_id,
                message_type=request.message_type,
                metadata=request.metadata
            )
            
            # 5. 添加消息到对话
            conversation.add_message(message)
            
            # 6. 保存对话
            updated_conversation = await self.conversation_repo.save(conversation)
            
            # 7. 发布领域事件
            await self._publish_events(conversation)
            
            # 8. 如果消息包含@提及，处理AI代理响应
            if request.mentions:
                await self._handle_agent_mentions(
                    conversation_id=request.conversation_id,
                    mentions=request.mentions,
                    context=message
                )
            
            self.logger.info(
                f"Message sent successfully",
                extra={
                    "user_id": request.user_id,
                    "conversation_id": request.conversation_id,
                    "message_id": message.id
                }
            )
            
            return MessageResponse.from_entity(message)
            
        except Exception as e:
            self.logger.error(
                f"Failed to send message: {str(e)}",
                extra={
                    "user_id": request.user_id,
                    "conversation_id": request.conversation_id,
                    "error": str(e)
                }
            )
            raise
    
    async def _handle_agent_mentions(
        self,
        conversation_id: ConversationId,
        mentions: List[AgentMention],
        context: Message
    ) -> None:
        """处理AI代理@提及"""
        for mention in mentions:
            # 异步处理AI响应
            await self.ai_service.generate_response_async(
                agent_id=mention.agent_id,
                conversation_id=conversation_id,
                context=context,
                mention=mention
            )
```

#### 3.2 领域服务设计
```python
# 领域服务
class AgentMentionService:
    """代理@提及领域服务"""
    
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo
    
    async def can_mention_agent(
        self, 
        agent_id: AgentId, 
        user_id: UserId,
        conversation_id: ConversationId
    ) -> bool:
        """验证是否可以@指定代理"""
        agent = await self.agent_repo.get_by_id(agent_id)
        if not agent:
            return False
        
        # 检查代理可用性
        if not agent.is_available():
            return False
        
        # 检查用户权限
        if not agent.can_be_mentioned_by(user_id):
            return False
        
        # 检查对话类型限制
        if not agent.supports_conversation_type(conversation_id):
            return False
        
        return True
    
    def parse_mentions_from_content(self, content: str) -> List[AgentMention]:
        """从消息内容中解析@提及"""
        # 正则表达式匹配@提及
        import re
        pattern = r'@(\w+)(?:\[([^\]]+)\])?'
        matches = re.findall(pattern, content)
        
        mentions = []
        for match in matches:
            agent_name = match[0]
            instructions = match[1] if match[1] else None
            
            mentions.append(AgentMention(
                agent_name=agent_name,
                instructions=instructions,
                position=content.find(f'@{agent_name}')
            ))
        
        return mentions
```

## AI系统架构

### 1. LangChain/LangGraph集成

#### 1.1 AI代理基础架构
```python
# AI代理基类
from langchain.agents import BaseAgent
from langgraph import Graph, StateGraph
from typing import Dict, Any, List

class ConnetAIAgent(BaseAgent):
    """Connet.AI基础代理类"""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[str],
        model_config: Dict[str, Any],
        tools: List[BaseTool] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.model_config = model_config
        self.tools = tools or []
        self.memory = ConversationBufferMemory()
        
        # 初始化LLM
        self.llm = self._initialize_llm()
        
        # 初始化工具
        self._setup_tools()
    
    def _initialize_llm(self):
        """初始化语言模型"""
        from langchain.llms import OpenAI
        return OpenAI(
            model_name=self.model_config.get('model', 'gpt-3.5-turbo'),
            temperature=self.model_config.get('temperature', 0.7),
            max_tokens=self.model_config.get('max_tokens', 2048)
        )
    
    def _setup_tools(self):
        """设置工具"""
        # 基础工具
        basic_tools = [
            SearchTool(),
            CalculatorTool(),
            DateTimeTool()
        ]
        
        # 根据能力添加专业工具
        if 'code_generation' in self.capabilities:
            basic_tools.append(CodeExecutionTool())
        
        if 'file_analysis' in self.capabilities:
            basic_tools.append(FileAnalysisTool())
        
        self.tools.extend(basic_tools)
    
    async def process_message(
        self,
        message: str,
        conversation_context: ConversationContext,
        user_context: UserContext
    ) -> AgentResponse:
        """处理消息并生成响应"""
        try:
            # 1. 构建prompt上下文
            context = self._build_context(
                message=message,
                conversation_context=conversation_context,
                user_context=user_context
            )
            
            # 2. 使用LangGraph处理复杂决策
            if self._requires_complex_processing(message):
                return await self._process_with_graph(context)
            else:
                return await self._process_simple(context)
                
        except Exception as e:
            return AgentResponse(
                content=f"抱歉，处理您的请求时遇到了问题：{str(e)}",
                response_type=ResponseType.ERROR,
                confidence=0.0
            )
    
    async def _process_with_graph(self, context: Dict[str, Any]) -> AgentResponse:
        """使用LangGraph处理复杂任务"""
        # 定义状态图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("analyze", self._analyze_request)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("execute", self._execute_plan)
        workflow.add_node("review", self._review_result)
        
        # 添加边
        workflow.add_edge("analyze", "plan")
        workflow.add_edge("plan", "execute")  
        workflow.add_edge("execute", "review")
        
        # 设置入口点
        workflow.set_entry_point("analyze")
        
        # 编译图
        app = workflow.compile()
        
        # 执行图
        result = await app.ainvoke({"context": context})
        
        return AgentResponse(
            content=result["final_response"],
            response_type=ResponseType.SUCCESS,
            confidence=result.get("confidence", 0.8),
            metadata=result.get("metadata", {})
        )

# 专业AI代理实现
class CodeAssistantAgent(ConnetAIAgent):
    """代码助手代理"""
    
    def __init__(self):
        super().__init__(
            agent_id="code_assistant",
            name="代码助手",
            capabilities=[
                "code_generation",
                "code_review", 
                "debugging",
                "documentation"
            ],
            model_config={
                "model": "gpt-4",
                "temperature": 0.2,
                "max_tokens": 4096
            }
        )
    
    def _setup_tools(self):
        """设置代码相关工具"""
        super()._setup_tools()
        
        # 添加代码专用工具
        self.tools.extend([
            CodeExecutionTool(),
            GitHubTool(),
            DocumentationTool(),
            LintingTool(),
            TestGenerationTool()
        ])

class DesignConsultantAgent(ConnetAIAgent):
    """设计顾问代理"""
    
    def __init__(self):
        super().__init__(
            agent_id="design_consultant",
            name="设计顾问",
            capabilities=[
                "ui_design",
                "ux_analysis",
                "design_review",
                "prototyping"
            ],
            model_config={
                "model": "gpt-4-vision-preview",
                "temperature": 0.7,
                "max_tokens": 3000
            }
        )
    
    def _setup_tools(self):
        """设置设计相关工具"""
        super()._setup_tools()
        
        self.tools.extend([
            ColorPaletteTool(),
            TypographyTool(),
            LayoutAnalysisTool(),
            AccessibilityCheckerTool(),
            DesignSystemTool()
        ])
```

#### 1.2 多代理协作图
```python
# 多代理协作系统
class MultiAgentCollaborationGraph:
    """多代理协作图"""
    
    def __init__(self, agents: Dict[str, ConnetAIAgent]):
        self.agents = agents
        self.coordinator = AgentCoordinator()
        self.workflow = self._build_collaboration_workflow()
    
    def _build_collaboration_workflow(self) -> StateGraph:
        """构建协作工作流"""
        workflow = StateGraph(CollaborationState)
        
        # 协调者节点
        workflow.add_node("coordinator", self._coordinate_agents)
        
        # 代理节点
        for agent_id, agent in self.agents.items():
            workflow.add_node(agent_id, agent.process_message)
        
        # 汇总节点
        workflow.add_node("synthesizer", self._synthesize_responses)
        
        # 动态边：根据任务类型路由到不同代理
        workflow.add_conditional_edges(
            "coordinator",
            self._route_to_agents,
            list(self.agents.keys())
        )
        
        # 所有代理完成后汇总
        for agent_id in self.agents.keys():
            workflow.add_edge(agent_id, "synthesizer")
        
        workflow.set_entry_point("coordinator")
        workflow.set_finish_point("synthesizer")
        
        return workflow.compile()
    
    async def process_collaborative_task(
        self,
        task: CollaborativeTask,
        conversation_context: ConversationContext
    ) -> CollaborativeResponse:
        """处理协作任务"""
        
        state = CollaborationState(
            task=task,
            context=conversation_context,
            agent_responses={},
            coordination_plan=None,
            final_response=None
        )
        
        result = await self.workflow.ainvoke(state)
        
        return CollaborativeResponse(
            content=result["final_response"],
            participating_agents=result["participating_agents"],
            coordination_metadata=result["coordination_metadata"]
        )
    
    def _route_to_agents(self, state: CollaborationState) -> List[str]:
        """根据任务内容路由到相应代理"""
        task_keywords = state.task.keywords
        required_capabilities = state.task.required_capabilities
        
        selected_agents = []
        
        # 基于能力匹配选择代理
        for agent_id, agent in self.agents.items():
            if any(cap in agent.capabilities for cap in required_capabilities):
                selected_agents.append(agent_id)
        
        # 基于关键词选择代理
        keyword_agent_mapping = {
            'code': ['code_assistant', 'architect'],
            'design': ['design_consultant', 'ui_specialist'],
            'content': ['content_writer', 'editor'],
            'analysis': ['data_analyst', 'research_assistant']
        }
        
        for keyword in task_keywords:
            if keyword in keyword_agent_mapping:
                selected_agents.extend(keyword_agent_mapping[keyword])
        
        # 去重并限制最大代理数量
        selected_agents = list(set(selected_agents))[:5]
        
        return selected_agents if selected_agents else ['general_assistant']
```

### 2. 向量存储和语义搜索

#### 2.1 向量存储架构
```python
# 向量存储服务
class VectorStoreService:
    """向量存储服务"""
    
    def __init__(
        self,
        db_session: AsyncSession,
        embedding_model: str = "text-embedding-ada-002"
    ):
        self.db_session = db_session
        self.embedding_client = OpenAIEmbeddings(model=embedding_model)
        self.vector_store = PGVectorStore(db_session)
    
    async def store_agent_embeddings(self, agent: AIAgent) -> None:
        """存储AI代理的向量嵌入"""
        # 生成代理描述的嵌入
        description_embedding = await self.embedding_client.aembed_query(
            agent.description
        )
        
        # 生成能力的嵌入
        capabilities_text = " ".join(agent.capabilities)
        capabilities_embedding = await self.embedding_client.aembed_query(
            capabilities_text
        )
        
        # 存储到数据库
        await self.vector_store.store_embeddings(
            entity_id=agent.id,
            entity_type="agent",
            embeddings={
                "description": description_embedding,
                "capabilities": capabilities_embedding
            }
        )
    
    async def semantic_search_agents(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[AgentSearchResult]:
        """语义搜索AI代理"""
        
        # 生成查询嵌入
        query_embedding = await self.embedding_client.aembed_query(query)
        
        # 向量相似度搜索
        results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            entity_type="agent",
            limit=limit,
            threshold=threshold
        )
        
        # 加载代理详细信息
        agent_results = []
        for result in results:
            agent = await self._load_agent_by_id(result.entity_id)
            if agent:
                agent_results.append(
                    AgentSearchResult(
                        agent=agent,
                        similarity_score=result.similarity,
                        match_type=result.match_type
                    )
                )
        
        return agent_results
    
    async def store_conversation_embeddings(
        self,
        conversation_id: str,
        messages: List[Message]
    ) -> None:
        """存储对话的向量嵌入"""
        
        # 为每条消息生成嵌入
        for message in messages:
            if message.content:
                embedding = await self.embedding_client.aembed_query(
                    message.content
                )
                
                await self.vector_store.store_embeddings(
                    entity_id=message.id,
                    entity_type="message",
                    embeddings={"content": embedding},
                    metadata={
                        "conversation_id": conversation_id,
                        "sender_id": message.sender_id,
                        "timestamp": message.created_at
                    }
                )
    
    async def find_similar_conversations(
        self,
        query: str,
        user_id: str,
        limit: int = 5
    ) -> List[ConversationSummary]:
        """查找相似对话"""
        
        query_embedding = await self.embedding_client.aembed_query(query)
        
        # 搜索相似消息
        similar_messages = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            entity_type="message",
            limit=limit * 3,  # 多获取一些候选
            filters={"user_id": user_id}
        )
        
        # 按对话分组并汇总
        conversation_groups = {}
        for msg_result in similar_messages:
            conv_id = msg_result.metadata["conversation_id"]
            if conv_id not in conversation_groups:
                conversation_groups[conv_id] = []
            conversation_groups[conv_id].append(msg_result)
        
        # 生成对话摘要
        summaries = []
        for conv_id, messages in conversation_groups.items():
            if len(summaries) >= limit:
                break
                
            conversation = await self._load_conversation_summary(conv_id)
            if conversation:
                avg_similarity = sum(m.similarity for m in messages) / len(messages)
                summaries.append(
                    ConversationSummary(
                        conversation=conversation,
                        similarity_score=avg_similarity,
                        matching_messages=len(messages)
                    )
                )
        
        return sorted(summaries, key=lambda x: x.similarity_score, reverse=True)
```

## 缓存架构

### 1. 多级缓存策略

#### 1.1 缓存层设计
```python
# 缓存管理器
class CacheManager:
    """多级缓存管理器"""
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        local_cache: Optional[TTLCache] = None
    ):
        self.redis = redis_client
        self.local_cache = local_cache or TTLCache(maxsize=1000, ttl=300)
        self.metrics = CacheMetrics()
    
    async def get(self, key: str, default=None) -> Any:
        """获取缓存值（多级查找）"""
        cache_key = self._normalize_key(key)
        
        # 1. 本地缓存查找
        if cache_key in self.local_cache:
            self.metrics.record_hit("local")
            return self.local_cache[cache_key]
        
        # 2. Redis缓存查找
        try:
            value = await self.redis.get(cache_key)
            if value is not None:
                # 反序列化
                deserialized_value = self._deserialize(value)
                # 写入本地缓存
                self.local_cache[cache_key] = deserialized_value
                self.metrics.record_hit("redis")
                return deserialized_value
        except Exception as e:
            logger.warning(f"Redis cache error: {e}")
        
        # 3. 缓存未命中
        self.metrics.record_miss()
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
        local_ttl: int = 300
    ) -> None:
        """设置缓存值"""
        cache_key = self._normalize_key(key)
        
        # 序列化值
        serialized_value = self._serialize(value)
        
        # 设置Redis缓存
        try:
            await self.redis.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            logger.warning(f"Failed to set Redis cache: {e}")
        
        # 设置本地缓存
        if local_ttl > 0:
            self.local_cache[cache_key] = value
    
    async def delete(self, key: str) -> None:
        """删除缓存"""
        cache_key = self._normalize_key(key)
        
        # 删除本地缓存
        self.local_cache.pop(cache_key, None)
        
        # 删除Redis缓存
        try:
            await self.redis.delete(cache_key)
        except Exception as e:
            logger.warning(f"Failed to delete Redis cache: {e}")
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """按模式失效缓存"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
                
            # 清理本地缓存中匹配的键
            import re
            regex_pattern = pattern.replace('*', '.*')
            to_remove = [
                key for key in self.local_cache.keys()
                if re.match(regex_pattern, key)
            ]
            for key in to_remove:
                self.local_cache.pop(key, None)
                
        except Exception as e:
            logger.warning(f"Failed to invalidate cache pattern {pattern}: {e}")

# 缓存装饰器
def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    key_generator: Optional[Callable] = None
):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{key_prefix}:{func.__name__}:{hash_args(args, kwargs)}"
            
            # 尝试从缓存获取
            cache_manager = get_cache_manager()  # 从依赖注入获取
            cached_result = await cache_manager.get(cache_key)
            
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator

# 使用示例
class AgentService:
    
    @cached(ttl=1800, key_prefix="agent")
    async def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """获取代理信息（带缓存）"""
        return await self.agent_repository.get_by_id(agent_id)
    
    @cached(
        ttl=3600,
        key_generator=lambda self, query, limit: f"agent_search:{hash(query)}:{limit}"
    )
    async def search_agents(self, query: str, limit: int = 10) -> List[Agent]:
        """搜索代理（带缓存）"""
        return await self.vector_store.semantic_search_agents(query, limit)
```

### 2. 缓存失效策略

#### 2.1 智能缓存失效
```python
# 缓存失效管理器
class CacheInvalidationManager:
    """缓存失效管理器"""
    
    def __init__(self, cache_manager: CacheManager, event_bus: EventBus):
        self.cache_manager = cache_manager
        self.event_bus = event_bus
        self._setup_event_handlers()
    
    def _setup_event_handlers(self) -> None:
        """设置事件处理器"""
        # 用户相关事件
        self.event_bus.subscribe(UserUpdatedEvent, self._handle_user_updated)
        self.event_bus.subscribe(UserDeletedEvent, self._handle_user_deleted)
        
        # 代理相关事件
        self.event_bus.subscribe(AgentUpdatedEvent, self._handle_agent_updated)
        self.event_bus.subscribe(AgentDeletedEvent, self._handle_agent_deleted)
        
        # 对话相关事件
        self.event_bus.subscribe(MessageSentEvent, self._handle_message_sent)
        self.event_bus.subscribe(ConversationUpdatedEvent, self._handle_conversation_updated)
    
    async def _handle_user_updated(self, event: UserUpdatedEvent) -> None:
        """处理用户更新事件"""
        user_id = event.user_id
        
        # 失效用户相关缓存
        await self.cache_manager.invalidate_pattern(f"user:{user_id}:*")
        await self.cache_manager.invalidate_pattern(f"*:user:{user_id}")
        
        # 失效用户的对话列表缓存
        await self.cache_manager.invalidate_pattern(f"conversations:user:{user_id}")
        
        logger.info(f"Invalidated cache for user {user_id}")
    
    async def _handle_agent_updated(self, event: AgentUpdatedEvent) -> None:
        """处理代理更新事件"""
        agent_id = event.agent_id
        
        # 失效代理相关缓存
        await self.cache_manager.invalidate_pattern(f"agent:{agent_id}:*")
        
        # 失效代理搜索缓存
        await self.cache_manager.invalidate_pattern("agent_search:*")
        
        # 失效代理推荐缓存
        await self.cache_manager.invalidate_pattern("agent_recommendations:*")
        
        logger.info(f"Invalidated cache for agent {agent_id}")
    
    async def _handle_message_sent(self, event: MessageSentEvent) -> None:
        """处理消息发送事件"""
        conversation_id = event.conversation_id
        
        # 失效对话消息缓存
        await self.cache_manager.invalidate_pattern(f"messages:{conversation_id}:*")
        
        # 失效对话列表缓存（更新最后消息时间）
        participants = event.participants
        for participant_id in participants:
            await self.cache_manager.invalidate_pattern(f"conversations:user:{participant_id}")
        
        logger.debug(f"Invalidated message cache for conversation {conversation_id}")
```

## 实时通信架构

### 1. WebSocket管理

#### 1.1 连接管理器
```python
# WebSocket连接管理器
class WebSocketConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.connection_metadata: Dict[str, ConnectionMetadata] = {}
        self.lock = asyncio.Lock()
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        connection_type: str = "main"
    ) -> str:
        """建立WebSocket连接"""
        await websocket.accept()
        
        connection_id = self._generate_connection_id()
        
        async with self.lock:
            # 初始化用户连接字典
            if user_id not in self.active_connections:
                self.active_connections[user_id] = {}
                self.user_connections[user_id] = set()
            
            # 添加连接
            self.active_connections[user_id][connection_id] = websocket
            self.user_connections[user_id].add(connection_id)
            
            # 存储连接元数据
            self.connection_metadata[connection_id] = ConnectionMetadata(
                user_id=user_id,
                connection_type=connection_type,
                connected_at=datetime.utcnow()
            )
        
        # 发送连接确认
        await self._send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 广播用户上线状态
        await self._broadcast_presence_update(user_id, "online")
        
        logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")
        return connection_id
    
    async def disconnect(self, connection_id: str) -> None:
        """断开WebSocket连接"""
        async with self.lock:
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return
            
            user_id = metadata.user_id
            
            # 移除连接
            if user_id in self.active_connections:
                self.active_connections[user_id].pop(connection_id, None)
                
                if connection_id in self.user_connections.get(user_id, set()):
                    self.user_connections[user_id].remove(connection_id)
                
                # 如果用户没有其他连接，清理用户记录
                if not self.user_connections[user_id]:
                    del self.active_connections[user_id]
                    del self.user_connections[user_id]
                    
                    # 广播用户离线状态
                    await self._broadcast_presence_update(user_id, "offline")
            
            # 清理连接元数据
            del self.connection_metadata[connection_id]
        
        logger.info(f"WebSocket disconnected: connection={connection_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """向用户发送消息"""
        connections = self.active_connections.get(user_id, {})
        
        if not connections:
            logger.warning(f"No active connections for user {user_id}")
            return
        
        # 向用户的所有连接发送消息
        disconnected_connections = []
        for connection_id, websocket in connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to connection {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)
    
    async def broadcast_to_conversation(
        self,
        conversation_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ) -> None:
        """向对话中的所有用户广播消息"""
        # 获取对话参与者
        participants = await self._get_conversation_participants(conversation_id)
        
        # 广播给所有参与者
        for participant_id in participants:
            if exclude_user and participant_id == exclude_user:
                continue
                
            await self.send_to_user(participant_id, {
                **message,
                "conversation_id": conversation_id
            })
    
    async def _send_to_connection(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """向特定连接发送消息"""
        metadata = self.connection_metadata.get(connection_id)
        if not metadata:
            return False
        
        user_id = metadata.user_id
        websocket = self.active_connections.get(user_id, {}).get(connection_id)
        
        if not websocket:
            return False
        
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.warning(f"Failed to send to connection {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
    
    def get_user_presence(self, user_id: str) -> UserPresence:
        """获取用户在线状态"""
        connections = self.active_connections.get(user_id, {})
        
        if not connections:
            return UserPresence(
                user_id=user_id,
                status="offline",
                last_seen=None
            )
        
        # 检查连接活跃度
        active_connections = 0
        latest_activity = None
        
        for connection_id in connections:
            metadata = self.connection_metadata.get(connection_id)
            if metadata:
                active_connections += 1
                if not latest_activity or metadata.last_activity > latest_activity:
                    latest_activity = metadata.last_activity
        
        status = "online" if active_connections > 0 else "offline"
        
        return UserPresence(
            user_id=user_id,
            status=status,
            active_connections=active_connections,
            last_seen=latest_activity
        )

# WebSocket路由处理
class WebSocketHandler:
    """WebSocket消息处理器"""
    
    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        message_service: MessageService,
        presence_service: PresenceService
    ):
        self.connection_manager = connection_manager
        self.message_service = message_service
        self.presence_service = presence_service
        
        # 消息类型处理器映射
        self.handlers = {
            "ping": self._handle_ping,
            "send_message": self._handle_send_message,
            "typing_start": self._handle_typing_start,
            "typing_stop": self._handle_typing_stop,
            "join_conversation": self._handle_join_conversation,
            "leave_conversation": self._handle_leave_conversation,
        }
    
    async def handle_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> None:
        """处理WebSocket消息"""
        message_type = message.get("type")
        handler = self.handlers.get(message_type)
        
        if not handler:
            await self._send_error(connection_id, f"Unknown message type: {message_type}")
            return
        
        try:
            await handler(connection_id, message)
        except Exception as e:
            logger.error(f"Error handling message {message_type}: {e}")
            await self._send_error(connection_id, "Internal server error")
    
    async def _handle_send_message(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> None:
        """处理发送消息"""
        try:
            # 提取消息数据
            conversation_id = message["conversation_id"]
            content = message["content"]
            message_type = message.get("message_type", "text")
            
            # 获取用户ID
            metadata = self.connection_manager.connection_metadata[connection_id]
            user_id = metadata.user_id
            
            # 通过服务层发送消息
            sent_message = await self.message_service.send_message(
                SendMessageRequest(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    content=content,
                    message_type=message_type
                )
            )
            
            # 广播消息给对话参与者
            await self.connection_manager.broadcast_to_conversation(
                conversation_id=conversation_id,
                message={
                    "type": "message_received",
                    "message": sent_message.dict(),
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )
            
            # 向发送者确认
            await self.connection_manager._send_to_connection(connection_id, {
                "type": "message_sent",
                "message": sent_message.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            await self._send_error(connection_id, f"Failed to send message: {str(e)}")
    
    async def _handle_typing_start(
        self,
        connection_id: str,
        message: Dict[str, Any]
    ) -> None:
        """处理开始输入"""
        conversation_id = message.get("conversation_id")
        if not conversation_id:
            return
        
        metadata = self.connection_manager.connection_metadata[connection_id]
        user_id = metadata.user_id
        
        # 广播输入状态
        await self.connection_manager.broadcast_to_conversation(
            conversation_id=conversation_id,
            message={
                "type": "user_typing_start",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        # 更新输入状态
        await self.presence_service.set_typing_status(
            user_id=user_id,
            conversation_id=conversation_id,
            is_typing=True
        )
```

## 安全架构

### 1. 认证和授权

#### 1.1 JWT令牌管理
```python
# JWT管理器
class JWTManager:
    """JWT令牌管理器"""
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(
        self,
        subject: str,
        scopes: List[str] = None,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "scopes": scopes or []
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, subject: str) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        # 实现令牌黑名单检查逻辑
        # 通常使用Redis存储被撤销的令牌JTI
        pass

# 权限管理器
class PermissionManager:
    """权限管理器"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
    
    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """检查用户权限"""
        
        # 从缓存获取用户权限
        cache_key = f"permissions:user:{user_id}"
        user_permissions = await self.cache_manager.get(cache_key)
        
        if user_permissions is None:
            user_permissions = await self._load_user_permissions(user_id)
            await self.cache_manager.set(cache_key, user_permissions, ttl=1800)
        
        # 检查权限
        permission_key = f"{resource}:{action}"
        
        # 直接权限检查
        if permission_key in user_permissions.get("direct", []):
            return True
        
        # 角色权限检查
        user_roles = user_permissions.get("roles", [])
        for role in user_roles:
            role_permissions = await self._get_role_permissions(role)
            if permission_key in role_permissions:
                return True
        
        # 上下文权限检查（如资源所有者权限）
        if context:
            return await self._check_context_permissions(
                user_id, resource, action, context
            )
        
        return False
    
    async def _check_context_permissions(
        self,
        user_id: str,
        resource: str,
        action: str,
        context: Dict[str, Any]
    ) -> bool:
        """检查上下文权限"""
        
        # 资源所有者权限
        if resource == "conversation" and action in ["read", "write"]:
            conversation_id = context.get("conversation_id")
            if conversation_id:
                return await self._is_conversation_participant(user_id, conversation_id)
        
        if resource == "file" and action in ["read", "download"]:
            file_id = context.get("file_id")
            if file_id:
                return await self._has_file_access(user_id, file_id)
        
        if resource == "agent" and action == "use":
            agent_id = context.get("agent_id")
            if agent_id:
                return await self._can_use_agent(user_id, agent_id)
        
        return False

# 认证依赖项
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """获取当前用户（FastAPI依赖项）"""
    
    try:
        # 验证令牌
        payload = jwt_manager.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise InvalidTokenError("Token missing subject")
        
        # 检查令牌类型
        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")
        
        # 检查令牌是否被撤销
        if await jwt_manager.is_token_blacklisted(token):
            raise InvalidTokenError("Token has been revoked")
        
        # 获取用户信息
        user = await user_service.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        
        # 检查用户状态
        if not user.is_active:
            raise InactiveUserError("User account is inactive")
        
        return user
        
    except JWTError:
        raise InvalidTokenError("Could not validate credentials")

# 权限检查装饰器
def require_permission(resource: str, action: str):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户（假设在kwargs中）
            current_user = kwargs.get("current_user")
            if not current_user:
                raise UnauthorizedError("Authentication required")
            
            # 获取权限管理器
            permission_manager = get_permission_manager()
            
            # 构建上下文
            context = {k: v for k, v in kwargs.items() if k.endswith("_id")}
            
            # 检查权限
            has_permission = await permission_manager.check_permission(
                user_id=current_user.id,
                resource=resource,
                action=action,
                context=context
            )
            
            if not has_permission:
                raise ForbiddenError(f"Insufficient permissions for {resource}:{action}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 监控和可观测性

### 1. 结构化日志

#### 1.1 日志管理器
```python
# 结构化日志管理器
import structlog
from typing import Dict, Any, Optional

class LogManager:
    """结构化日志管理器"""
    
    def __init__(self, service_name: str, environment: str):
        self.service_name = service_name
        self.environment = environment
        self._setup_logging()
    
    def _setup_logging(self):
        """设置结构化日志"""
        
        # 配置structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # 获取logger
        self.logger = structlog.get_logger()
        
        # 绑定服务信息
        self.logger = self.logger.bind(
            service=self.service_name,
            environment=self.environment
        )
    
    def get_logger(self, **context) -> structlog.BoundLogger:
        """获取绑定上下文的logger"""
        return self.logger.bind(**context)
    
    def log_api_request(
        self,
        method: str,
        path: str,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        status_code: Optional[int] = None,
        **extra
    ):
        """记录API请求日志"""
        logger = self.get_logger(
            event_type="api_request",
            method=method,
            path=path,
            user_id=user_id,
            duration_ms=duration_ms,
            status_code=status_code,
            **extra
        )
        
        if status_code and status_code >= 400:
            logger.warning("API request failed")
        else:
            logger.info("API request completed")
    
    def log_ai_interaction(
        self,
        agent_id: str,
        user_id: str,
        conversation_id: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: float,
        model: str,
        success: bool = True,
        error: Optional[str] = None,
        **extra
    ):
        """记录AI交互日志"""
        logger = self.get_logger(
            event_type="ai_interaction",
            agent_id=agent_id,
            user_id=user_id,
            conversation_id=conversation_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration_ms=duration_ms,
            model=model,
            success=success,
            error=error,
            **extra
        )
        
        if success:
            logger.info("AI interaction completed")
        else:
            logger.error("AI interaction failed")
    
    def log_business_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        **data
    ):
        """记录业务事件日志"""
        logger = self.get_logger(
            event_type="business_event",
            business_event=event_type,
            user_id=user_id,
            **data
        )
        
        logger.info(f"Business event: {event_type}")

# 性能监控中间件
class PerformanceMonitoringMiddleware:
    """性能监控中间件"""
    
    def __init__(self, app: FastAPI, log_manager: LogManager):
        self.app = app
        self.log_manager = log_manager
        self.metrics_collector = MetricsCollector()
    
    async def __call__(self, request: Request, call_next):
        """处理请求并收集性能指标"""
        start_time = time.time()
        
        # 提取请求信息
        method = request.method
        path = request.url.path
        user_id = self._extract_user_id(request)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算响应时间
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录日志
            self.log_manager.log_api_request(
                method=method,
                path=path,
                user_id=user_id,
                duration_ms=duration_ms,
                status_code=response.status_code
            )
            
            # 收集指标
            self.metrics_collector.record_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            return response
            
        except Exception as e:
            # 计算错误响应时间
            duration_ms = (time.time() - start_time) * 1000
            
            # 记录错误日志
            self.log_manager.log_api_request(
                method=method,
                path=path,
                user_id=user_id,
                duration_ms=duration_ms,
                status_code=500,
                error=str(e)
            )
            
            # 收集错误指标
            self.metrics_collector.record_error(
                method=method,
                path=path,
                error_type=type(e).__name__
            )
            
            raise
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """从请求中提取用户ID"""
        # 从JWT token中提取用户ID
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # 这里应该使用JWT管理器解析token
                # 为了简化，这里返回None
                return None
            except:
                return None
        return None

# 指标收集器
class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
        self.request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'path'])
        self.ai_interactions = Counter('ai_interactions_total', 'Total AI interactions', ['agent_id', 'model', 'success'])
        self.ai_tokens = Counter('ai_tokens_total', 'Total AI tokens used', ['type', 'model'])
        self.active_connections = Gauge('websocket_connections_active', 'Active WebSocket connections')
        self.cache_operations = Counter('cache_operations_total', 'Cache operations', ['operation', 'result'])
    
    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """记录HTTP请求指标"""
        self.request_count.labels(method=method, path=path, status=str(status_code)).inc()
        self.request_duration.labels(method=method, path=path).observe(duration_ms / 1000)
    
    def record_ai_interaction(
        self, 
        agent_id: str, 
        model: str, 
        success: bool,
        input_tokens: int,
        output_tokens: int
    ):
        """记录AI交互指标"""
        self.ai_interactions.labels(
            agent_id=agent_id, 
            model=model, 
            success=str(success)
        ).inc()
        
        self.ai_tokens.labels(type='input', model=model).inc(input_tokens)
        self.ai_tokens.labels(type='output', model=model).inc(output_tokens)
    
    def record_websocket_connection(self, increment: bool = True):
        """记录WebSocket连接指标"""
        if increment:
            self.active_connections.inc()
        else:
            self.active_connections.dec()
    
    def record_cache_operation(self, operation: str, result: str):
        """记录缓存操作指标"""
        self.cache_operations.labels(operation=operation, result=result).inc()
```

---

**架构设计版本**: v1.0  
**最后更新**: 2025-01-08  
**下次审查**: 每月架构评审  

这个后端架构设计注重：
1. **可扩展性**: 微服务友好的模块化设计和清晰的层次结构
2. **清晰性**: 领域驱动设计和明确的职责分离
3. **维护性**: 完整的测试覆盖和标准化的开发模式
4. **性能**: 多级缓存、异步处理和资源优化
5. **安全性**: 全面的认证授权和数据保护机制
6. **可观测性**: 结构化日志、指标收集和性能监控

这个架构将为 Connet.AI 提供一个强大、安全、高性能的后端基础设施。
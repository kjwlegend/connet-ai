# LangGraph 多智能体后端实现方案

## 📋 项目概述

基于 LangGraph 的多智能体协作系统后端实现方案，支持 Agent 市场、Contact 实例管理、工作流编排、完整追溯和监控。本方案基于业务流程 `Agent市场 → Contact实例 → Conversation → Group Chat`，在现有 BFF 架构基础上扩展实现。

### 核心业务流程
```
用户浏览Agent市场 → 添加Agent为Contact → 创建Conversation → 邀请Contact参与 → 动态LangGraph工作流
```

### 架构重点
- **Agent定义** - 市场中的智能体模板，定义能力和配置
- **Contact实例** - 用户个人的智能体实例，支持个性化配置
- **动态工作流** - 基于Conversation参与者动态构建LangGraph
- **完整追溯** - 每个执行步骤的数据库记录和Token统计

## 🏗️ 基于现有架构的扩展规划

### 1. 现有目录结构保持 + 新增扩展

```
bff/
├── app/                                  # ✅ 现有结构保持
│   ├── main.py                           # ✅ FastAPI 主入口 (无需修改)
│   ├── __init__.py
│   │
│   ├── api/                              # ✅ 现有 API 路由层
│   │   ├── __init__.py
│   │   ├── dependencies.py               # ✅ 现有依赖注入 (扩展)
│   │   ├── middleware.py                 # ✅ 现有中间件 (扩展)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                 # ✅ 现有路由注册
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── ai_agents.py          # 🔄 现有 - 需扩展动态节点管理
│   │           ├── ai_chat.py            # 🔄 现有 - 需重构为LangGraph
│   │           ├── auth.py               # ✅ 现有认证接口
│   │           ├── contacts.py           # ✅ 现有联系人接口
│   │           ├── conversations.py      # ✅ 现有对话接口
│   │           ├── health.py             # ✅ 现有健康检查
│   │           ├── settings.py           # ✅ 现有设置接口
│   │           ├── timeline.py           # ✅ 现有时间线接口
│   │           ├── users.py              # ✅ 现有用户接口
│   │           ├── workflows.py          # 🆕 新增工作流管理接口
│   │           ├── tools.py              # 🆕 新增工具管理接口
│   │           └── analytics.py          # 🆕 新增分析统计接口
│   │
│   ├── config/                           # ✅ 现有配置管理
│   │   ├── __init__.py
│   │   └── settings.py                   # ✅ 现有配置设置
│   │
│   ├── core/                             # ✅ 现有核心层 (扩展)
│   │   ├── __init__.py
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── repositories/             # ✅ 现有仓库接口
│   │
│   ├── services/                         # ✅ 现有服务层 (扩展)
│   │   ├── __init__.py
│   │   ├── ai_agent_service.py           # 🔄 现有 - 需增强LangGraph集成
│   │   ├── ai_memory_service.py          # 🔄 现有 - 需增强Mem0集成
│   │   ├── auth_service.py               # ✅ 现有认证服务
│   │   ├── base.py                       # ✅ 现有基础服务类
│   │   ├── contact_service.py            # ✅ 现有联系人服务
│   │   ├── conversation_service.py       # ✅ 现有对话服务
│   │   ├── knowledge_service.py          # ✅ 现有知识服务
│   │   ├── rag_service.py                # 🔄 现有 - 需集成到工作流
│   │   ├── supabase_auth_service.py      # ✅ 现有Supabase认证
│   │   ├── tools_service.py              # 🔄 现有 - 需扩展工具执行
│   │   ├── user_service.py               # ✅ 现有用户服务
│   │   │
│   │   ├── langgraph/                    # 🆕 新增LangGraph服务
│   │   │   ├── __init__.py
│   │   │   ├── workflow_engine.py        # 工作流引擎
│   │   │   ├── node_registry.py          # 节点注册中心
│   │   │   ├── state_manager.py          # 状态管理器
│   │   │   ├── execution_tracker.py      # 执行追踪器
│   │   │   └── mention_router.py         # @mention路由器
│   │   │
│   │   ├── tools/                        # 🆕 新增工具执行系统
│   │   │   ├── __init__.py
│   │   │   ├── tool_executor.py          # 工具执行器
│   │   │   ├── tool_registry.py          # 工具注册中心
│   │   │   └── builtin_tools/            # 内置工具
│   │   │
│   │   └── monitoring/                   # 🆕 新增监控服务
│   │       ├── __init__.py
│   │       ├── execution_tracer.py       # 执行追踪器
│   │       ├── metrics_collector.py      # 指标收集器
│   │       ├── token_counter.py          # Token统计器
│   │       └── performance_monitor.py    # 性能监控器
│   │
│   ├── schemas/                          # ✅ 现有API模式 (扩展)
│   │   ├── __init__.py
│   │   ├── ai.py                         # 🔄 现有AI相关模式 - 需扩展
│   │   ├── auth.py                       # ✅ 现有认证模式
│   │   ├── base.py                       # ✅ 现有基础模式
│   │   ├── contact.py                    # ✅ 现有联系人模式
│   │   ├── conversation.py               # ✅ 现有对话模式
│   │   ├── knowledge.py                  # ✅ 现有知识模式
│   │   ├── responses.py                  # ✅ 现有响应模式
│   │   ├── tools.py                      # 🔄 现有工具模式 - 需扩展
│   │   ├── user.py                       # ✅ 现有用户模式
│   │   │
│   │   ├── workflows.py                  # 🆕 新增工作流相关模式
│   │   ├── analytics.py                  # 🆕 新增分析统计模式
│   │   └── langgraph.py                  # 🆕 新增LangGraph状态模式
│   │
│   ├── infrastructure/                   # ✅ 现有基础设施层 (扩展)
│   │   ├── __init__.py
│   │   │
│   │   ├── cache/                        # ✅ 现有缓存系统
│   │   │   ├── cache_decorators.py       # ✅ 现有缓存装饰器
│   │   │   └── cache_keys.py             # ✅ 现有缓存键管理
│   │   │
│   │   ├── database/                     # ✅ 现有数据库层 (扩展)
│   │   │   ├── __init__.py
│   │   │   ├── connection.py             # ✅ 现有数据库连接
│   │   │   │
│   │   │   ├── models/                   # ✅ 现有数据库模型 (扩展)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent_model.py        # 🔄 现有智能体模型 - 需扩展LangGraph字段
│   │   │   │   ├── contact_model.py      # ✅ 现有联系人模型
│   │   │   │   ├── conversation_model.py # ✅ 现有对话模型
│   │   │   │   ├── file_model.py         # ✅ 现有文件模型
│   │   │   │   ├── knowledge_model.py    # ✅ 现有知识模型
│   │   │   │   ├── message_model.py      # ✅ 现有消息模型
│   │   │   │   ├── tool_model.py         # 🔄 现有工具模型 - 需扩展
│   │   │   │   ├── user_model.py         # ✅ 现有用户模型
│   │   │   │   │
│   │   │   │   ├── workflow_execution_model.py  # 🆕 新增工作流执行模型
│   │   │   │   ├── node_execution_model.py      # 🆕 新增节点执行模型
│   │   │   │   ├── tool_execution_model.py      # 🆕 新增工具执行模型
│   │   │   │   └── token_usage_model.py         # 🆕 新增Token使用模型
│   │   │   │
│   │   │   └── repositories/             # ✅ 现有仓库层 (扩展)
│   │   │       ├── __init__.py
│   │   │       ├── agent_repository_impl.py     # 🔄 现有 - 需扩展节点管理
│   │   │       ├── ai_memory_repository_impl.py # 🔄 现有 - 需优化
│   │   │       ├── base_repository.py    # ✅ 现有基础仓库
│   │   │       ├── contacts_repository_impl.py  # ✅ 现有
│   │   │       ├── conversation_repository_impl.py # ✅ 现有
│   │   │       ├── knowledge_repository_impl.py # ✅ 现有
│   │   │       ├── message_repository_impl.py   # ✅ 现有
│   │   │       ├── tools_repository_impl.py     # 🔄 现有 - 需扩展
│   │   │       ├── user_repository_impl.py      # ✅ 现有
│   │   │       │
│   │   │       ├── workflow_execution_repository.py # 🆕 新增
│   │   │       ├── node_execution_repository.py     # 🆕 新增
│   │   │       └── token_usage_repository.py        # 🆕 新增
│   │   │
│   │   ├── external/                     # ✅ 现有外部服务集成 (扩展)
│   │   │   ├── __init__.py
│   │   │   └── supabase/                 # ✅ 现有Supabase集成
│   │   │       ├── __init__.py
│   │   │       ├── auth.py               # ✅ 现有认证集成
│   │   │       ├── client.py             # ✅ 现有客户端
│   │   │       ├── realtime.py           # ✅ 现有实时通信
│   │   │       └── storage.py            # ✅ 现有存储
│   │   │
│   │   ├── messaging/                    # ✅ 现有消息系统 (可扩展)
│   │   │   ├── __init__.py
│   │   │   └── event_bus.py              # ✅ 现有事件总线
│   │   │
│   │   └── security/                     # ✅ 现有安全系统 (无需修改)
│   │       ├── __init__.py
│   │       ├── auth.py                   # ✅ 现有认证
│   │       └── permissions.py            # ✅ 现有权限管理
│   │
│   ├── utils/                            # ✅ 现有工具函数 (扩展)
│   │   ├── __init__.py
│   │   ├── constants.py                  # ✅ 现有常量
│   │   ├── datetime.py                   # ✅ 现有日期工具
│   │   ├── helpers.py                    # ✅ 现有辅助函数
│   │   ├── logging.py                    # ✅ 现有日志工具
│   │   │
│   │   ├── validation.py                 # 🆕 新增验证工具
│   │   ├── serialization.py              # 🆕 新增序列化工具
│   │   ├── token_counter.py              # 🆕 新增Token计数器
│   │   └── langgraph_helpers.py          # 🆕 新增LangGraph辅助工具
│   │
│   └── agents/                           # 🆕 新增智能体实现目录
│       ├── __init__.py
│       ├── base_agent.py                 # 基础智能体类
│       ├── builtin/                      # 内置智能体
│       │   ├── __init__.py
│       │   ├── coder_agent.py            # 代码助手
│       │   ├── analyst_agent.py          # 数据分析师
│       │   ├── writer_agent.py           # 写作助手
│       │   └── researcher_agent.py       # 研究员
│       └── registry.py                   # 智能体注册器
│
├── alembic/                              # 数据库迁移
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
│
├── tests/                                # 测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   ├── test_models/
│   └── test_agents/
│
├── scripts/                              # 脚本
│   ├── __init__.py
│   ├── init_db.py                        # 数据库初始化
│   ├── seed_agents.py                    # 智能体数据种子
│   └── migrate_data.py                   # 数据迁移
│
├── config/                               # 配置文件
│   ├── __init__.py
│   ├── settings.py                       # 配置设置
│   ├── agents_config.yaml                # 智能体配置
│   ├── tools_config.yaml                 # 工具配置
│   └── workflows_config.yaml             # 工作流配置
│
├── requirements.txt                      # 依赖管理
├── pyproject.toml                        # 项目配置
├── Dockerfile                            # Docker 配置
├── docker-compose.yml                    # Docker Compose
└── README.md                             # 项目说明
```

## 📊 数据库架构设计

### 1. 核心表结构

```sql
-- 对话表
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),
    user_id UUID NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 工作流定义表
CREATE TABLE workflow_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50) DEFAULT '1.0.0',
    graph_config JSONB NOT NULL,  -- LangGraph 配置
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 工作流执行记录表
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    workflow_definition_id UUID REFERENCES workflow_definitions(id),
    status VARCHAR(50) DEFAULT 'running',
    input_data JSONB,
    output_data JSONB,
    execution_path JSONB,  -- 执行路径追踪
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB
);

-- 现有 agents 表作为智能体定义 (已存在，需扩展)
-- 参考: bff/app/infrastructure/database/models/agent_model.py
-- 新增字段通过 Alembic 迁移添加:
--   node_type VARCHAR(50) DEFAULT 'agent'
--   execution_config JSONB DEFAULT '{}'
--   resource_limits JSONB DEFAULT '{}'

-- Contact 表 (用户的智能体实例)
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    agent_id UUID REFERENCES agents(id) NOT NULL,
    
    -- 个性化配置
    custom_name VARCHAR(255),
    custom_avatar_url VARCHAR(500),
    custom_system_prompt TEXT,
    custom_personality JSONB DEFAULT '{}',
    custom_tools JSONB DEFAULT '[]',
    
    -- Contact实例配置
    is_favorite BOOLEAN DEFAULT false,
    conversation_style VARCHAR(100),
    memory_retention_days INTEGER DEFAULT 30,
    
    -- LangGraph实例配置
    instance_config JSONB DEFAULT '{}',
    resource_limits JSONB DEFAULT '{}',
    permissions JSONB DEFAULT '[]',
    
    status VARCHAR(50) DEFAULT 'active',
    added_at TIMESTAMP DEFAULT NOW(),
    last_interaction_at TIMESTAMP,
    
    UNIQUE(user_id, agent_id)
);

-- 节点执行记录表
CREATE TABLE node_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES workflow_executions(id),
    node_id VARCHAR(100) NOT NULL,  -- 节点标识
    node_type VARCHAR(50) NOT NULL,  -- 节点类型
    agent_id VARCHAR(100),  -- 关联智能体
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    token_usage JSONB,  -- Token 使用统计
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- 工具定义表
CREATE TABLE tool_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    schema JSONB,  -- 工具参数架构
    endpoint VARCHAR(500),  -- API 端点
    auth_config JSONB,  -- 认证配置
    rate_limit JSONB,  -- 限流配置
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 工具调用记录表
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_execution_id UUID REFERENCES node_executions(id),
    tool_id VARCHAR(100) REFERENCES tool_definitions(tool_id),
    function_name VARCHAR(100),
    input_parameters JSONB,
    output_result JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- 记忆引用表
CREATE TABLE memory_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_execution_id UUID REFERENCES node_executions(id),
    memory_type VARCHAR(50),  -- 'individual', 'shared', 'conversation'
    memory_id VARCHAR(255),  -- Mem0 记忆 ID
    relevance_score FLOAT,
    used_in_context BOOLEAN DEFAULT false,
    retrieved_at TIMESTAMP DEFAULT NOW()
);

-- Token 使用统计表
CREATE TABLE token_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES workflow_executions(id),
    node_execution_id UUID REFERENCES node_executions(id),
    model_name VARCHAR(100),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6),  -- 成本（美元）
    recorded_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- 系统指标表
CREATE TABLE system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(100),  -- 'workflow_duration', 'node_duration', 'memory_usage'
    metric_name VARCHAR(100),
    value NUMERIC,
    unit VARCHAR(50),
    tags JSONB,  -- 标签和维度
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- 执行日志表
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES workflow_executions(id),
    node_execution_id UUID REFERENCES node_executions(id),
    level VARCHAR(20),  -- 'INFO', 'WARNING', 'ERROR', 'DEBUG'
    message TEXT,
    context JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### 2. 索引优化

```sql
-- 性能优化索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_workflow_executions_conversation_id ON workflow_executions(conversation_id);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);
CREATE INDEX idx_node_executions_workflow_id ON node_executions(workflow_execution_id);
CREATE INDEX idx_node_executions_agent_id ON node_executions(agent_id);
CREATE INDEX idx_tool_executions_node_id ON tool_executions(node_execution_id);
CREATE INDEX idx_memory_references_node_id ON memory_references(node_execution_id);
CREATE INDEX idx_token_usage_workflow_id ON token_usage_logs(workflow_execution_id);
CREATE INDEX idx_execution_logs_workflow_id ON execution_logs(workflow_execution_id);

-- 时间范围查询优化
CREATE INDEX idx_node_executions_started_at ON node_executions(started_at);
CREATE INDEX idx_tool_executions_started_at ON tool_executions(started_at);
CREATE INDEX idx_token_usage_recorded_at ON token_usage_logs(recorded_at);
```

## 🏛️ 架构分层设计

### 1. API 路由层 (API Routes Layer)

**职责**: 处理 HTTP 请求，参数验证，响应格式化

**主要文件**:
- `api/v1/chat.py` - 聊天接口
- `api/v1/agents.py` - 智能体管理
- `api/v1/workflows.py` - 工作流管理
- `api/websocket/workflow_updates.py` - WebSocket 实时更新

### 2. 服务层 (Service Layer)

**职责**: 业务逻辑处理，服务编排

**主要组件**:
- **LangGraph 服务**: 工作流执行引擎
- **智能体服务**: 智能体生命周期管理
- **记忆服务**: 多层记忆管理
- **工具服务**: 工具调用和管理
- **监控服务**: 日志、指标、追踪

### 3. 模型层 (Model Layer)

**职责**: 数据建模，状态定义

**主要组件**:
- **数据库模型**: SQLModel 数据库实体
- **API 模式**: Pydantic 请求/响应模型
- **LangGraph 状态**: 工作流状态定义

### 4. 数据访问层 (Repository Layer)

**职责**: 数据库操作封装，查询优化

**设计原则**:
- 每个实体一个仓库类
- 支持事务管理
- 查询性能优化

### 5. 基础设施层 (Infrastructure Layer)

**职责**: 外部服务集成，配置管理

**主要组件**:
- **数据库连接**: PostgreSQL 连接管理
- **缓存服务**: Redis 缓存
- **外部 API**: LLM、Mem0、工具服务

## ✅ 基于业务流程的AI实现TODO Checklist

**重要澄清**: 基于业务流程 `Agent市场 → Contact → Conversation → Group Chat`，实施计划重新调整为以对话参与者为核心的架构。

### 阶段 1: 数据模型重构和基础设施 (Week 1-2)

#### 1.1 核心数据模型扩展 (依赖: 无)
- [ ] 扩展现有 `agents` 表，添加 LangGraph 节点配置字段
  - 添加 `node_type`, `execution_config`, `resource_limits` 字段
  - 保持现有字段不变，确保向后兼容
- [ ] 扩展现有 `contacts` 表，添加实例个性化配置
  - 添加 `custom_system_prompt`, `instance_config`, `permissions` 字段
  - 支持用户对 Agent 的个性化定制
- [ ] 扩展现有 `conversation_participants` 表，添加工作流配置
  - 添加 `workflow_priority`, `conversation_permissions` 字段
  - 支持参与者在工作流中的角色和权限
- [ ] 创建 `workflow_executions` 表 - 工作流执行记录
- [ ] 创建 `node_executions` 表 - 节点执行记录，关联到 `contact_id`
- [ ] 创建 `tool_executions` 表 - 工具调用记录
- [ ] 创建 `conversation_memories` 表 - 分层记忆管理 (个人/共享)

#### 1.2 数据库迁移和索引优化 (依赖: 1.1)
- [ ] 创建 Alembic 迁移脚本，保持现有数据完整性
- [ ] 添加性能优化索引 (contact查询、participant查询、工作流追踪)
- [ ] 创建测试数据种子脚本 (Agent市场数据、示例Contacts)
- [ ] 验证数据模型关系和约束

#### 1.3 依赖管理和环境配置 (依赖: 现有配置系统)
- [ ] 添加 LangGraph 相关依赖 (`pyproject.toml`)
- [ ] 配置 Mem0 集成依赖
- [ ] 添加环境变量配置 (LANGGRAPH_ENABLED, MEM0_API_KEY)
- [ ] 设置特性开关系统
- [ ] 配置开发和测试环境

### 阶段 2: Contact实例管理和核心服务 (Week 2-4)

#### 2.1 Contact实例管理系统 (依赖: 1.2)
- [ ] 扩展现有 `ContactRepository` 支持 Agent 实例配置
  - 支持根据 `agent_id` 创建个性化 Contact 实例
  - 实现 Contact 配置的 CRUD 操作
- [ ] 实现 `ContactInstanceManager` - Contact实例生命周期管理
  - Agent 市场浏览 → 添加为 Contact 的业务流程
  - Contact 个性化配置和权限管理
  - Contact 与 Agent 定义的关系维护
- [ ] 实现 Agent 添加到 Contact 的业务逻辑
  - 验证 Agent 定义存在性和用户权限
  - 防止重复添加同一 Agent
  - 支持 Agent 版本升级通知
- [ ] 实现 Contact 个性化配置管理
  - 自定义系统提示词 (覆盖 Agent 默认提示)
  - 自定义工具配置和权限
  - 自定义模型偏好和资源限制
- [ ] 支持 Contact 在对话中的角色和优先级管理

#### 2.2 ConversationParticipant增强 (依赖: 2.1)
- [ ] 扩展现有 `ConversationParticipantRepository`
- [ ] 实现参与者动态添加/移除逻辑
- [ ] 实现参与者工作流优先级管理
- [ ] 支持参与者权限和角色配置
- [ ] 实现参与者状态追踪 (活跃/非活跃)

#### 2.3 扩展API模式定义 (依赖: 现有schemas)
- [ ] 扩展现有 `schemas/ai.py` 支持 LangGraph 配置
- [ ] 创建 `schemas/workflows.py` - 工作流相关模式
- [ ] 创建 `schemas/langgraph.py` - LangGraph 状态模式
- [ ] 扩展 `schemas/contact.py` 支持实例配置
- [ ] 创建 `schemas/analytics.py` - 分析统计模式

#### 2.4 新增仓库层实现 (依赖: 1.1)
- [ ] 实现 `WorkflowExecutionRepository`
- [ ] 实现 `NodeExecutionRepository`  
- [ ] 实现 `ToolExecutionRepository`
- [ ] 实现 `ConversationMemoryRepository`
- [ ] 扩展现有仓库类支持新字段和关系

### 阶段 3: LangGraph 工作流引擎和动态构建 (Week 3-5)

#### 3.1 动态工作流构建器 (依赖: 2.4)
- [ ] 实现 `DynamicWorkflowBuilder` - 基于 Contact 参与者构建工作流
  - 输入: `conversation_id` + 活跃的 Contact 参与者列表
  - 输出: 可执行的 LangGraph 工作流
  - 支持参与者变更时的工作流重构
- [ ] 支持多种工作流类型
  - `single_agent`: 1v1 对话 (单个 Contact)
  - `mention_routing`: @mention 路由到特定 Contact
  - `parallel_discussion`: 多个 Contact 并行响应
  - `sequential_processing`: 按优先级顺序处理
  - `consensus_building`: 多 Contact 共识构建
- [ ] 实现工作流类型智能识别
  - 基于消息内容分析 (@mention 检测)
  - 基于参与者数量和配置
  - 基于历史协作模式
- [ ] 支持工作流运行时重构
  - Contact 加入/离开时动态调整
  - 权限变更时重新验证
  - 工作流执行异常时的降级策略
- [ ] 实现工作流配置持久化和版本管理

#### 3.2 LangGraph 节点系统 (依赖: 3.1)  
- [ ] 实现 `ContactAgentNode` - 基于 Contact 实例的智能体节点
  - 使用 Contact 的个性化配置 (custom_system_prompt, instance_config)
  - 集成 Contact 的工具权限和资源限制
  - 支持 Contact 级别的记忆检索和存储
  - 追踪节点执行到具体的 Contact 实例
- [ ] 实现路由节点
  - `MentionRouter`: 解析 @mention 并路由到对应 Contact
  - `DiscussionCoordinator`: 协调多 Contact 并行讨论
  - `PriorityRouter`: 基于 Contact 优先级的路由决策
- [ ] 实现聚合节点
  - `ResponseAggregator`: 聚合多个 Contact 的响应
  - `ConsensusBuilder`: 构建多 Contact 共识
  - `ConflictResolver`: 解决 Contact 间的冲突观点
- [ ] 实现决策节点
  - `WorkflowController`: 控制工作流执行流程
  - `ParticipantManager`: 动态管理参与者状态
- [ ] 节点执行状态追踪和错误处理
  - 记录每个节点的 Contact 执行者
  - 支持节点级别的重试和降级
  - 集成到现有的错误处理框架

#### 3.3 对话记忆系统增强 (依赖: 现有ai_memory_service)
- [ ] 重构现有 `AIMemoryService` 集成 Mem0
- [ ] 实现 `ConversationMemoryManager` - 基于参与者的记忆管理
- [ ] 支持个人记忆 (Contact级别) 和共享记忆 (Conversation级别)
- [ ] 实现记忆检索优化 (基于参与者角色和上下文)
- [ ] 集成记忆到 LangGraph 状态管理

#### 3.4 工具调用系统 (依赖: 现有tools_service)
- [ ] 扩展现有 `ToolsService` 支持 LangGraph 集成
- [ ] 实现基于Contact配置的工具权限管理
- [ ] 实现工具调用追踪和记录
- [ ] 支持工具调用的并发控制和限流
- [ ] 集成工具执行到工作流节点

### 阶段 4: 对话流程和API接口集成 (Week 4-6)

#### 4.1 现有服务增强 (依赖: 3.3)
- [ ] 增强现有 `AIAgentService` 支持 Agent 市场功能
  - Agent 浏览、搜索、分类和推荐
  - Agent 添加到用户 Contact 列表
  - Agent 版本管理和更新通知
  - Agent 使用统计和评分系统
- [ ] 增强现有 `ConversationService` 支持动态工作流
  - 基于 Contact 参与者构建工作流
  - 支持 1v1 → Group Chat 的无缝转换
  - 参与者动态加入/离开时的工作流重构
  - 集成 LangGraph 执行状态到对话状态
- [ ] 实现 Contact 生命周期管理
  - Contact 创建 (从 Agent 市场添加)
  - Contact 个性化配置和权限设置
  - Contact 使用统计和交互历史
  - Contact 归档和删除
- [ ] 实现对话参与者管理
  - Contact 邀请到对话的业务逻辑
  - 参与者权限和角色管理
  - 参与者状态追踪 (在线/离线)
  - 参与者工作流优先级调整
- [ ] 集成 LangGraph 工作流到对话处理
  - 工作流执行结果转换为对话消息
  - 工作流异常处理和用户友好提示
  - 工作流执行状态的实时推送

#### 4.2 聊天接口重构 (依赖: 4.1)
- [ ] 重构现有 `ai_chat.py` 支持 Contact 参与者对话
  - 移除现有 mock 逻辑，集成真实 LangGraph 处理
  - 支持基于 Contact 实例的智能体调用
  - 实现 @mention 解析和 Contact 路由
  - 集成 Contact 个性化配置到 LLM 调用
- [ ] 实现基于 Contact 参与者的动态路由
  - 根据 @mention 内容确定目标 Contact
  - 支持多 Contact 并行或串行处理
  - 实现 Contact 能力匹配和任务分配
- [ ] 支持 1v1 到 Group Chat 的无缝转换
  - 单个 Contact 对话 → 多 Contact 协作
  - 动态添加/移除 Contact 参与者
  - 保持对话历史和上下文连续性
- [ ] 实现实时 Contact 参与者状态同步
  - Contact 在线/离线状态
  - Contact 工作流执行状态
  - Contact 资源使用和限流状态
- [ ] 流式响应和实时状态更新
  - Contact 执行进度实时推送
  - 支持工作流中断和恢复
  - 错误处理和用户友好提示

#### 4.3 智能体市场接口 (依赖: 现有ai_agents.py)
- [ ] 扩展现有 `ai_agents.py` 支持完整的 Agent 市场功能
  - Agent 浏览界面 (分页、筛选、搜索)
  - Agent 详情页面 (能力、工具、示例对话)
  - Agent 分类和标签系统
  - Agent 推荐算法 (基于用户偏好和使用历史)
- [ ] 实现 Agent 添加到 Contact 的完整流程
  - 验证用户权限和 Agent 可用性
  - 创建 Contact 实例并支持初始配置
  - 处理重复添加和版本升级场景
  - 集成到现有的 Contact 管理系统
- [ ] 实现 Agent 评分和评论系统
  - Agent 使用评分 (1-5星)
  - 用户评论和反馈收集
  - Agent 质量指标统计
  - 恶意评论检测和过滤
- [ ] 支持 Agent 版本管理和生命周期
  - Agent 版本发布和变更日志
  - 现有 Contact 的版本升级通知
  - 向后兼容性检查
  - 废弃 Agent 的迁移建议

#### 4.4 Contact 管理接口 (依赖: 现有contacts.py)
- [ ] 扩展现有 `contacts.py` 支持 Agent Contact 全生命周期管理
  - Contact 列表展示 (基于 Agent 的个性化实例)
  - Contact 详情页面 (配置、统计、历史)
  - Contact 状态管理 (活跃、暂停、归档)
  - Contact 与底层 Agent 定义的关系维护
- [ ] 实现 Contact 个性化配置接口
  - 自定义系统提示词编辑器
  - 个性化工具权限配置
  - 模型偏好和参数调整
  - 对话风格和行为设置
- [ ] 实现 Contact 使用分析和统计
  - Contact 对话历史和交互记录
  - Contact 使用频率和效果统计
  - Contact Token 消耗和成本分析
  - Contact 协作效果评估报告
- [ ] 支持 Contact 组织和管理功能
  - Contact 自定义分组 (工作、学习、娱乐等)
  - Contact 收藏和快速访问
  - Contact 搜索和筛选
  - Contact 导入导出和备份
- [ ] 实现 Contact 权限和隐私管理
  - Contact 访问权限控制
  - Contact 数据隐私设置
  - Contact 共享和协作权限
  - Contact 使用日志和审计

### 阶段 5: 监控、追踪和分析系统 (Week 5-7)

#### 5.1 执行追踪系统 (依赖: 3.2)
- [ ] 实现 `WorkflowExecutionTracker` - 完整工作流执行追踪
  - 记录工作流触发原因 (用户消息、@mention、参与者变更)
  - 追踪工作流类型和参与的 Contact 列表
  - 记录工作流执行路径和决策点
  - 统计工作流整体性能指标
- [ ] 实现 `NodeExecutionTracker` - 基于 Contact 的节点执行记录
  - 记录每个节点执行的 Contact 实例信息
  - 追踪 Contact 个性化配置对执行的影响
  - 记录 Contact 级别的资源使用和限制
  - 分析 Contact 协作效果和贡献度
- [ ] 实现 `ToolExecutionTracker` - Contact 工具调用追踪
  - 记录 Contact 调用的具体工具和权限
  - 追踪工具执行结果和错误信息
  - 分析 Contact 工具使用模式
  - 监控工具调用的安全性和合规性
- [ ] 支持执行路径可视化和分析
  - Contact 协作流程图和时间线
  - Contact 贡献度和交互关系图
  - 工作流瓶颈和优化建议
  - 用户友好的执行报告生成
- [ ] 实现错误追踪和调试信息收集
  - Contact 执行错误的根因分析
  - 工作流失败的自动恢复策略
  - 详细的调试日志和上下文信息
  - 错误趋势分析和预防建议

#### 5.2 Token 使用统计 (依赖: 5.1)
- [ ] 实现 `TokenUsageCollector` - 基于 Contact 的精确 Token 计费
  - 按 Contact 实例统计 Token 使用
  - 区分 Contact 个性化配置对 Token 消耗的影响
  - 记录不同模型和配置的 Token 成本
  - 支持实时 Token 使用监控和告警
- [ ] 支持多维度的使用统计分析
  - Contact 维度: 每个 Contact 的使用量和成本
  - Conversation 维度: 对话级别的 Token 消耗分析
  - User 维度: 用户总体使用量和成本统计
  - Agent 维度: 不同 Agent 定义的效率对比
- [ ] 实现成本分析和预算控制
  - Contact 级别的成本限制和预算管理
  - 用户级别的月度/年度预算控制
  - 成本超标时的自动限流和通知
  - 成本优化建议和模型推荐
- [ ] 支持不同模型和配置的计费管理
  - 多种 LLM 提供商的统一计费
  - Contact 个性化模型选择的成本差异
  - 动态定价和折扣策略支持
  - 成本透明度和详细账单
- [ ] 实现使用趋势分析和智能预测
  - Contact 使用模式和趋势分析
  - 基于历史数据的成本预测
  - 异常使用检测和风险预警
  - 使用效率优化建议

#### 5.3 性能监控系统 (依赖: 5.1, 5.2)
- [ ] 实现 `PerformanceMonitor` - 系统性能监控
- [ ] 监控工作流执行时间和资源消耗
- [ ] 实现性能基线和异常检测
- [ ] 集成系统资源监控 (CPU、内存、网络)
- [ ] 实现智能告警和自动恢复

#### 5.4 分析报告系统 (依赖: 5.2, 5.3)
- [ ] 实现用户使用行为分析
- [ ] 实现 Contact 交互效果分析
- [ ] 实现多智能体协作效果评估
- [ ] 生成个性化使用报告
- [ ] 实现 A/B 测试框架支持

### 阶段 6: 高级功能和优化 (Week 6-8)

#### 6.1 高级协作模式 (依赖: 3.2)
- [ ] 实现基于 Contact 的辩论模式
  - 多个 Contact 观点对抗和论证
  - Contact 角色分配 (正方、反方、中立)
  - 辩论轮次控制和时间管理
  - 论证质量评估和获胜判定
- [ ] 实现基于 Contact 的头脑风暴模式
  - 多个 Contact 并行创意生成
  - Contact 创意评估和筛选
  - 创意合并和优化协作
  - 最终方案的投票和确定
- [ ] 实现基于 Contact 的专家会诊模式
  - 根据问题类型自动匹配专家 Contact
  - Contact 专业领域和能力匹配
  - 分层会诊和意见整合
  - 综合诊断结果和建议输出
- [ ] 实现基于 Contact 的共识构建模式
  - Contact 间观点差异识别和分析
  - 冲突解决和妥协方案生成
  - Contact 投票和共识达成机制
  - 决策过程透明化和可追溯
- [ ] 支持用户自定义协作流程配置
  - Contact 协作模板创建和保存
  - 协作流程的参数化配置
  - Contact 角色和权限的灵活分配
  - 协作效果评估和模板优化

#### 6.2 智能路由和决策 (依赖: 6.1)
- [ ] 实现基于上下文的智能 Contact 推荐
  - 根据对话内容自动推荐相关 Contact
  - 基于 Contact 历史表现的推荐权重
  - Contact 能力与任务需求的匹配算法
  - 用户偏好和使用习惯的学习适应
- [ ] 实现动态工作流优化
  - 基于 Contact 协作历史的流程优化
  - Contact 组合效果的学习和改进
  - 工作流路径的智能调整
  - A/B 测试支持不同协作策略
- [ ] 实现 Contact 负载均衡和资源调度
  - Contact 工作负载监控和分配
  - 资源使用的智能调度和优化
  - Contact 并发执行的协调管理
  - 系统资源的动态分配和回收
- [ ] 支持 Contact 能力匹配和任务智能分配
  - Contact 专业能力和工具的精确匹配
  - 任务复杂度与 Contact 能力的评估
  - 多 Contact 协作的最优组合推荐
  - 任务分解和 Contact 责任分配
- [ ] 实现协作效果学习和持续改进
  - Contact 协作模式的效果量化评估
  - 用户满意度和结果质量的反馈学习
  - 协作策略的持续优化和演进
  - 最佳实践的抽取和模板化

#### 6.3 新增API接口 (依赖: 5.4)
- [ ] 创建 `api/v1/endpoints/workflows.py` - 工作流管理接口
- [ ] 创建 `api/v1/endpoints/analytics.py` - 分析统计接口
- [ ] 扩展现有 WebSocket 支持实时协作状态
- [ ] 实现工作流可视化数据接口
- [ ] 支持工作流模板和配置导入导出

#### 6.4 系统优化和扩展 (依赖: 6.2)
- [ ] 实现动态负载均衡和自动扩展
- [ ] 优化数据库查询和缓存策略
- [ ] 实现分布式工作流执行支持
- [ ] 支持工作流检查点和断点续传
- [ ] 实现系统容灾和故障恢复

### 阶段 7: 测试和文档 (Week 7-8)

#### 7.1 单元测试 (依赖: 6.3)
- [ ] 编写模型层测试 (`tests/test_models/`)
- [ ] 编写仓库层测试 (`tests/test_repositories/`)
- [ ] 编写服务层测试 (`tests/test_services/`)
- [ ] 编写API接口测试 (`tests/test_api/`)
- [ ] 编写智能体测试 (`tests/test_agents/`)

#### 7.2 集成测试 (依赖: 7.1)
- [ ] 编写工作流集成测试
- [ ] 编写端到端聊天测试
- [ ] 编写多智能体协作测试
- [ ] 编写性能压力测试
- [ ] 编写错误恢复测试

#### 7.3 文档和部署 (依赖: 7.2)
- [ ] 编写API文档 (OpenAPI/Swagger)
- [ ] 编写开发者指南
- [ ] 编写部署文档
- [ ] 编写监控和运维文档
- [ ] 配置CI/CD流水线

### 阶段 8: 性能优化和监控 (Week 8+)

#### 8.1 性能优化 (依赖: 7.3)
- [ ] 数据库查询优化
- [ ] 缓存策略实现
- [ ] 并发性能优化
- [ ] 内存使用优化
- [ ] 网络通信优化

#### 8.2 监控和告警 (依赖: 8.1)
- [ ] 配置Prometheus指标收集
- [ ] 配置Grafana仪表板
- [ ] 配置告警规则
- [ ] 实现健康检查监控
- [ ] 实现性能基线监控

## 🔧 关键技术实现要点

### 1. 基于 Contact 的动态工作流系统

```python
# 示例：基于 Contact 参与者的动态工作流构建
class ContactWorkflowBuilder:
    """Contact 工作流构建器 - 基于参与者动态构建工作流"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.contact_manager = ContactInstanceManager(db_session)
    
    async def build_workflow_for_conversation(
        self, 
        conversation_id: UUID,
        trigger_message: str
    ) -> LangGraphWorkflow:
        """为对话构建基于 Contact 的工作流"""
        
        # 1. 获取对话中的活跃 Contact 参与者
        active_contacts = await self.contact_manager.get_conversation_participants(
            conversation_id
        )
        
        # 2. 分析消息确定工作流类型
        workflow_type = await self._analyze_workflow_type(
            trigger_message, active_contacts
        )
        
        # 3. 根据 Contact 参与者构建工作流
        if workflow_type == WorkflowType.MENTION_ROUTING:
            return await self._build_mention_routing_workflow(
                trigger_message, active_contacts
            )
        elif workflow_type == WorkflowType.PARALLEL_DISCUSSION:
            return await self._build_parallel_discussion_workflow(active_contacts)
        # ... 其他工作流类型
    
    async def _build_mention_routing_workflow(
        self, 
        message: str, 
        contacts: List[ContactInstance]
    ) -> LangGraphWorkflow:
        """构建基于 Contact 的 @mention 路由工作流"""
        
        from langgraph import StateGraph
        from .states import ConversationState
        
        workflow = StateGraph(ConversationState)
        
        # 解析 @mention 并匹配到具体的 Contact
        mentioned_contacts = await self._extract_mentioned_contacts(message, contacts)
        
        # 为每个被提及的 Contact 创建智能体节点
        for contact in mentioned_contacts:
            workflow.add_node(
                f"contact_{contact.id}",
                self._create_contact_agent_node(contact)
            )
        
        # 添加响应聚合节点
        workflow.add_node("response_aggregator", self._create_response_aggregator())
        
        # 定义路由逻辑
        workflow.add_conditional_edges(
            "mention_router",
            self._route_to_mentioned_contacts,
            {f"contact_{c.id}": f"contact_{c.id}" for c in mentioned_contacts}
        )
        
        return workflow.compile()
    
    def _create_contact_agent_node(self, contact: ContactInstance):
        """创建基于 Contact 实例的智能体节点"""
        
        async def contact_processor(state: ConversationState) -> ConversationState:
            # 使用 Contact 的个性化配置
            system_prompt = contact.custom_system_prompt or contact.agent_system_prompt
            model_config = contact.instance_config.get(
                "model_preferences", 
                contact.agent_model_preferences
            )
            
            # 获取 Contact 级别的记忆上下文
            memory_context = await self._get_contact_memory_context(
                contact.id, 
                state.conversation_id,
                state.messages[-1]["content"]
            )
            
            # 调用 LLM
            response = await self._call_llm_with_contact_config(
                system_prompt,
                memory_context,
                state.messages,
                model_config,
                contact.permissions
            )
            
            # 记录 Contact 执行结果
            state.contact_responses[str(contact.id)] = {
                "contact_name": contact.custom_name or contact.agent_display_name,
                "response": response,
                "contact_id": contact.id,
                "agent_id": contact.agent_id,
                "timestamp": datetime.utcnow()
            }
            
            # 记录 Contact 节点执行到数据库
            await self._record_contact_node_execution(
                state.workflow_execution_id,
                contact.id,
                state.messages,
                response
            )
            
            return state
        
        return contact_processor
```

### 2. 基于 Contact 权限的工具调用框架

```python
# 示例：基于 Contact 的工具调用架构设计
class ContactToolExecutor:
    """Contact 工具执行器 - 基于 Contact 权限的工具调用"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.tool_registry = ToolRegistry()
        self.permission_checker = ContactPermissionChecker()
    
    async def execute_tool_for_contact(
        self, 
        contact_id: UUID,
        tool_id: str,
        function_name: str,
        parameters: Dict[str, Any],
        execution_context: ExecutionContext
    ) -> ToolResult:
        """为特定 Contact 执行工具调用"""
        
        # 1. 获取 Contact 实例和权限
        contact = await self.get_contact_instance(contact_id)
        if not contact:
            raise ContactNotFoundError(f"Contact {contact_id} not found")
        
        # 2. 检查 Contact 工具权限
        has_permission = await self.permission_checker.check_tool_permission(
            contact, tool_id, function_name
        )
        if not has_permission:
            raise PermissionDeniedError(
                f"Contact {contact.custom_name} does not have permission to use {tool_id}"
            )
        
        # 3. 记录工具执行开始
        execution_record = await self.create_tool_execution_record(
            contact_id, tool_id, function_name, parameters, execution_context
        )
        
        try:
            # 4. 获取工具定义和 Contact 自定义配置
            tool_def = await self.tool_registry.get_tool(tool_id)
            contact_tool_config = contact.instance_config.get("tools", {}).get(tool_id, {})
            
            # 5. 应用 Contact 级别的参数覆盖和限制
            validated_params = await self._apply_contact_tool_config(
                tool_def.schema, 
                parameters, 
                contact_tool_config,
                contact.resource_limits
            )
            
            # 6. 执行工具调用
            result = await self.call_tool_function(
                tool_def, function_name, validated_params, contact
            )
            
            # 7. 记录成功结果
            await self.update_tool_execution_record(
                execution_record.id, 
                status='completed',
                result=result,
                tokens_used=result.get('tokens_used', 0)
            )
            
            # 8. 更新 Contact 使用统计
            await self._update_contact_tool_usage_stats(contact_id, tool_id, result)
            
            return result
            
        except Exception as e:
            # 9. 记录错误和恢复
            await self.update_tool_execution_record(
                execution_record.id,
                status='failed',
                error=str(e)
            )
            
            # 10. 错误处理和用户通知
            await self._handle_tool_execution_error(contact, tool_id, e)
            raise
    
    async def _apply_contact_tool_config(
        self,
        tool_schema: Dict,
        parameters: Dict[str, Any],
        contact_config: Dict,
        resource_limits: Dict
    ) -> Dict[str, Any]:
        """应用 Contact 级别的工具配置和限制"""
        
        # 应用 Contact 自定义的默认参数
        validated_params = {**contact_config.get("default_params", {}), **parameters}
        
        # 应用资源限制
        if "max_tokens" in resource_limits:
            validated_params["max_tokens"] = min(
                validated_params.get("max_tokens", resource_limits["max_tokens"]),
                resource_limits["max_tokens"]
            )
        
        # 验证参数符合工具模式
        self.validate_parameters(tool_schema, validated_params)
        
        return validated_params
```

### 3. 完整的追溯系统

```python
# 示例：执行追溯架构设计
class ExecutionTracer:
    """执行追踪器 - 记录每个步骤"""
    
    async def trace_workflow_execution(self, workflow_execution_id: str):
        """追溯工作流执行过程"""
        
        # 获取工作流执行记录
        workflow = await self.workflow_repo.get_execution(workflow_execution_id)
        
        # 获取所有节点执行记录
        nodes = await self.execution_repo.get_node_executions(workflow_execution_id)
        
        # 获取工具调用记录
        for node in nodes:
            node.tool_calls = await self.tool_repo.get_tool_executions(node.id)
        
        # 获取记忆引用记录
        for node in nodes:
            node.memory_refs = await self.memory_repo.get_memory_references(node.id)
        
        # 获取Token使用记录
        token_usage = await self.metrics_repo.get_token_usage(workflow_execution_id)
        
        # 构建完整的执行追溯链
        trace_chain = self.build_trace_chain(workflow, nodes, token_usage)
        
        return trace_chain
```

### 4. 日志和监控系统

```python
# 示例：监控系统架构设计
class MonitoringService:
    """监控服务 - 全面的系统监控"""
    
    async def record_workflow_metrics(self, 
                                    workflow_execution: WorkflowExecution,
                                    nodes: List[NodeExecution]):
        """记录工作流指标"""
        
        # 1. 工作流整体指标
        workflow_metrics = {
            'workflow_duration': workflow_execution.duration_ms,
            'nodes_count': len(nodes),
            'success_rate': self.calculate_success_rate(nodes),
            'total_tokens': sum(node.token_usage.total for node in nodes),
            'total_cost': sum(node.token_usage.cost_usd for node in nodes)
        }
        
        await self.metrics_repo.record_metrics(
            'workflow_performance', workflow_metrics
        )
        
        # 2. 节点级别指标
        for node in nodes:
            node_metrics = {
                'node_duration': node.duration_ms,
                'token_usage': node.token_usage.total,
                'tool_calls_count': len(node.tool_calls),
                'memory_refs_count': len(node.memory_refs)
            }
            
            await self.metrics_repo.record_metrics(
                'node_performance', node_metrics, tags={
                    'node_type': node.node_type,
                    'agent_id': node.agent_id
                }
            )
```

### 5. 基于 Contact 的 Token 使用统计

```python
# 示例：Contact Token 统计架构设计
class ContactTokenUsageService:
    """Contact Token 使用统计服务"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.token_repo = TokenUsageRepository(db_session)
        self.contact_repo = ContactRepository(db_session)
    
    async def track_contact_token_usage(
        self,
        contact_id: UUID,
        execution_context: ExecutionContext,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_per_1k_tokens: Dict[str, float]
    ):
        """追踪 Contact 级别的 Token 使用"""
        
        # 获取 Contact 实例信息
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact:
            raise ContactNotFoundError(f"Contact {contact_id} not found")
        
        total_tokens = prompt_tokens + completion_tokens
        
        # 计算成本 (考虑 Contact 个性化配置对成本的影响)
        base_prompt_cost = (prompt_tokens / 1000) * cost_per_1k_tokens['prompt']
        base_completion_cost = (completion_tokens / 1000) * cost_per_1k_tokens['completion']
        
        # 应用 Contact 级别的成本调整 (如果有定制模型配置)
        cost_multiplier = contact.instance_config.get("cost_multiplier", 1.0)
        total_cost = (base_prompt_cost + base_completion_cost) * cost_multiplier
        
        # 创建详细的使用记录
        usage_log = TokenUsageLog(
            workflow_execution_id=execution_context.workflow_execution_id,
            node_execution_id=execution_context.node_execution_id,
            contact_id=contact_id,
            agent_id=contact.agent_id,
            user_id=contact.user_id,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=total_cost,
            contact_config_snapshot=contact.instance_config,
            recorded_at=datetime.utcnow()
        )
        
        await self.token_repo.create(usage_log)
        
        # 更新 Contact 实时统计
        await self._update_contact_usage_stats(contact_id, usage_log)
        
        # 检查 Contact 预算限制
        await self._check_contact_budget_limits(contact_id, usage_log)
        
        # 更新用户级别统计
        await self._update_user_usage_stats(contact.user_id, usage_log)
    
    async def get_contact_usage_analysis(
        self, 
        contact_id: UUID, 
        time_range: TimeRange
    ) -> ContactUsageAnalysis:
        """获取 Contact 使用分析报告"""
        
        # 查询 Contact 在指定时间范围内的所有使用记录
        usage_logs = await self.token_repo.get_contact_usage_logs(
            contact_id, time_range.start, time_range.end
        )
        
        if not usage_logs:
            return ContactUsageAnalysis.empty(contact_id)
        
        # 计算基础统计信息
        total_tokens = sum(log.total_tokens for log in usage_logs)
        total_cost = sum(log.cost_usd for log in usage_logs)
        avg_tokens_per_interaction = total_tokens / len(usage_logs)
        
        # 按模型分组统计
        model_usage = defaultdict(lambda: {"tokens": 0, "cost": 0, "count": 0})
        for log in usage_logs:
            model_usage[log.model_name]["tokens"] += log.total_tokens
            model_usage[log.model_name]["cost"] += log.cost_usd
            model_usage[log.model_name]["count"] += 1
        
        # 时间趋势分析
        daily_usage = self._calculate_daily_usage_trend(usage_logs)
        
        # 效率分析
        efficiency_metrics = await self._calculate_contact_efficiency_metrics(
            contact_id, usage_logs
        )
        
        return ContactUsageAnalysis(
            contact_id=contact_id,
            time_range=time_range,
            total_tokens=total_tokens,
            total_cost=total_cost,
            interaction_count=len(usage_logs),
            avg_tokens_per_interaction=avg_tokens_per_interaction,
            model_breakdown=dict(model_usage),
            daily_trend=daily_usage,
            efficiency_metrics=efficiency_metrics
        )
    
    async def _check_contact_budget_limits(
        self, 
        contact_id: UUID, 
        usage_log: TokenUsageLog
    ):
        """检查 Contact 预算限制并执行相应动作"""
        
        # 获取 Contact 的预算设置
        contact = await self.contact_repo.get_by_id(contact_id)
        budget_config = contact.instance_config.get("budget", {})
        
        if not budget_config:
            return
        
        # 计算当月累计使用
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        monthly_usage = await self.token_repo.get_contact_monthly_usage(
            contact_id, month_start
        )
        
        monthly_limit = budget_config.get("monthly_limit_usd")
        if monthly_limit and monthly_usage.total_cost >= monthly_limit:
            # 超出预算，暂停 Contact
            await self._suspend_contact_for_budget_exceeded(contact_id)
            
        # 预算预警
        warning_threshold = budget_config.get("warning_threshold", 0.8)
        if monthly_limit and monthly_usage.total_cost >= monthly_limit * warning_threshold:
            await self._send_budget_warning(contact_id, monthly_usage, monthly_limit)
```

## 🔒 安全和权限设计

### 1. 智能体权限模型

```python
# 智能体权限定义
class AgentPermissions:
    """智能体权限模型"""
    
    def __init__(self):
        self.tool_permissions: Dict[str, List[str]] = {}  # 工具使用权限
        self.memory_permissions: Dict[str, List[str]] = {}  # 记忆访问权限
        self.resource_limits: Dict[str, Any] = {}  # 资源限制
        self.execution_limits: Dict[str, Any] = {}  # 执行限制
```

### 2. API 安全控制

```python
# API安全中间件
class SecurityMiddleware:
    """API安全中间件"""
    
    async def authenticate_request(self, request):
        """请求认证"""
        pass
    
    async def authorize_agent_access(self, agent_id: str, resource: str):
        """智能体访问授权"""
        pass
    
    async def rate_limit_check(self, user_id: str, endpoint: str):
        """限流检查"""
        pass
```

## 📈 性能优化策略

### 1. 数据库优化

- **连接池管理**: 使用 SQLAlchemy 连接池
- **查询优化**: 预编译查询，避免N+1问题
- **索引策略**: 关键字段建立索引
- **分区表**: 大数据量表按时间分区

### 2. 缓存策略

- **Redis缓存**: 智能体配置、工具定义缓存
- **内存缓存**: 工作流定义、节点注册信息
- **查询结果缓存**: 常用查询结果缓存

### 3. 异步处理

- **异步I/O**: 所有数据库和外部API调用异步化
- **并行执行**: 独立节点并行执行
- **后台任务**: 日志记录、指标收集后台处理

## 📋 开发优先级建议

### 高优先级 (必须完成)
1. **数据库设计和模型** - 系统基础
2. **LangGraph工作流引擎** - 核心功能
3. **智能体框架** - 主要功能
4. **API接口** - 前端集成必需
5. **基础监控和日志** - 系统稳定性

### 中优先级 (重要功能)
1. **工具调用系统** - 智能体能力扩展
2. **记忆管理优化** - 用户体验提升
3. **WebSocket实时通信** - 交互体验
4. **性能监控** - 系统优化
5. **Token统计** - 成本控制

### 低优先级 (可后续添加)
1. **高级协作模式** - 功能增强
2. **详细分析报告** - 数据洞察
3. **A/B测试框架** - 产品优化
4. **多租户支持** - 扩展性
5. **集成测试自动化** - 开发效率

这个实现方案提供了完整的后端架构规划，涵盖了您提出的所有需求点。建议按照阶段化的方式实施，确保每个阶段都有可验证的交付物。
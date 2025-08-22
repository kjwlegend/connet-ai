# Connet.AI 系统目录架构

> 基于 LangGraph 多智能体协作的完整后端目录结构设计

## 📋 目录

- [总体架构概览](#总体架构概览)
- [详细目录结构](#详细目录结构)
- [核心模块说明](#核心模块说明)
- [新增业务模块](#新增业务模块)
- [文件命名规范](#文件命名规范)
- [相关文档](#相关文档)

## 🎯 总体架构概览

### 设计原则

- **渐进式扩展**: 基于现有 BFF 架构扩展，保持向后兼容
- **模块化设计**: 清晰的功能模块划分，便于维护和扩展
- **业务驱动**: 支持 Agent 市场 → Contact 实例 → Conversation → Group Chat 的完整业务流程
- **游戏化集成**: 内置支持会员系统、积分体系、用户成长等商业化功能

### 架构分层

```
┌─────────────────────────────────────────┐
│           API路由层 (api/)              │ ← 处理HTTP请求和WebSocket
├─────────────────────────────────────────┤
│           业务服务层 (services/)         │ ← 业务逻辑和服务编排
├─────────────────────────────────────────┤
│           智能体层 (agents/)            │ ← LangGraph集成和Agent管理
├─────────────────────────────────────────┤
│           数据模型层 (infrastructure/)   │ ← 数据库模型和仓库
├─────────────────────────────────────────┤
│           基础设施层 (infrastructure/)   │ ← 外部服务和配置管理
└─────────────────────────────────────────┘
```

## 🏗️ 详细目录结构

```
bff/
├── app/                                  # 主应用目录
│   ├── main.py                           # ✅ FastAPI 主入口 (无需修改)
│   ├── __init__.py
│   │
│   ├── api/                              # API路由层
│   │   ├── __init__.py
│   │   ├── dependencies.py               # ✅ 现有依赖注入 (扩展)
│   │   ├── middleware.py                 # ✅ 现有中间件 (扩展)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                 # ✅ 路由注册器
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           │
│   │           # 核心功能接口
│   │           ├── ai_agents.py          # 🔄 Agent市场和管理
│   │           ├── ai_chat.py            # 🔄 重构为LangGraph驱动
│   │           ├── contacts.py           # ✅ Contact实例管理
│   │           ├── conversations.py      # ✅ 对话管理
│   │           │
│   │           # 用户和认证
│   │           ├── auth.py               # ✅ 认证接口
│   │           ├── users.py              # ✅ 用户接口
│   │           ├── settings.py           # ✅ 用户设置
│   │           │
│   │           # 业务功能接口 (🆕 新增)
│   │           ├── membership.py         # 🆕 会员权益管理
│   │           ├── gamification.py       # 🆕 游戏化系统 (积分/等级)
│   │           ├── rewards.py            # 🆕 奖励和任务系统
│   │           ├── marketplace.py        # 🆕 Agent市场交易
│   │           │
│   │           # AI工作流接口 (🆕 新增)
│   │           ├── workflows.py          # 🆕 工作流管理
│   │           ├── tools.py              # 🆕 工具管理和调用
│   │           ├── analytics.py          # 🆕 分析统计
│   │           │
│   │           # 内容和社交
│   │           ├── timeline.py           # ✅ 时间线接口
│   │           ├── files.py              # ✅ 文件管理
│   │           └── health.py             # ✅ 健康检查
│   │
│   ├── config/                           # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py                   # ✅ 基础配置
│   │   ├── agents_config.yaml            # 🆕 Agent配置
│   │   ├── tools_config.yaml             # 🆕 工具配置
│   │   ├── workflows_config.yaml         # 🆕 工作流配置
│   │   └── business_config.yaml          # 🆕 商业化配置
│   │
│   ├── core/                             # 核心接口层
│   │   ├── __init__.py
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── repositories/             # ✅ 仓库接口
│   │
│   ├── services/                         # 业务服务层
│   │   ├── __init__.py
│   │   ├── base.py                       # ✅ 基础服务类
│   │   │
│   │   # 现有核心服务 (扩展)
│   │   ├── ai_agent_service.py           # 🔄 增强LangGraph集成
│   │   ├── ai_memory_service.py          # 🔄 增强Mem0集成
│   │   ├── auth_service.py               # ✅ 认证服务
│   │   ├── contact_service.py            # ✅ 联系人服务
│   │   ├── conversation_service.py       # ✅ 对话服务
│   │   ├── knowledge_service.py          # ✅ 知识服务
│   │   ├── rag_service.py                # 🔄 集成到工作流
│   │   ├── supabase_auth_service.py      # ✅ Supabase认证
│   │   ├── tools_service.py              # 🔄 扩展工具执行
│   │   ├── user_service.py               # ✅ 用户服务
│   │   │
│   │   # 新增商业化服务 (🆕)
│   │   ├── membership_service.py         # 🆕 会员权益服务
│   │   ├── gamification_service.py       # 🆕 游戏化系统服务
│   │   ├── points_service.py             # 🆕 积分管理服务
│   │   ├── subscription_service.py       # 🆕 订阅管理服务
│   │   ├── payment_service.py            # 🆕 支付处理服务
│   │   ├── marketplace_service.py        # 🆕 市场交易服务
│   │   │
│   │   # LangGraph工作流服务 (🆕)
│   │   ├── langgraph/
│   │   │   ├── __init__.py
│   │   │   ├── workflow_engine.py        # 工作流引擎
│   │   │   ├── node_registry.py          # 节点注册中心
│   │   │   ├── state_manager.py          # 状态管理器
│   │   │   ├── execution_tracker.py      # 执行追踪器
│   │   │   ├── mention_router.py         # @mention路由器
│   │   │   └── dynamic_builder.py        # 动态工作流构建器
│   │   │
│   │   # 工具和监控服务 (🆕)
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── tool_executor.py          # 工具执行器
│   │   │   ├── tool_registry.py          # 工具注册中心
│   │   │   ├── permission_checker.py     # 权限检查器
│   │   │   └── builtin_tools/            # 内置工具
│   │   │       ├── code_tools.py
│   │   │       ├── search_tools.py
│   │   │       ├── file_tools.py
│   │   │       └── web_tools.py
│   │   │
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       ├── execution_tracer.py       # 执行追踪器
│   │       ├── metrics_collector.py      # 指标收集器
│   │       ├── token_counter.py          # Token统计器
│   │       ├── performance_monitor.py    # 性能监控器
│   │       └── usage_analyzer.py         # 使用分析器
│   │
│   ├── schemas/                          # API模式定义
│   │   ├── __init__.py
│   │   ├── base.py                       # ✅ 基础模式
│   │   ├── responses.py                  # ✅ 响应模式
│   │   │
│   │   # 现有模式 (扩展)
│   │   ├── ai.py                         # 🔄 AI相关模式 - 扩展
│   │   ├── auth.py                       # ✅ 认证模式
│   │   ├── contact.py                    # ✅ 联系人模式
│   │   ├── conversation.py               # ✅ 对话模式
│   │   ├── knowledge.py                  # ✅ 知识模式
│   │   ├── tools.py                      # 🔄 工具模式 - 扩展
│   │   ├── user.py                       # ✅ 用户模式
│   │   │
│   │   # 新增业务模式 (🆕)
│   │   ├── membership.py                 # 🆕 会员相关模式
│   │   ├── gamification.py               # 🆕 游戏化模式
│   │   ├── marketplace.py                # 🆕 市场交易模式
│   │   ├── payment.py                    # 🆕 支付相关模式
│   │   │
│   │   # 新增工作流模式 (🆕)
│   │   ├── workflows.py                  # 🆕 工作流相关模式
│   │   ├── analytics.py                  # 🆕 分析统计模式
│   │   └── langgraph.py                  # 🆕 LangGraph状态模式
│   │
│   ├── infrastructure/                   # 基础设施层
│   │   ├── __init__.py
│   │   │
│   │   ├── cache/                        # ✅ 缓存系统
│   │   │   ├── cache_decorators.py       # ✅ 缓存装饰器
│   │   │   ├── cache_keys.py             # ✅ 缓存键管理
│   │   │   └── redis_client.py           # 🆕 Redis客户端封装
│   │   │
│   │   ├── database/                     # 数据库层
│   │   │   ├── __init__.py
│   │   │   ├── connection.py             # ✅ 数据库连接
│   │   │   │
│   │   │   ├── models/                   # 数据库模型
│   │   │   │   ├── __init__.py
│   │   │   │   │
│   │   │   │   # 现有模型 (扩展)
│   │   │   │   ├── agent_model.py        # 🔄 扩展LangGraph字段
│   │   │   │   ├── contact_model.py      # ✅ 联系人模型
│   │   │   │   ├── conversation_model.py # ✅ 对话模型
│   │   │   │   ├── file_model.py         # ✅ 文件模型
│   │   │   │   ├── knowledge_model.py    # ✅ 知识模型
│   │   │   │   ├── message_model.py      # ✅ 消息模型
│   │   │   │   ├── tool_model.py         # 🔄 扩展工具模型
│   │   │   │   ├── user_model.py         # ✅ 用户模型
│   │   │   │   │
│   │   │   │   # 新增商业化模型 (🆕)
│   │   │   │   ├── membership_model.py   # 🆕 会员模型
│   │   │   │   ├── subscription_model.py # 🆕 订阅模型
│   │   │   │   ├── points_model.py       # 🆕 积分模型
│   │   │   │   ├── level_model.py        # 🆕 等级模型
│   │   │   │   ├── task_model.py         # 🆕 任务模型
│   │   │   │   ├── reward_model.py       # 🆕 奖励模型
│   │   │   │   ├── transaction_model.py  # 🆕 交易模型
│   │   │   │   │
│   │   │   │   # 新增工作流模型 (🆕)
│   │   │   │   ├── workflow_execution_model.py  # 🆕 工作流执行
│   │   │   │   ├── node_execution_model.py      # 🆕 节点执行
│   │   │   │   ├── tool_execution_model.py      # 🆕 工具执行
│   │   │   │   ├── token_usage_model.py         # 🆕 Token使用
│   │   │   │   └── analytics_model.py           # 🆕 分析数据
│   │   │   │
│   │   │   └── repositories/             # 仓库实现层
│   │   │       ├── __init__.py
│   │   │       ├── base_repository.py    # ✅ 基础仓库
│   │   │       │
│   │   │       # 现有仓库 (扩展)
│   │   │       ├── agent_repository_impl.py     # 🔄 扩展节点管理
│   │   │       ├── ai_memory_repository_impl.py # 🔄 优化记忆管理
│   │   │       ├── contacts_repository_impl.py  # ✅ 联系人仓库
│   │   │       ├── conversation_repository_impl.py # ✅ 对话仓库
│   │   │       ├── knowledge_repository_impl.py # ✅ 知识仓库
│   │   │       ├── message_repository_impl.py   # ✅ 消息仓库
│   │   │       ├── tools_repository_impl.py     # 🔄 扩展工具仓库
│   │   │       ├── user_repository_impl.py      # ✅ 用户仓库
│   │   │       │
│   │   │       # 新增商业化仓库 (🆕)
│   │   │       ├── membership_repository.py     # 🆕 会员仓库
│   │   │       ├── subscription_repository.py   # 🆕 订阅仓库
│   │   │       ├── points_repository.py         # 🆕 积分仓库
│   │   │       ├── task_repository.py           # 🆕 任务仓库
│   │   │       ├── reward_repository.py         # 🆕 奖励仓库
│   │   │       │
│   │   │       # 新增工作流仓库 (🆕)
│   │   │       ├── workflow_execution_repository.py # 🆕 工作流执行仓库
│   │   │       ├── node_execution_repository.py     # 🆕 节点执行仓库
│   │   │       ├── tool_execution_repository.py     # 🆕 工具执行仓库
│   │   │       ├── token_usage_repository.py        # 🆕 Token使用仓库
│   │   │       └── analytics_repository.py          # 🆕 分析数据仓库
│   │   │
│   │   ├── external/                     # 外部服务集成
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── supabase/                 # ✅ Supabase集成
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py               # ✅ 认证集成
│   │   │   │   ├── client.py             # ✅ 客户端
│   │   │   │   ├── realtime.py           # ✅ 实时通信
│   │   │   │   └── storage.py            # ✅ 存储
│   │   │   │
│   │   │   ├── payment/                  # 🆕 支付服务集成
│   │   │   │   ├── __init__.py
│   │   │   │   ├── stripe_client.py      # 🆕 Stripe集成
│   │   │   │   ├── creem_client.py       # 🆕 Creem.io集成
│   │   │   │   └── webhook_handler.py    # 🆕 支付回调处理
│   │   │   │
│   │   │   ├── llm/                      # 🆕 智能LLM路由集成
│   │   │   │   ├── __init__.py
│   │   │   │   ├── unified_client.py     # 🆕 统一LLM客户端 (OpenAI格式)
│   │   │   │   ├── model_router.py       # 🆕 智能模型路由器
│   │   │   │   ├── task_analyzer.py      # 🆕 任务复杂度分析器
│   │   │   │   ├── cost_calculator.py    # 🆕 成本计算器
│   │   │   │   ├── tier_manager.py       # 🆕 会员等级模型管理器
│   │   │   │   └── usage_monitor.py      # 🆕 用量监控器
│   │   │   │
│   │   │   └── mem0/                     # 🆕 Mem0记忆服务
│   │   │       ├── __init__.py
│   │   │       ├── memory_client.py      # 🆕 Mem0客户端
│   │   │       └── memory_manager.py     # 🆕 记忆管理器
│   │   │
│   │   ├── messaging/                    # 消息系统
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py              # ✅ 事件总线
│   │   │   ├── notification_service.py   # 🆕 通知服务
│   │   │   └── websocket_manager.py      # 🆕 WebSocket管理器
│   │   │
│   │   └── security/                     # 安全系统
│   │       ├── __init__.py
│   │       ├── auth.py                   # ✅ 认证
│   │       ├── permissions.py            # ✅ 权限管理
│   │       ├── rate_limiter.py           # 🆕 限流器
│   │       └── encryption.py             # 🆕 加密工具
│   │
│   ├── utils/                            # 工具函数
│   │   ├── __init__.py
│   │   ├── constants.py                  # ✅ 常量定义
│   │   ├── datetime.py                   # ✅ 日期工具
│   │   ├── helpers.py                    # ✅ 辅助函数
│   │   ├── logging.py                    # ✅ 日志工具
│   │   │
│   │   # 新增工具 (🆕)
│   │   ├── validation.py                 # 🆕 验证工具
│   │   ├── serialization.py              # 🆕 序列化工具
│   │   ├── token_counter.py              # 🆕 Token计数器
│   │   ├── langgraph_helpers.py          # 🆕 LangGraph辅助工具
│   │   ├── business_helpers.py           # 🆕 商业化辅助工具
│   │   └── gamification_helpers.py       # 🆕 游戏化辅助工具
│   │
│   └── agents/                           # 智能体实现
│       ├── __init__.py
│       ├── base_agent.py                 # 基础智能体类
│       ├── registry.py                   # 智能体注册器
│       │
│       ├── builtin/                      # 内置智能体
│       │   ├── __init__.py
│       │   ├── coder_agent.py            # 代码助手
│       │   ├── analyst_agent.py          # 数据分析师
│       │   ├── writer_agent.py           # 写作助手
│       │   ├── researcher_agent.py       # 研究员
│       │   ├── business_agent.py         # 🆕 商业分析师
│       │   └── support_agent.py          # 🆕 客服助手
│       │
│       └── marketplace/                  # 🆕 市场智能体
│           ├── __init__.py
│           ├── agent_validator.py        # 🆕 Agent验证器
│           ├── agent_publisher.py        # 🆕 Agent发布器
│           └── agent_recommender.py      # 🆕 Agent推荐器
│
├── alembic/                              # 数据库迁移
│   ├── versions/
│   │   ├── 001_initial_migration.py
│   │   ├── 002_add_business_tables.py    # 🆕 商业化表结构
│   │   ├── 003_add_workflow_tables.py    # 🆕 工作流表结构
│   │   └── 004_add_analytics_tables.py   # 🆕 分析统计表
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
│
├── tests/                                # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   │
│   ├── test_api/                         # API测试
│   │   ├── test_endpoints/
│   │   ├── test_auth.py
│   │   ├── test_business.py              # 🆕 商业化功能测试
│   │   └── test_workflows.py             # 🆕 工作流测试
│   │
│   ├── test_services/                    # 服务测试
│   │   ├── test_ai_services.py
│   │   ├── test_business_services.py     # 🆕 商业化服务测试
│   │   └── test_langgraph_services.py    # 🆕 LangGraph服务测试
│   │
│   ├── test_models/                      # 模型测试
│   │   ├── test_user_models.py
│   │   ├── test_business_models.py       # 🆕 商业化模型测试
│   │   └── test_workflow_models.py       # 🆕 工作流模型测试
│   │
│   └── test_agents/                      # 智能体测试
│       ├── test_builtin_agents.py
│       ├── test_agent_registry.py
│       └── test_marketplace_agents.py    # 🆕 市场智能体测试
│
├── scripts/                              # 脚本目录
│   ├── __init__.py
│   ├── init_db.py                        # 数据库初始化
│   ├── seed_agents.py                    # 智能体数据种子
│   ├── seed_business.py                  # 🆕 商业化数据种子
│   ├── migrate_data.py                   # 数据迁移
│   └── backup_db.py                      # 🆕 数据库备份
│
├── config/                               # 配置文件目录
│   ├── __init__.py
│   ├── settings.py                       # 基础配置
│   ├── agents_config.yaml                # 智能体配置
│   ├── tools_config.yaml                 # 工具配置
│   ├── workflows_config.yaml             # 工作流配置
│   ├── business_config.yaml              # 🆕 商业化配置
│   ├── payment_config.yaml               # 🆕 支付配置
│   └── deployment_config.yaml            # 🆕 部署配置
│
├── docs/                                 # 项目文档
│   ├── api/                              # API文档
│   ├── architecture/                     # 架构文档
│   ├── deployment/                       # 部署文档
│   └── business/                         # 🆕 商业化文档
│
├── requirements.txt                      # Python依赖
├── pyproject.toml                        # 项目配置
├── Dockerfile                            # Docker配置
├── docker-compose.yml                    # Docker Compose
├── .env.example                          # 环境变量示例
├── Makefile                              # 构建脚本
└── README.md                             # 项目说明
```

## 🎯 核心模块说明

### 1. API 路由层 (api/)

**职责**: HTTP 请求处理、参数验证、响应格式化

**新增端点**:

- `membership.py`: 会员权益管理接口
- `gamification.py`: 积分、等级、任务系统接口
- `rewards.py`: 奖励发放和统计接口
- `marketplace.py`: Agent 市场交易接口
- `workflows.py`: 工作流管理接口

### 2. 业务服务层 (services/)

**职责**: 业务逻辑实现、服务编排

**新增服务模块**:

- **商业化服务**: membership, gamification, points, subscription, payment
- **LangGraph 服务**: workflow_engine, node_registry, state_manager
- **工具服务**: tool_executor, tool_registry, permission_checker
- **监控服务**: execution_tracer, metrics_collector, usage_analyzer

### 3. 智能体层 (agents/)

**职责**: Agent 定义、注册、市场管理

**组织结构**:

- `builtin/`: 内置系统 Agent (代码助手、写作助手等)
- `marketplace/`: 市场 Agent 管理 (验证器、发布器、推荐器)
- `registry.py`: 统一 Agent 注册和发现机制

### 4. 数据模型层 (infrastructure/database/models/)

**职责**: 数据库实体定义、关系映射

**新增模型类别**:

- **商业化模型**: 会员、订阅、积分、等级、任务、奖励、交易
- **工作流模型**: 工作流执行、节点执行、工具执行、Token 使用
- **分析模型**: 用户行为、使用统计、性能指标

### 5. 基础设施层 (infrastructure/)

**职责**: 外部服务集成、配置管理

**扩展集成**:

- `payment/`: Stripe、Creem.io 支付集成
- `llm/`: 智能 LLM 模型路由和成本优化
- `mem0/`: Mem0 记忆服务集成

## 🆕 新增业务模块

### 商业化游戏化系统

#### 会员权益管理

```
services/membership_service.py     # 会员权益逻辑
models/membership_model.py         # 会员数据模型
repositories/membership_repository.py  # 会员数据访问
endpoints/membership.py           # 会员API接口
```

#### 积分等级体系

```
services/gamification_service.py  # 游戏化逻辑
services/points_service.py         # 积分管理逻辑
models/points_model.py             # 积分数据模型
models/level_model.py              # 等级数据模型
endpoints/gamification.py         # 游戏化API接口
```

#### 任务奖励系统

```
services/task_service.py           # 任务管理逻辑 (新增)
models/task_model.py               # 任务数据模型
models/reward_model.py             # 奖励数据模型
repositories/task_repository.py    # 任务数据访问
endpoints/rewards.py               # 奖励API接口
```

### LangGraph 工作流系统

#### 工作流引擎

```
services/langgraph/workflow_engine.py     # 核心工作流引擎
services/langgraph/dynamic_builder.py     # 动态工作流构建器
services/langgraph/state_manager.py       # 状态管理器
models/workflow_execution_model.py        # 工作流执行模型
```

#### 智能体协作

```
services/langgraph/node_registry.py       # 节点注册中心
services/langgraph/mention_router.py      # @mention路由器
models/node_execution_model.py            # 节点执行模型
agents/base_agent.py                      # 基础智能体类
```

### 智能LLM路由系统

#### 动态模型选择

```
infrastructure/external/llm/model_router.py       # 智能模型路由器
infrastructure/external/llm/task_analyzer.py      # 任务复杂度分析器
infrastructure/external/llm/cost_calculator.py    # 成本计算器
infrastructure/external/llm/tier_manager.py       # 会员等级模型管理器
```

### 监控分析系统

#### 执行追踪

```
services/monitoring/execution_tracer.py   # 执行追踪器
services/monitoring/token_counter.py      # Token统计器
models/token_usage_model.py               # Token使用模型
repositories/analytics_repository.py      # 分析数据仓库
```

## 📝 文件命名规范

### 模块命名

- **模型文件**: `{domain}_model.py` (如 `membership_model.py`)
- **服务文件**: `{domain}_service.py` (如 `gamification_service.py`)
- **仓库文件**: `{domain}_repository.py` (如 `points_repository.py`)
- **API 文件**: `{domain}.py` (如 `membership.py`)

### 类命名

- **模型类**: `{Domain}Model` (如 `MembershipModel`)
- **服务类**: `{Domain}Service` (如 `GamificationService`)
- **仓库类**: `{Domain}Repository` (如 `PointsRepository`)

### 常量和配置

- **常量文件**: `constants.py` (全局常量)
- **配置文件**: `{domain}_config.yaml` (如 `business_config.yaml`)
- **环境变量**: `{DOMAIN}_{SETTING}` (如 `MEMBERSHIP_TIER_COUNT`)

## 📚 相关文档

### 核心架构文档

- **[架构概览](architecture-overview.md)** - 整体系统架构设计
- **[数据库设计](database-design.md)** - 详细数据模型和关系
- **[LangGraph 集成](langgraph-architecture.md)** - 工作流引擎架构
- **[智能LLM路由](intelligent-llm-routing.md)** - 智能模型选择和成本优化策略

### 业务设计文档

- **[业务商业化模型](business-model.md)** - 游戏化和收费策略
- **[用户体验策略](user-psychology-strategy.md)** - 用户心理学和转化设计

### 实施文档

- **[实施计划](implementation-plan.md)** - 分阶段开发计划
- **[迁移策略](migration-strategy.md)** - 系统迁移方案
- **[部署指南](deployment-guide.md)** - 生产环境部署

---

> 📝 **文档维护**: 架构团队 + 开发团队  
> 🔄 **最后更新**: 2025-08-22  
> 📋 **相关决策**: [ADR-004: 系统目录架构设计](../decisions/adr-004-directory-architecture.md)

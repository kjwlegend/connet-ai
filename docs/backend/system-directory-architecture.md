# Connet.AI 系统目录架构

> BFF 后端在多 App 场景下的垂直切片（Vertical Slice）+ Clean/Hexagonal 组合目录指引

## 📋 目录
- [总体架构概览](#总体架构概览)
- [详细目录结构](#详细目录结构)
- [核心层说明](#核心层说明)
- [功能模块（modules/）规范](#功能模块modules规范)
- [测试与运维](#测试与运维)
- [文件命名规范](#文件命名规范)
- [相关文档](#相关文档)

## 🎯 总体架构概览

### 设计原则
- **垂直切片 + 分层**：每个业务模块带齐 router → schema → service → repository → model，模块之间通过接口交互，避免水平分层的跨目录耦合。
- **核心设施内聚**：跨模块的基础能力（配置、数据库、鉴权、异常等）统一放在 `app/core` 与 `app/infrastructure`，可被任何模块安全复用。
- **多 App 共享身份**：用户身份服务支撑多个 C 端 App，同一用户可在不同 App 拥有独立账号视图，邀请逻辑按 App 维度划分。
- **可扩展的外部集成**：Supabase、OAuth、Redis、对象存储等外部系统通过 infrastructure 适配层隔离。

### 分层关系
```
┌──────────────────────────────┐
│            api/              │ 依赖所有模块的 router
├──────────────────────────────┤
│           modules/           │ 垂直切片业务实现
├──────────────────────────────┤
│    core/ & infrastructure/   │ 共享设施、技术适配层
└──────────────────────────────┘
```

## 🏗️ 详细目录结构

```
bff/
├── app/
│   ├── main.py                  # FastAPI 入口
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps/                # 共享依赖：认证、RBAC、分页等
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # JWT / Supabase 解析
│   │   │   ├── db.py            # Session / Repository / UnitOfWork
│   │   │   ├── cache.py         # 缓存实例注入
│   │   │   ├── pagination.py    # 分页参数校验
│   │   │   ├── rbac.py          # RBAC 依赖，调用 core.security
│   │   │   └── services.py      # 组合 Service 层依赖
│   │   ├── routers.py           # include_router 聚合
│   │   └── lifespan.py          # 启动/关闭生命周期钩子
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic Settings / 环境变量
│   │   ├── db.py                # Engine、Session、UnitOfWork
│   │   ├── security.py          # 角色/权限基础逻辑
│   │   ├── events.py            # 领域事件 / 消息总线（可选）
│   │   ├── uow.py               # Unit of Work 抽象（可选）
│   │   └── exceptions.py        # 统一异常与错误码
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── sqlalchemy/
│   │   │   ├── __init__.py
│   │   │   ├── base.py          # Declarative Base / metadata
│   │   │   ├── mixins.py        # 通用字段（时间戳、多租字段等）
│   │   │   └── session.py       # Async engine & session 工厂
│   │   ├── caches/
│   │   │   ├── __init__.py
│   │   │   └── redis.py
│   │   ├── storages/
│   │   │   ├── __init__.py
│   │   │   └── s3.py
│   │   ├── email_sms/
│   │   │   ├── __init__.py
│   │   │   └── provider.py
│   │   └── supabase/
│   │       ├── __init__.py
│   │       └── client.py
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # SQLAlchemy/SQLModel 定义
│   │   │   ├── schemas.py       # Pydantic DTO / 请求响应
│   │   │   ├── repository.py    # 抽象接口（Protocol/ABC）
│   │   │   ├── repository_impl.py
│   │   │   ├── service.py       # 领域服务 & 协调逻辑
│   │   │   ├── router.py        # FastAPI 路由
│   │   │   ├── policies.py      # RBAC/ABAC 判定（可选）
│   │   │   ├── events.py        # 模块自有领域事件定义
│   │   │   ├── event_handlers.py # 注册本模块的事件监听
│   │   │   └── tasks.py         # 背景任务（可选）
│   │   │   ├── invitations/
│   │   │   │   └── models.py    # 邀请码等扩展模型（后续补仓库/服务）
│   │   │   ├── llm_settings/
│   │   │   │   └── models.py    # 用户 LLM 偏好配置
│   │   │   ├── prompt_library/
│   │   │   │   └── models.py    # 用户自定义提示语库
│   │   │   ├── registration/
│   │   │   │   └── models.py    # 注册来源追踪
│   │   │   └── subscriptions/
│   │   │       └── models.py    # 会员订阅信息
│   │   ├── contacts/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── repository_impl.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── timeline/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── repository_impl.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── conversations/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── repository_impl.py
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── messages/
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       ├── repository.py
│   │   │       ├── repository_impl.py
│   │   │       └── service.py
│   │   │   └── topics/
│   │   │       └── models.py
│   │   ├── auth/
│   │   │   ├── service.py       # Supabase / OAuth 组合
│   │   │   ├── router.py
│   │   │   └── provider_clients.py
│   │   ├── memberships/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── repository.py
│   │   │   ├── repository_impl.py
│   │   │   ├── service.py
│   │   │   └── router.py
│   │   ├── ai/
│   │   │   ├── agents/
│   │   │   ├── memory/
│   │   │   ├── knowledge_bases/
│   │   │   ├── rag/
│   │   │   ├── tools/
│   │   │   └── workflows/       # LangGraph & 工作流 slice
│   │   ├── storage/
│   │   │   └── files/
│   │   └── ...                  # 其他业务模块按需新增
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── unit/                # 以模块命名（users/test_service.py 等）
│   │   ├── integration/
│   │   └── e2e/
│   ├── alembic/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/            # 迁移文件按 `YYYYMMDD_module_desc.py`
│   └── docs/
│       └── module_guides/       # 各模块设计/决策记录（可选）
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── Makefile
└── README.md
```

## 🧩 核心层说明

### api/
- `deps/`：集中存放 FastAPI 依赖（`Depends`）函数，处理 JWT 校验、RBAC、分页、上下文注入等，供各 router 重用。
- `routers.py`：聚合所有模块的 router，保持入口清晰。
- `lifespan.py`：在应用启动/关闭时初始化数据库连接池、缓存、后台任务等资源。

### core/
- `config.py`：封装配置加载逻辑，向模块提供类型安全的设置对象。
- `db.py`：提供 `session()` 上下文/Unit of Work，保证事务控制。
- `security.py`：统一角色/权限检查、RBAC 辅助。
- `events.py`（规划中）：事件分发辅助、公共事件基类，可供模块共享。
- `db.py` / `uow.py`：对外暴露获取 session、事务或 UnitOfWork 的入口，模块只依赖抽象对象。
- `exceptions.py`：定义业务异常及错误码，结合 FastAPI 全局异常处理。

### infrastructure/
- `sqlalchemy/`：集中放置 Base、通用 mixin、session 创建逻辑，便于所有模块复用。
- `caches/`、`storages/`、`email_sms/`、`supabase/`：分别适配 Redis、对象存储、消息通道、Supabase 等外部服务，模块通过注入或接口调用。

## 🧱 功能模块（modules/）规范

- **模块自洽**：每个模块是一个闭环，从 HTTP 接口到持久化逻辑全部就地实现，降低跨文件夹耦合。
- **抽象接口优先**：`repository.py` 暴露 Protocol/ABC，实际实现放在 `repository_impl.py`，便于替换不同数据源（Postgres、Supabase、缓存等）。
- **服务层职责**：`service.py` 负责组合仓库、外部服务、策略（如邀请逻辑、RBAC 检查），对 router 暴露清晰的应用层 API。
- **策略/任务扩展**：`policies.py` 用于描述 ACL/ABAC 规则，`tasks.py` 用于 Celery/Arq 等异步任务或计划任务。
- **多 App 支持**：`users` 模块内包含 `client_apps`、`user_app_accounts`、`user_auth_identities` 等模型，与邀请、角色表协同满足多 App 的独立账号视图。

推荐初始模块清单：
1. `users`（身份、认证、RBAC、邀请）
2. `contacts`（联系人与关系）
3. `timeline`（社交动态、评论、点赞、分享）
4. `conversations`（会话、参与者、消息）
5. `auth`（Supabase + OAuth 登录流程）
6. `memberships`（会员与订阅）
7. `ai`（AI 相关能力：agents、memory、knowledge bases、RAG、tools、workflows 等子 slice）
8. `storage`（文件元数据与权限管理，面向知识库和多媒体场景）
   - `workflows/`：LangGraph 工作流引擎、会话服务、记忆管理、节点/工具注册与执行跟踪

## 🧪 测试与运维
- `tests/unit/`：根据模块划分子目录，例如 `tests/unit/users/test_service.py`。
- `tests/integration/`：覆盖数据库、缓存、外部依赖的组合测试。
- `tests/e2e/`：端到端接口或业务流程回归。
- `alembic/versions/`：命名建议 `YYYYMMDDHHMM_<module>_<change>.py`，便于追踪来源模块。

## 🧾 文件命名规范
- Python 模块全部使用 `snake_case`，类使用 `PascalCase`，函数/变量使用 `camel_case`。
- 路由文件命名为 `router.py`，Pydantic 模式为 `schemas.py`，仓库接口为 `repository.py`。
- 配置文件后缀保持 `.py` 或 `.yaml`，区分动态与静态配置。

## 🔗 相关文档
- `docs/backend/user-refactor-guide.md`：用户与身份模块的重构规划。
- `docs/backend/architecture-overview.md`：整体系统架构图。
- `docs/backend/progress-tracker.md`：后端阶段计划与交付清单。
- 若新增模块，请在 `docs/backend/module_guides/` 下记录设计决策与接口契约。
- `docs/backend/event-bus-architecture.md`：事件总线模式与使用规范。

项目初始化文档：[你的项目名称] AI 协作平台

1. 项目概述
   [你的项目名称] 是一个旨在通过人机协作和多智能体自主协作来完成复杂任务的 AI 平台。项目初期将专注于通过 @ 机制实现用户与多个 AI 智能体的动态交互，后续将发展为允许 AI 进行任务规划和自主协作执行的模式。
2. 核心目标
   阶段一 (人机协作):
   用户可以创建聊天室，并与默认 AI 智能体进行对话。
   用户可以通过 @ 机制在会话中动态引入其他专业 AI 智能体参与对话或执行特定任务。
   支持会话记忆共享和基本的上下文管理。
   所有 AI 交互均采用异步架构，保证用户体验流畅。
   阶段二 (自主协作):
   引入任务规划智能体，能够将用户的高层目标分解为可执行的子任务。
   多个 AI 智能体根据规划好的任务进行协作，自主完成目标。
   在 AI 自主执行过程中，提供人工检查点和干预机制。
   平衡 AI 自主性与执行成本（如 token 消耗）。
3. 技术架构
   前端: Next.js (React)
   后端 API: FastAPI (Python)
   AI 核心与编排: LangChain (LangGraph) (Python)
   数据库: PostgreSQL
   ORM: SQLModel (Python)
   向量数据库: ChromaDB (起步) / pgvector (集成于 PostgreSQL)
   缓存: Redis
   任务队列: ARQ (Async Redis Queue) (Python)
   实时通信: FastAPI WebSockets
   身份认证: FastAPI Security (OAuth2 with JWT)
   容器化: Docker, Docker Compose
   ASGI 服务器: Uvicorn (由 Gunicorn 管理)

针对未来扩展的架构调整与技术栈补充：

1. 用户端的注册试用
   这涉及到用户生命周期管理、试用策略以及可能的资源限制。
   用户注册流程:
   标准注册: 邮箱/密码，需要邮箱验证。
   社交登录 (OAuth): Google, GitHub, etc. 这能降低注册门槛。
   技术选型:
   FastAPI Security: 可以扩展以支持 OAuth2 客户端流程。
   NextAuth.js (前端): 如果前端处理 OAuth 回调，NextAuth.js 是一个优秀的选择，它可以与后端 FastAPI 配合使用（例如，NextAuth.js 处理认证，然后向 FastAPI 请求一个自定义的会话 token 或 JWT）。
   第三方认证服务 (Auth0, Okta, Firebase Auth, AWS Cognito): 这些服务内置了社交登录、邮箱验证、密码重置等功能，能极大简化开发。它们通常提供与后端无关的 JWT。
   试用策略:
   功能限制试用: 免费用户可以使用部分功能，或功能有次数/用量限制 (e.g., 每月可 @ 智能体 10 次，或 LLM token 用量限制)。
   时间限制试用: 注册后 N 天内可免费使用所有或部分高级功能。
   免费套餐: 永久免费但功能受限的基础套餐。
   数据库层面:
   User 模型: 需要增加字段来管理试用状态，例如 trial_ends_at (timestamp), plan_id (关联到套餐表), usage_limits (JSONB 存储各种用量限制和当前用量)。
   Plan 模型: 存储不同的会员套餐信息 (名称, 价格, 功能列表, 限制等)。
   技术实现:
   中间件/依赖项 (FastAPI): 检查用户套餐和用量限制，对于超出限制的请求返回错误。
   定时任务 (ARQ/Celery):
   处理试用到期逻辑（例如，发送提醒邮件，自动降级套餐）。
   定期重置用量（例如，每月初重置 token 数量）。
2. 商业化 (支付, 会员)
   这是将项目转化为可持续业务的关键。
   支付网关集成:
   Stripe (强烈推荐):
   优点: 开发者友好，文档完善，API 强大，支持订阅、一次性支付、多种支付方式，处理税务和合规性。有良好的 Python SDK (stripe-python)。
   缺点: 在某些地区可能不可用或费率较高。
   Paddle: 另一个流行的选择，尤其适合 SaaS 订阅，它可以作为 Merchant of Record (MoR)，处理税务和合规更彻底。
   PayPal: 广泛使用，但 API 可能不如 Stripe 现代。
   区域性支付网关: 根据你的目标市场选择，如支付宝、微信支付（中国）。
   订阅管理:
   Stripe Subscriptions: Stripe 提供了强大的订阅管理功能，包括创建套餐、处理循环付款、升级/降级、取消订阅、试用期管理等。
   FastAPI 后端:
   创建端点处理支付意图创建 (Payment Intents for Stripe)。
   创建 Webhook 端点接收来自支付网关的事件 (e.g., invoice.payment_succeeded, customer.subscription.updated, customer.subscription.deleted)。Webhook 是实现支付和订阅状态同步的关键。
   Webhook 处理逻辑会更新数据库中的用户套餐状态、有效期等。
   数据库层面:
   User 模型: stripe_customer_id (关联到 Stripe 的客户对象), subscription_id (关联到 Stripe 的订阅对象), subscription_status (e.g., active, trialing, past_due, canceled)。
   Subscription 或 Order 模型 (可选): 存储更详细的订阅或订单历史记录。
   安全性:
   PCI DSS 合规: 如果你直接处理信用卡信息（不推荐），需要符合 PCI DSS 标准。使用 Stripe Elements 或 Checkout 可以将大部分 PCI 合规责任转移给 Stripe。
   Webhook 安全: 验证来自支付网关的 Webhook 请求的签名，防止伪造请求。
3. 更多的插件和外部模块对接
   这需要一个灵活且可扩展的架构，允许轻松集成新的智能体能力或第三方服务。
   插件化架构 (AI/LangGraph 层面):
   标准化的插件接口: 定义一个清晰的接口，所有插件（或代表外部模块的 LangChain 工具/智能体）都必须实现这个接口。
   例如: 一个插件可能需要定义 name, description, input_schema (Pydantic model), output_schema (Pydantic model), execute_async(input_data, user_context) 方法。
   插件注册与发现机制:
   代码层面: 可以在一个集中的地方（例如，一个插件目录或配置文件）注册所有可用的插件。
   数据库层面 (更灵活): 将插件元数据存储在数据库中，允许动态加载和管理插件，甚至用户可以选择性启用/禁用某些插件。
   LangGraph 中的动态工具/节点加载:
   LangGraph 的智能体节点可以根据用户的请求或任务上下文，动态地从插件注册表中选择并加载合适的工具/插件来执行。
   Tool 对象在 LangChain 中是实现这种对接的自然方式。每个插件可以表现为一个或多个 Tool。
   沙箱与安全: 如果插件可以执行任意代码或调用外部 API，需要考虑安全沙箱机制，防止恶意插件破坏系统或泄露数据。
   外部模块/API 对接:
   API 密钥管理:
   用户可能需要提供他们自己的 API 密钥来使用某些插件（例如，访问他们自己的 Google Drive, Notion,或其他 SaaS 服务）。
   需要安全地存储这些用户提供的 API 密钥（例如，使用 HashiCorp Vault, AWS Secrets Manager, Google Secret Manager, 或至少是加密后存储在数据库中，并严格控制访问）。
   用户级别的 API 密钥应该与用户的会话或账户关联。
   OAuth 2.0 for Third-Party Services:
   对于需要代表用户访问第三方服务的插件，需要实现 OAuth 2.0 客户端流程来获取访问令牌。
   FastAPI 后端需要处理 OAuth 回调，安全存储和刷新 access/refresh tokens。
   统一的 API 调用层 (可选): 可以创建一个内部服务或库来封装对常用外部 API 的调用，处理认证、错误处理、重试等。
   版本控制与依赖管理:
   插件可能有自己的依赖项。如果插件是动态加载的，需要考虑如何管理这些依赖，避免冲突。
   插件也需要版本控制。
   技术栈影响与调整：
   身份认证: 可能会更倾向于使用第三方认证服务 (如 Auth0, Clerk, Supabase Auth)，因为它们通常内置了社交登录、更完善的用户管理界面，并且在处理 OAuth 流程方面经验更丰富，可以为未来的插件 OAuth 对接打下基础。
   数据库 (PostgreSQL): 角色和权限管理变得更重要。需要仔细设计表结构来支持套餐、订阅、插件配置、用户 API 密钥等。
   任务队列 (ARQ/Celery):
   处理 Webhook 事件应该是异步的，放在任务队列中，确保快速响应支付网关并处理潜在的失败和重试。
   处理与第三方 API 的长时间交互。
   配置管理: 随着插件和外部服务的增多，配置项会变多。使用 .env 文件结合 Pydantic Settings (FastAPI core/config.py 中常用) 是个好方法。对于更复杂的配置或动态配置，可以考虑 HashiCorp Consul 或类似工具。
   安全性:
   OWASP Top 10: 始终关注 Web 应用安全最佳实践。
   输入验证: 对所有来自用户和第三方的数据进行严格验证 (Pydantic 在这里很有用)。
   依赖项安全: 定期扫描项目依赖项的漏洞 (e.g., pip_audit, npm audit, Snyk)。
   API 限流与防滥用: 保护你的 API 和 LLM 调用不被滥用。
   项目代码结构目录的调整 (示意性，主要在后端)：

4. 项目代码结构目录 (建议)
   为了清晰和可维护性，我们将前端和后端代码放在同一个主项目仓库的不同子目录中。
   [your_project_name]/
   frontend/
   ├── src/
   │ ├── app/
   │ │ ├── (auth)/
   │ │ │ ├── login/page.tsx
   │ │ │ └── register/page.tsx
   │ │ ├── (main)/
   │ │ │ ├── layout.tsx
   │ │ │ ├── chat/
   │ │ │ │ └── [chatId]/page.tsx
   │ │ │ └── dashboard/page.tsx
   │ │ ├── api/
   │ │ │ └── auth/[...nextauth].ts # (如果使用 NextAuth.js)
   │ │ ├── globals.css
   │ │ ├── layout.tsx # 根布局 (重要: ThemeProvider, LocaleProvider 会在这里)
   │ │ └── page.tsx # 首页
   │ ├── components/
   │ │ ├── ui/ # shadcn/ui 生成的组件
   │ │ ├── layout/ # 布局组件 (Navbar, Sidebar, ThemeToggle, LanguageSwitcher)
   │ │ ├── chat/ # 聊天特定组件
   │ │ └── common/ # 其他可复用的通用组件
   │ ├── contexts/ # (如果某些简单全局状态仍用 Context)
   │ ├── hooks/ # 自定义 React Hooks (e.g., useAuth, useTheme, useTranslations)
   │ ├── lib/ # 辅助函数、工具库
   │ │ ├── i18n/ # 多语言配置文件和加载器
   │ │ │ ├── config.ts # i18n 配置 (支持的语言, 默认语言)
   │ │ │ ├── locales/ # 语言包目录
   │ │ │ │ ├── en.json
   │ │ │ │ └── zh.json
   │ │ │ └── middleware.ts # (可选) Next.js 中间件用于语言路由
   │ │ └── utils.ts # shadcn/ui 生成的，可添加自定义工具函数
   │ ├── services/ # API 调用服务
   │ │ └── apiClient.ts
   │ ├── store/ # Zustand 状态管理
   │ │ ├── **tests**/ # (可选) Zustand store 的测试
   │ │ ├── index.ts # Zustand store 主入口 (组合所有 slices)
   │ │ ├── slices/ # Zustand store 的不同切片 (slices)
   │ │ │ ├── **tests**/
   │ │ │ ├── authSlice.ts
   │ │ │ ├── chatSlice.ts
   │ │ │ ├── settingsSlice.ts # (例如用于主题和语言偏好)
   │ │ │ └── uiSlice.ts # (例如用于全局 UI 状态，如 Modal, Toast)
   │ │ └── types.ts # Zustand store 的类型定义
   │ ├── styles/ # (可选) 额外的全局样式
   │ ├── themes/ # 主题相关配置 (如果需要更复杂的 CSS 变量管理)
   │ │ └── index.ts # (可选) 主题变量定义
   │ └── types/ # 全局 TypeScript 类型定义
   │ ├── index.d.ts
   │ └── api.ts # API 响应/请求相关的类型
   ├── public/
   │ └── locales/ # (可选) 另一种存放语言包的方式, 如果 i18n 库需要从 public 加载
   ├── next.config.js
   ├── postcss.config.js
   ├── tailwind.config.ts
   ├── tsconfig.json
   └── package.json
   ├── README.md
   ├── .env.example
   ├── .env.local
   ├── .env.production
   ├── .env.staging
   ├── .gitignore
   ├── .prettierrc
   ├── .eslintrc.json
   ├── .dockerignore
   ├── Dockerfile
   ├── docker-compose.yml
   ├── package-lock.json
   ├── pnpm-lock.yaml

---

├── backend/ # FastAPI 后端应用
│ ├── app/ # 应用核心代码 (遵循 FastAPI 最佳实践)
│ │ ├── **init**.py
│ │ ├── main.py # FastAPI 应用实例创建和全局配置
│ │ ├── api/ # API 路由器和端点
│ │ │ ├── **init**.py
│ │ │ ├── deps.py # API 依赖项 (e.g., get_current_user)
│ │ │ └── v1/ # API 版本控制
│ │ │ ├── **init**.py
│ │ │ ├── endpoints/ # 各模块的端点
│ │ │ │ ├── **init**.py
│ │ │ │ ├── auth.py
│ │ │ │ ├── users.py
│ │ │ │ ├── chats.py
│ │ │ │ └── agents.py # AI 智能体交互相关
│ │ │ ├── payments.py # 处理支付、订阅、webhook
│ │ │ └── plugins.py # 插件管理/交互 (如果需要 API)

│ │ │ └── schemas.py # (可选) Pydantic schemas 总入口, 或分散到各模块
│ │ ├── core/ # 核心配置、安全等
│ │ │ ├── **init**.py
│ │ │ ├── config.py # 应用配置 (e.g., from .env)
│ │ │ └── security.py # 密码哈希、JWT 生成/验证
│ │ ├── crud/ # 数据库操作 (Create, Read, Update, Delete)
│ │ │ ├── **init**.py
│ │ │ ├── base.py # CRUD 基类 (可选)
│ │ │ ├── crud_user.py
│ │ │ └── crud_chat.py
│ │ ├── db/ # 数据库相关
│ │ │ ├── **init**.py
│ │ │ ├── session.py # 数据库会话管理 (SQLAlchemy/SQLModel session)
│ │ │ └── base.py # (可选) SQLAlchemy Base, or SQLModel base classes
│ │ ├── models/ # SQLModel/SQLAlchemy 数据模型 (表结构)
│ │ │ ├── **init**.py
│ │ │ ├── user.py
│ │ │ ├── chat.py
│ │ │ └── message.py
│ │ ├── schemas/ # Pydantic 数据模型 (用于 API 请求/响应验证)
│ │ │ ├── **init**.py
│ │ │ ├── user.py
│ │ │ ├── chat.py
│ │ │ ├── message.py
│ │ │ ├── token.py # JWT token schema
│ │ │ └── agent.py # AI Agent 相关 schema
│ │ ├── services/ # 业务逻辑服务层
│ │ │ ├── **init**.py
│ │ │ ├── agent_service.py # 封装 LangGraph/AI 逻辑调用
│ │ │ └── chat_service.py
│ │ ├── ai/ # LangChain/LangGraph 相关代码
│ │ │ ├── **init**.py
│ │ │ ├── agents/ # 不同智能体的定义
│ │ │ │ ├── **init**.py
│ │ │ │ ├── basic_responder.py
│ │ │ │ └── planner_agent.py
│ │ │ ├── chains/ # (如果使用独立的 LangChain chains)
│ │ │ ├── graphs/ # LangGraph 定义
│ │ │ │ ├── **init**.py
│ │ │ │ └── main_chat_graph.py
│ │ │ ├── tools/ # 自定义 LangChain 工具
│ │ │ ├── prompts/ # 提示模板
│ │ │ └── memory.py # 自定义记忆模块或配置
│ │ ├── websockets/ # WebSocket 相关逻辑
│ │ │ ├── **init**.py
│ │ │ └── chat_ws.py
│ │ ├── worker/ # ARQ 任务 worker 相关
│ │ │ ├── **init**.py
│ │ │ └── tasks.py # ARQ 任务定义
│ │ │ └── arq_config.py # ARQ worker 配置
│ │ └── tests/ # 测试代码
│ │ ├── **init**.py
│ │ ├── conftest.py # Pytest fixtures
│ │ └── api_v1/
│ │ └── test_users.py
│ ├── alembic/ # Alembic 数据库迁移工具目录 (如果使用 SQLAlchemy/SQLModel)
│ │ ├── versions/
│ │ ├── env.py
│ │ └── script.py.mako
│ ├── .env # 环境变量 (gitignored)
│ ├── .env.example # 环境变量示例
│ ├── .gitignore
│ ├── alembic.ini # Alembic 配置
│ ├── pyproject.toml # (推荐) 使用 PDM 或 Poetry 管理依赖
│ ├── README.md
│ └── Dockerfile # 后端 Dockerfile
│
├── docker-compose.yml # Docker Compose 配置文件
├── .gitignore # 主项目 gitignore
└── README.md # 主项目 README
Use code with caution.
目录结构说明 (后端 FastAPI):
app/: 包含所有应用代码。
main.py: 创建 FastAPI app 实例，挂载路由器，配置中间件等。
api/: 组织 API 端点。
deps.py: 可复用的依赖项，如获取当前用户。
v1/: API 版本控制。
endpoints/: 按模块组织路由，如 auth.py, users.py。
core/: 存放核心配置 (config.py 从 .env 读取环境变量) 和安全相关逻辑 (security.py)。
crud/: 数据库交互的底层函数 (CRUD 操作)。每个模型一个文件。
db/: 数据库会话管理 (session.py)。
models/: SQLModel/SQLAlchemy 数据模型定义 (对应数据库表)。
schemas/: Pydantic 模型，用于 API 的请求体、响应体验证和序列化。
services/: 业务逻辑层。API 端点应该保持精简，调用这里的服务函数来处理复杂逻辑。例如，agent_service.py 会封装与 LangGraph 的交互。
ai/: 专门存放所有 LangChain/LangGraph 相关的代码，包括智能体定义、图定义、工具、提示等。保持 AI 逻辑的独立性。
websockets/: 处理 WebSocket 连接和消息的逻辑。
worker/: ARQ 任务定义和 worker 配置。
tests/: 单元测试和集成测试。
alembic/: 如果使用 SQLAlchemy/SQLModel 并需要数据库迁移，Alembic 的目录。
.env: 存储敏感配置和环境变量，不提交到 git。
pyproject.toml: 使用 PDM 或 Poetry 进行依赖管理和项目构建。
目录结构说明 (前端 Next.js):
app/ (App Router):
(auth) 和 (main): 使用路由组来组织不同部分的页面布局和逻辑。
api/: Next.js 的 API Routes，如果需要一些前端特定的简单后端逻辑（如 NextAuth.js 集成），但主要 API 由 FastAPI 提供。
components/: 可复用的 React 组件。
ui/: 推荐使用像 shadcn/ui 这样的库来快速构建高质量 UI 组件，可以按需复制代码到这里。
contexts/: 全局状态管理，如认证状态、WebSocket 连接。
hooks/: 自定义 React Hooks。
lib/: 通用工具函数。
services/: 封装对 FastAPI 后端 API 的调用。 5. 初始化步骤与工具
版本控制: git init
依赖管理 (后端):
推荐使用 PDM 或 Poetry。
pdm init 或 poetry init
安装核心依赖: fastapi, uvicorn[standard], sqlmodel, psycopg2-binary (or asyncpg), redis, arq, langchain, langgraph, python-jose[cryptography] (for JWT), passlib[bcrypt] (for passwords), python-dotenv。
依赖管理 (前端):
npx create-next-app@latest frontend
进入 frontend 目录，安装额外依赖: axios (或使用 fetch), socket.io-client (如果选择 Socket.IO，否则原生 WebSocket), UI 库 (e.g., tailwindcss, shadcn-ui)。
数据库设置:
安装 PostgreSQL。
创建数据库和用户。
(如果使用 Alembic) alembic init alembic，并配置 env.py 和 alembic.ini。
缓存设置: 安装和运行 Redis。
环境变量: 创建 .env 文件 (后端) 和 .env.local (前端)，并从 .env.example 中复制内容并填写。
Docker: 编写 backend/Dockerfile 和根目录的 docker-compose.yml 文件，以便本地开发环境的容器化运行 (FastAPI, PostgreSQL, Redis)。
Pre-commit Hooks (可选但推荐): 使用 pre-commit 配合 black, flake8/ruff, isort, mypy 来保证代码质量和风格一致性。

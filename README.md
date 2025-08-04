项目初始化文档：[你的项目名称] AI 协作平台

1. 项目概述
   [你的项目名称] 是一个旨在通过人机协作和多智能体自主协作来完成复杂任务的 AI 平台。项目初期将专注于通过 @ 机制实现用户与多个 AI 智能体的动态交互，后续将发展为允许 AI 进行任务规划和自主协作执行的模式。

2. 产品设计理念：AI 社交化协作平台

   2.1 核心概念转换
   传统的 AI 工具往往以"功能"为导向，而本平台采用"社交化"的设计理念，将 AI Agent 包装为"虚拟联系人"，让用户像使用微信、Slack、Discord 一样自然地与 AI 进行交互。

   2.2 用户交互流程

   - **发现阶段**: 用户通过搜索功能发现和添加 AI Agent（表现为添加"联系人"）
   - **建立连接**: 每个 AI Agent 都有独特的"人设"、专业领域和交互风格
   - **对话交互**: 基于联系人的一对一对话，支持持续的上下文记忆
   - **群组协作**: 支持多个 AI Agent 参与的群聊模式，实现多智能体协作
   - **内容分享**: 通过"朋友圈"功能，AI Agent 可以分享知识、案例、工作成果

     2.3 界面布局设计（类微信/Slack 模式）

   **左侧主导航栏** (固定宽度 240px)

   ```
   ┌─────────────────────────────┐
   │ [用户头像] 用户名           │
   │ ─────────────────────────   │
   │ 📱 对话                     │
   │ 👥 联系人                   │
   │ 📁 文件                     │
   │ 🌟 朋友圈                   │
   │ 🔧 工具插件                 │
   │ ⚙️  设置                    │
   └─────────────────────────────┘
   ```

   **中间对话列表区** (可变宽度 300-400px)

   - **对话模式**: 显示最近对话列表，支持置顶、免打扰、删除
   - **联系人模式**: 分类显示 AI Agent（按专业领域分组）
   - **文件模式**: 显示共享文件、对话附件、知识库
   - **朋友圈模式**: 显示 AI Agent 的动态和内容分享
   - **工具插件模式**: 显示可用插件和工具库

   **右侧主内容区** (自适应宽度)

   - **聊天界面**: 对话气泡、输入框、工具栏
   - **联系人详情**: Agent 信息、能力介绍、历史对话
   - **文件预览**: 文档查看、编辑、协作
   - **朋友圈内容**: 动态详情、评论互动
   - **插件工作区**: 插件界面嵌入区域

     2.4 核心功能模块

   **智能联系人系统**

   - AI Agent 目录：按类别（编程、设计、分析、写作等）组织
   - 智能推荐：基于用户使用习惯推荐合适的 Agent
   - 自定义 Agent：用户可以训练和定制专属 AI 助手
   - 联系人关系：支持分组、标签、备注等管理功能

   **对话交互系统**

   - 持续记忆：每个联系人都有独立的对话历史和上下文
   - 多媒体支持：文本、图片、文件、代码块、图表等
   - 实时协作：支持多人（含 AI）同时参与的群聊
   - 智能提醒：重要消息提醒、任务进度通知

   **内容分享生态**

   - 朋友圈动态：AI Agent 分享专业见解、学习资源、工作案例
   - 知识沉淀：对话中的有价值内容自动整理为知识库
   - 内容协作：用户和 AI 共同创作文档、报告、方案

   **插件工具生态**

   - 工具市场：第三方开发者贡献的 AI 工具和插件
   - 一键集成：插件无缝集成到对话和工作流中
   - 自定义工作流：用户可以组合多个工具创建个人工作流

3. 核心目标
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
4. 精细化技术架构

   4.1 核心技术栈 (优化版)

   **前端技术栈**

   - 框架: Next.js 14+ (React 18+, App Router)
   - 状态管理: Zustand (轻量级，适合快速开发)
   - UI 组件: shadcn/ui + Tailwind CSS
   - 实时通信: Supabase Realtime + WebSocket
   - 类型安全: TypeScript 5+
   - 构建工具: Turbopack (Next.js 内置)

   **后端技术栈**

   - API 框架: FastAPI (Python 3.11+)
   - 数据库: Supabase (PostgreSQL 云服务) + 本地 PostgreSQL (开发环境)
   - ORM: SQLModel + Supabase Python SDK
   - 向量数据库: Supabase Vector (pgvector 扩展)
   - AI 框架: LangChain + LangGraph (Python)
   - 缓存: Supabase 缓存 + Redis (高频数据)
   - 任务队列: ARQ + Supabase Functions (边缘函数)
   - 实时功能: Supabase Realtime (替代传统 WebSocket)
   - 身份认证: Supabase Auth (支持多种 OAuth 提供商)

**技术架构**

```
graph TB
    subgraph "前端层 (Next.js 14)"
        A1["Next.js App Router<br/>TypeScript 5+"]
        A2["Supabase Auth<br/>实时订阅"]
        A3["shadcn/ui<br/>Tailwind CSS"]
        A4["Zustand<br/>状态管理"]
    end

    subgraph "API层 (FastAPI)"
        B1["FastAPI<br/>Python 3.11+"]
        B2["Supabase SDK<br/>SQLModel ORM"]
        B3["LangChain<br/>LangGraph"]
        B4["ARQ<br/>任务队列"]
    end

    subgraph "数据层"
        C1["Supabase PostgreSQL<br/>pgvector向量搜索"]
        C2["Supabase Storage<br/>文件存储"]
        C3["Supabase Realtime<br/>实时同步"]
        C4["Redis<br/>高频缓存"]
    end

    subgraph "支付层"
        D1["Creem.io<br/>起步阶段"]
        D2["Stripe<br/>扩展阶段"]
        D3["全球税务合规<br/>MoR服务"]
    end

    subgraph "AI层"
        E1["OpenAI GPT<br/>LLM服务"]
        E2["Embedding API<br/>向量化"]
        E3["LangChain Tools<br/>插件生态"]
    end

    subgraph "部署层"
        F1["Vercel<br/>前端部署"]
        F2["Railway/Render<br/>后端部署"]
        F3["Supabase Cloud<br/>数据库服务"]
    end

    A1 --> B1
    A2 --> C1
    A3 --> A1
    A4 --> A1

    B1 --> C1
    B2 --> C1
    B3 --> E1
    B4 --> C4

    B1 --> D1
    D1 -.-> D2

    E2 --> C1
    E3 --> B3

    A1 --> F1
    B1 --> F2
    C1 --> F3

    classDef frontend fill:#e3f2fd
    classDef api fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef payment fill:#fff3e0
    classDef ai fill:#fce4ec
    classDef deploy fill:#f1f8e9

    class A1,A2,A3,A4 frontend
    class B1,B2,B3,B4 api
    class C1,C2,C3,C4 data
    class D1,D2,D3 payment
    class E1,E2,E3 ai
    class F1,F2,F3 deploy
```

**支付与商业化**

- 起步阶段: Creem.io (AI 公司专用的金融 OS)
- 扩展阶段: Stripe (成熟后迁移)
- 税务合规: Creem.io 全球税务处理
- 订阅管理: Creem.io 内置订阅系统

**基础设施与部署**

- 云平台: Vercel (前端) + Supabase (后端服务)
- 容器化: Docker (开发环境) + Serverless (生产环境)
- CI/CD: GitHub Actions + Vercel 自动部署
- 监控: Supabase Analytics + Vercel Analytics
- 文件存储: Supabase Storage

  4.2 Supabase 集成优势

**开发效率提升**

- 🚀 即时 API 生成: 基于数据库表自动生成 RESTful API
- 🔐 内置身份认证: 支持邮箱、OAuth (Google, GitHub 等)
- ⚡ 实时数据同步: 无需手动配置 WebSocket
- 📁 文件存储: 内置对象存储，支持 CDN 加速
- 🔍 全文搜索: PostgreSQL 内置搜索功能

**AI 功能增强**

- 🧠 向量搜索: pgvector 扩展，支持 AI 语义搜索
- 📊 边缘函数: 支持在边缘运行 AI 推理
- 🔄 实时 AI 响应: 结合 Realtime 实现流式 AI 对话
- 💾 智能缓存: AI 响应结果的自动缓存

**成本控制**

- 💰 按需付费: 免费额度 + 使用量计费
- 🌍 全球部署: 多区域部署，降低延迟
- 📈 弹性扩展: 自动扩容，无需运维

  4.3 Creem.io 支付系统选择

**为什么选择 Creem.io 作为起步方案**

根据 [Creem.io](https://www.creem.io/) 的特性，这是专为 AI 初创公司设计的金融 OS：

**核心优势**

- 🏢 全球商户代理(MoR): 自动处理全球税务合规
- 💳 即时支付集成: 支持 100+国家的支付方式
- 🔒 内置风险控制: AI 驱动的欺诈检测
- 📊 实时分析: AI 驱动的业务洞察
- 🤝 专属支持: 为小团队提供专业指导

**适合 AI 初创的特性**

- 快速启动: 几分钟内完成支付集成
- 全球运营: 从第一天就支持国际化
- 成本优化: 相比传统方案节省 50%费用
- 合规简化: 无需处理复杂的税务申报

**后续 Stripe 迁移策略**

- 🎯 迁移时机: 月收入达到$50k+或用户规模达到 10k+
- 🔄 渐进式迁移: 新用户走 Stripe，老用户保持 Creem
- 📋 迁移计划:
  - 第一阶段: 双系统并行运行
  - 第二阶段: 数据迁移和用户沟通
  - 第三阶段: 完全切换到 Stripe

5. 数据库设计 (Supabase 优化版)

   5.1 Supabase 特性集成

   **Row Level Security (RLS)**

   - 用户只能访问自己的对话和联系人
   - AI Agent 根据可见性设置控制访问
   - 朋友圈动态基于关注关系控制可见性
   - 文件基于权限级别控制访问

   **实时订阅 (Realtime)**

   - 对话消息的实时推送
   - 在线状态的实时更新
   - 朋友圈动态的实时通知
   - 文件上传进度的实时反馈

   **全文搜索 (PostgreSQL FTS)**

   - Agent 搜索：基于名称、描述、能力标签
   - 消息搜索：对话历史的全文检索
   - 文件搜索：文件名和内容的搜索
   - 动态搜索：朋友圈内容的搜索

   **向量搜索 (pgvector)**

   - Agent 语义匹配：基于用户需求推荐合适的 Agent
   - 消息语义搜索：相似对话内容的检索
   - 知识库匹配：相关文档和资源的推荐

     5.2 核心实体关系 (Supabase Schema)

   **用户系统 (profiles) - 扩展 Supabase Auth**

   ```sql
   -- 基于 auth.users 的扩展表
   CREATE TABLE public.profiles (
     id UUID REFERENCES auth.users(id) PRIMARY KEY,
     username VARCHAR(50) UNIQUE NOT NULL,
     display_name VARCHAR(100),
     bio TEXT,
     avatar_url TEXT,
     status profile_status DEFAULT 'offline',
     settings JSONB DEFAULT '{}',
     plan_type subscription_plan DEFAULT 'free',
     trial_ends_at TIMESTAMPTZ,
     last_seen_at TIMESTAMPTZ DEFAULT NOW(),
     created_at TIMESTAMPTZ DEFAULT NOW(),
     updated_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- RLS策略
   ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
   CREATE POLICY "Users can view all profiles" ON profiles FOR SELECT USING (true);
   CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

   -- 实时订阅
   ALTER PUBLICATION supabase_realtime ADD TABLE profiles;

   -- 索引优化
   CREATE INDEX idx_profiles_username ON profiles(username);
   CREATE INDEX idx_profiles_status ON profiles(status);
   ```

   **AI Agent 实体 (ai_agents)**

   ```sql
   CREATE TABLE public.ai_agents (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     name VARCHAR(100) NOT NULL,
     avatar_url TEXT,
     description TEXT NOT NULL,
     category agent_category NOT NULL,
     capabilities JSONB DEFAULT '[]',
     personality JSONB DEFAULT '{}',
     model_config JSONB DEFAULT '{}',
     is_public BOOLEAN DEFAULT true,
     creator_id UUID REFERENCES auth.users(id),
     usage_count INTEGER DEFAULT 0,
     rating DECIMAL(2,1) DEFAULT 0.0,
     status agent_status DEFAULT 'active',
     -- 向量搜索字段
     description_embedding vector(1536),
     capabilities_text TEXT GENERATED ALWAYS AS (
       COALESCE((capabilities->>'text'), capabilities::text)
     ) STORED,
     search_text TEXT GENERATED ALWAYS AS (
       name || ' ' || description || ' ' ||
       COALESCE((capabilities->>'text'), capabilities::text)
     ) STORED,
     created_at TIMESTAMPTZ DEFAULT NOW(),
     updated_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- RLS策略
   ALTER TABLE ai_agents ENABLE ROW LEVEL SECURITY;
   CREATE POLICY "Anyone can view public agents" ON ai_agents FOR SELECT USING (is_public = true);
   CREATE POLICY "Users can view own agents" ON ai_agents FOR SELECT USING (creator_id = auth.uid());
   CREATE POLICY "Users can create agents" ON ai_agents FOR INSERT WITH CHECK (creator_id = auth.uid());
   CREATE POLICY "Users can update own agents" ON ai_agents FOR UPDATE USING (creator_id = auth.uid());

   -- 索引优化
   CREATE INDEX idx_ai_agents_category ON ai_agents(category);
   CREATE INDEX idx_ai_agents_status ON ai_agents(status, is_public);
   CREATE INDEX idx_ai_agents_rating ON ai_agents(rating DESC);
   CREATE INDEX idx_ai_agents_usage ON ai_agents(usage_count DESC);
   CREATE INDEX idx_ai_agents_search_text ON ai_agents USING gin(to_tsvector('english', search_text));
   CREATE INDEX idx_ai_agents_embedding ON ai_agents USING ivfflat (description_embedding vector_cosine_ops);
   ```

   **联系人关系 (Contact)**

   ```sql
   - id: UUID (主键)
   - user_id: UUID (用户ID)
   - agent_id: UUID (Agent ID)
   - alias: VARCHAR (备注名称)
   - group_name: VARCHAR (分组名称)
   - tags: JSONB (标签列表)
   - is_pinned: BOOLEAN (是否置顶)
   - is_muted: BOOLEAN (是否免打扰)
   - add_source: VARCHAR (添加来源：search, recommend, share等)
   - first_interaction_at: TIMESTAMP (首次交互时间)
   - last_interaction_at: TIMESTAMP (最后交互时间)
   - interaction_count: INTEGER (交互次数)
   - created_at: TIMESTAMP
   ```

   **对话会话 (Conversation)**

   ```sql
   - id: UUID (主键)
   - type: ENUM (direct, group) (直接对话/群聊)
   - title: VARCHAR (会话标题，群聊使用)
   - participants: JSONB (参与者列表: user_id + agent_ids)
   - last_message_id: UUID (最后一条消息ID)
   - last_activity_at: TIMESTAMP (最后活动时间)
   - is_pinned: BOOLEAN (是否置顶)
   - is_archived: BOOLEAN (是否归档)
   - settings: JSONB (会话设置：免打扰等)
   - created_by: UUID (创建者ID)
   - created_at, updated_at: TIMESTAMP
   ```

   **消息记录 (Message)**

   ```sql
   - id: UUID (主键)
   - conversation_id: UUID (所属会话)
   - sender_id: UUID (发送者ID，可能是user或agent)
   - sender_type: ENUM (user, agent)
   - content: TEXT (消息内容)
   - message_type: ENUM (text, image, file, code, system)
   - metadata: JSONB (附加信息：文件信息、代码语言等)
   - reply_to_id: UUID (回复的消息ID)
   - is_edited: BOOLEAN (是否已编辑)
   - edit_history: JSONB (编辑历史)
   - reactions: JSONB (表情反应)
   - read_by: JSONB (已读用户列表)
   - created_at, updated_at: TIMESTAMP
   ```

   **朋友圈动态 (Timeline)**

   ```sql
   - id: UUID (主键)
   - agent_id: UUID (发布Agent的ID)
   - content: TEXT (动态内容)
   - content_type: ENUM (article, tip, case_study, resource)
   - media_urls: JSONB (媒体文件链接)
   - tags: JSONB (话题标签)
   - visibility: ENUM (public, followers_only, private)
   - like_count: INTEGER (点赞数)
   - comment_count: INTEGER (评论数)
   - share_count: INTEGER (分享数)
   - is_featured: BOOLEAN (是否精选)
   - created_at, updated_at: TIMESTAMP
   ```

   **动态互动 (TimelineInteraction)**

   ```sql
   - id: UUID (主键)
   - timeline_id: UUID (动态ID)
   - user_id: UUID (用户ID)
   - interaction_type: ENUM (like, comment, share, bookmark)
   - content: TEXT (评论内容，如果是评论)
   - created_at: TIMESTAMP
   ```

   **文件管理 (File)**

   ```sql
   - id: UUID (主键)
   - filename: VARCHAR (文件名)
   - original_name: VARCHAR (原始文件名)
   - file_type: VARCHAR (文件类型)
   - file_size: BIGINT (文件大小)
   - storage_path: VARCHAR (存储路径)
   - uploader_id: UUID (上传者ID)
   - uploader_type: ENUM (user, agent)
   - conversation_id: UUID (关联会话ID，可选)
   - timeline_id: UUID (关联动态ID，可选)
   - access_level: ENUM (private, shared, public)
   - download_count: INTEGER (下载次数)
   - metadata: JSONB (文件元信息)
   - created_at: TIMESTAMP
   ```

   **插件工具 (Plugin)**

   ```sql
   - id: UUID (主键)
   - name: VARCHAR (插件名称)
   - description: TEXT (插件描述)
   - category: VARCHAR (插件分类)
   - icon_url: VARCHAR (插件图标)
   - developer: VARCHAR (开发者)
   - version: VARCHAR (版本号)
   - config_schema: JSONB (配置项模式)
   - capabilities: JSONB (插件能力描述)
   - api_endpoint: VARCHAR (插件API端点)
   - is_enabled: BOOLEAN (是否启用)
   - install_count: INTEGER (安装次数)
   - rating: DECIMAL (用户评分)
   - created_at, updated_at: TIMESTAMP
   ```

   **用户插件配置 (UserPlugin)**

   ```sql
   - id: UUID (主键)
   - user_id: UUID (用户ID)
   - plugin_id: UUID (插件ID)
   - config: JSONB (用户的插件配置)
   - is_active: BOOLEAN (是否激活)
   - installed_at: TIMESTAMP
   - last_used_at: TIMESTAMP
   ```

6. API 设计 (RESTful + WebSocket)

   6.1 核心 API 端点设计

   **身份认证 API**

   ```
   POST /api/v1/auth/register          # 用户注册
   POST /api/v1/auth/login             # 用户登录
   POST /api/v1/auth/logout            # 用户登出
   POST /api/v1/auth/refresh           # 刷新Token
   GET  /api/v1/auth/me                # 获取当前用户信息
   PUT  /api/v1/auth/profile           # 更新用户资料
   ```

   **AI Agent 管理 API**

   ```
   GET    /api/v1/agents               # 获取Agent目录
   GET    /api/v1/agents/:id           # 获取Agent详情
   POST   /api/v1/agents/search        # 搜索Agent
   GET    /api/v1/agents/categories    # 获取Agent分类
   GET    /api/v1/agents/recommended   # 获取推荐Agent
   POST   /api/v1/agents               # 创建自定义Agent (用户)
   PUT    /api/v1/agents/:id           # 更新自定义Agent
   DELETE /api/v1/agents/:id           # 删除自定义Agent
   ```

   **联系人管理 API**

   ```
   GET    /api/v1/contacts             # 获取联系人列表
   POST   /api/v1/contacts             # 添加联系人
   PUT    /api/v1/contacts/:id         # 更新联系人信息(备注、分组等)
   DELETE /api/v1/contacts/:id         # 删除联系人
   GET    /api/v1/contacts/groups      # 获取联系人分组
   POST   /api/v1/contacts/groups      # 创建分组
   ```

   **对话管理 API**

   ```
   GET    /api/v1/conversations        # 获取对话列表
   POST   /api/v1/conversations        # 创建新对话/群聊
   GET    /api/v1/conversations/:id    # 获取对话详情
   PUT    /api/v1/conversations/:id    # 更新对话设置
   DELETE /api/v1/conversations/:id    # 删除对话
   GET    /api/v1/conversations/:id/messages  # 获取消息历史
   POST   /api/v1/conversations/:id/messages  # 发送消息
   PUT    /api/v1/messages/:id         # 编辑消息
   DELETE /api/v1/messages/:id         # 删除消息
   POST   /api/v1/messages/:id/reactions # 添加表情反应
   ```

   **朋友圈 API**

   ```
   GET    /api/v1/timeline             # 获取朋友圈动态
   GET    /api/v1/timeline/:id         # 获取动态详情
   POST   /api/v1/timeline/:id/like    # 点赞动态
   POST   /api/v1/timeline/:id/comment # 评论动态
   POST   /api/v1/timeline/:id/share   # 分享动态
   GET    /api/v1/agents/:id/timeline  # 获取特定Agent的动态
   ```

   **文件管理 API**

   ```
   GET    /api/v1/files                # 获取文件列表
   POST   /api/v1/files/upload         # 上传文件
   GET    /api/v1/files/:id            # 获取文件详情
   GET    /api/v1/files/:id/download   # 下载文件
   DELETE /api/v1/files/:id            # 删除文件
   GET    /api/v1/files/shared         # 获取共享文件
   ```

   **插件工具 API**

   ```
   GET    /api/v1/plugins              # 获取插件市场
   GET    /api/v1/plugins/:id          # 获取插件详情
   POST   /api/v1/plugins/:id/install  # 安装插件
   DELETE /api/v1/plugins/:id/uninstall # 卸载插件
   GET    /api/v1/plugins/installed    # 获取已安装插件
   PUT    /api/v1/plugins/:id/config   # 配置插件
   POST   /api/v1/plugins/:id/execute  # 执行插件功能
   ```

   6.2 WebSocket 实时通信

   ```
   /ws/chat/:conversation_id           # 对话实时消息
   /ws/presence                        # 在线状态同步
   /ws/notifications                   # 系统通知推送
   ```

7. 前端组件架构设计

   7.1 路由结构 (Next.js App Router)

   ```
   app/
   ├── (auth)/
   │   ├── login/page.tsx
   │   └── register/page.tsx
   ├── (main)/
   │   ├── layout.tsx                  # 主布局(三栏布局)
   │   ├── page.tsx                    # 默认重定向到对话
   │   ├── chat/
   │   │   ├── page.tsx                # 对话列表页
   │   │   └── [conversationId]/
   │   │       └── page.tsx            # 具体对话页
   │   ├── contacts/
   │   │   ├── page.tsx                # 联系人列表页
   │   │   ├── search/page.tsx         # Agent搜索页
   │   │   └── [agentId]/page.tsx      # Agent详情页
   │   ├── files/
   │   │   ├── page.tsx                # 文件管理页
   │   │   └── [fileId]/page.tsx       # 文件详情页
   │   ├── timeline/
   │   │   ├── page.tsx                # 朋友圈主页
   │   │   └── [postId]/page.tsx       # 动态详情页
   │   └── plugins/
   │       ├── page.tsx                # 插件工具页
   │       └── [pluginId]/page.tsx     # 插件详情页
   └── api/                            # NextAuth等前端API
   ```

   7.2 核心组件设计

   ```
   components/
   ├── layout/
   │   ├── MainLayout.tsx              # 三栏主布局
   │   ├── Sidebar.tsx                 # 左侧导航栏
   │   ├── MiddlePanel.tsx             # 中间列表面板
   │   ├── ContentArea.tsx             # 右侧内容区域
   │   └── TopBar.tsx                  # 顶部状态栏
   ├── chat/
   │   ├── ConversationList.tsx        # 对话列表
   │   ├── ConversationItem.tsx        # 对话项
   │   ├── ChatInterface.tsx           # 聊天界面
   │   ├── MessageBubble.tsx           # 消息气泡
   │   ├── MessageInput.tsx            # 消息输入框
   │   ├── MessageList.tsx             # 消息列表
   │   └── TypingIndicator.tsx         # 输入状态指示
   ├── contacts/
   │   ├── ContactList.tsx             # 联系人列表
   │   ├── ContactItem.tsx             # 联系人项
   │   ├── AgentCard.tsx               # Agent卡片
   │   ├── AgentSearch.tsx             # Agent搜索
   │   ├── AgentDetail.tsx             # Agent详情
   │   └── ContactGroups.tsx           # 联系人分组
   ├── timeline/
   │   ├── TimelineFeed.tsx            # 朋友圈信息流
   │   ├── TimelinePost.tsx            # 动态帖子
   │   ├── PostInteractions.tsx        # 帖子互动(点赞评论)
   │   └── CommentSection.tsx          # 评论区域
   ├── files/
   │   ├── FileExplorer.tsx            # 文件浏览器
   │   ├── FileItem.tsx                # 文件项
   │   ├── FileUpload.tsx              # 文件上传
   │   └── FilePreview.tsx             # 文件预览
   ├── plugins/
   │   ├── PluginMarket.tsx            # 插件市场
   │   ├── PluginCard.tsx              # 插件卡片
   │   ├── PluginConfig.tsx            # 插件配置
   │   └── PluginInterface.tsx         # 插件界面容器
   └── common/
       ├── Avatar.tsx                  # 头像组件
       ├── StatusIndicator.tsx         # 状态指示器
       ├── SearchBox.tsx               # 搜索框
       ├── NotificationBadge.tsx       # 通知徽章
       └── LoadingSpinner.tsx          # 加载动画
   ```

8. 详细 Layout 设计概念

   8.1 响应式三栏布局

   ```
   ┌─────────────────────────────────────────────────────────────────────────┐
   │                           顶部状态栏 (可选)                              │
   ├───────────┬─────────────────────────┬─────────────────────────────────────┤
   │           │                         │                                     │
   │  左侧导航  │      中间列表面板        │         右侧主内容区                 │
   │  (60-120px)  │     (300-400px)         │        (自适应宽度)                  │
   │           │                         │                                     │
   │ 👤 用户    │ 🔍 搜索框              │ 💬 聊天界面                         │
   │ ─────────  │ ─────────────────────   │ ───────────────────────────────────  │
   │ 💬 对话    │ 📋 内容列表            │ 📝 消息区域                         │
   │ 👥 联系人  │   • 对话项             │   • 消息气泡                        │
   │ 📁 文件    │   • 联系人项           │   • 时间戳                          │
   │ 🌟 朋友圈  │   • 文件项             │   • 已读状态                        │
   │ 🔧 插件    │   • 动态项             │ ─────────────────────────────────── │
   │ ⚙️ 设置    │                         │ ⌨️ 输入区域                         │
   │           │                         │   • 文本输入框                       │
   │           │                         │   • 工具栏 (文件/表情/插件)          │
   └───────────┴─────────────────────────┴─────────────────────────────────────┘
   ```

   8.2 交互模式切换

   **对话模式** (默认)

   - 左侧: 高亮"对话"导航
   - 中间: 显示对话列表，支持搜索和筛选
   - 右侧: 选中对话的聊天界面
   - 特性: 实时消息推送，输入状态指示，消息已读/未读

   **联系人模式**

   - 左侧: 高亮"联系人"导航
   - 中间: 按分组显示 AI Agent，支持搜索发现
   - 右侧: Agent 详情页或搜索结果
   - 特性: Agent 能力展示，快速开始对话，添加到联系人

   **文件模式**

   - 左侧: 高亮"文件"导航
   - 中间: 文件分类浏览 (最近/共享/类型)
   - 右侧: 文件预览或文件管理界面
   - 特性: 拖拽上传，在线预览，协作编辑

   **朋友圈模式**

   - 左侧: 高亮"朋友圈"导航
   - 中间: 动态信息流，按时间或热度排序
   - 右侧: 动态详情和评论互动
   - 特性: 类似社交媒体的内容浏览体验

   **插件模式**

   - 左侧: 高亮"工具插件"导航
   - 中间: 插件市场或已安装插件列表
   - 右侧: 插件详情或插件工作界面
   - 特性: 插件嵌入，配置管理，工具集成

     8.3 移动端适配策略

   ```
   手机端 (< 768px):
   ┌─────────────────────┐
   │ 🍔 ≡  标题    🔍 ⚙️ │ 顶部导航栏
   ├─────────────────────┤
   │                     │
   │    单栏内容区域      │ 全屏显示当前页面
   │                     │ 底部Tab导航切换
   │                     │
   ├─────────────────────┤
   │ 💬 👥 📁 🌟 🔧    │ 底部导航栏
   └─────────────────────┘

   平板端 (768px - 1024px):
   ┌──────────────┬──────────────────────┐
   │              │                      │
   │   侧边栏     │      主内容区         │ 双栏布局
   │  (可收起)     │                      │ 侧边栏可折叠
   │              │                      │
   └──────────────┴──────────────────────┘
   ```

   8.4 用户体验设计要点

   **视觉一致性**

   - 统一的颜色系统: 主色调 + 功能色 + 中性色
   - 图标风格统一: 线性图标 + 适当的填充图标
   - 字体层级清晰: 标题/正文/辅助文字的字重和大小
   - 圆角和阴影: 现代化的卡片设计和微交互

   **交互反馈**

   - 悬停状态: 按钮和链接的 hover 效果
   - 加载状态: 骨架屏 + 进度指示器
   - 错误处理: 友好的错误提示和重试机制
   - 成功反馈: Toast 通知 + 状态更新

   **性能优化**

   - 虚拟滚动: 长列表的性能优化
   - 懒加载: 图片和组件的按需加载
   - 缓存策略: 对话历史和用户数据的本地缓存
   - 预加载: 用户可能访问的内容提前加载

   **无障碍访问**

   - 键盘导航: 全功能的键盘快捷键支持
   - 屏幕阅读: 语义化 HTML 和 ARIA 标签
   - 颜色对比: 满足 WCAG 标准的对比度
   - 字体缩放: 支持用户的字体大小偏好

9. 核心功能实现策略

   9.1 Agent 搜索与发现

   - 基于语义搜索的 Agent 匹配算法
   - 标签和分类的多维度筛选
   - 基于用户行为的个性化推荐
   - 社区评分和使用统计

     9.2 对话上下文管理

   - 基于对话 ID 的独立上下文存储
   - 长期记忆与短期记忆的平衡
   - 跨会话的知识共享机制
   - 上下文压缩和检索优化

     9.3 实时协作体验

   - WebSocket 连接的稳定性保证
   - 断线重连和消息同步机制
   - 多设备同步的状态管理
   - 冲突解决和版本控制

     9.4 内容生态建设

   - Agent 生成内容的质量控制
   - 用户反馈和内容评价系统
   - 知识库的自动构建和更新
   - 版权和内容安全管理

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

10. 技术栈集成配置

    10.1 Supabase 集成配置

    **环境变量配置**

```env
# Supabase配置
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 数据库配置
DATABASE_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres
DIRECT_URL=postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres

# AI配置
OPENAI_API_KEY=your-openai-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langchain-key
```

**前端集成 (Next.js)**

```typescript
// lib/supabase/client.ts
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import { Database } from "@/types/supabase";

export const supabase = createClientComponentClient<Database>();

// lib/supabase/server.ts
import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";

export const createServerSupabaseClient = () =>
  createServerComponentClient({ cookies });
```

**后端集成 (FastAPI)**

```python
# app/core/supabase.py
from supabase import create_client, Client
from app.core.config import settings

supabase: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

# 实时订阅示例
def setup_realtime_subscriptions():
    def on_message_insert(payload):
        # 处理新消息推送
        pass

    supabase.table('messages') \
        .on('INSERT', on_message_insert) \
        .subscribe()
```

**RLS 策略示例**

```sql
-- 对话消息的RLS策略
CREATE POLICY "Users can view own conversation messages"
ON messages FOR SELECT
USING (
  conversation_id IN (
    SELECT id FROM conversations
    WHERE auth.uid() = ANY(participants::uuid[])
  )
);
```

10.2 Creem.io 支付集成

**SDK 安装和配置**

```bash
# Python后端
pip install creem-python-sdk

# Node.js前端 (如果需要)
npm install @creem/checkout-js
```

**后端集成示例**

```python
# app/services/payment_service.py
from creem import CreemClient
from app.core.config import settings

creem_client = CreemClient(
    api_key=settings.CREEM_API_KEY,
    environment="sandbox"  # 或 "production"
)

async def create_subscription(user_id: str, plan_id: str):
    """创建订阅"""
    try:
        subscription = await creem_client.subscriptions.create({
            "customer_id": user_id,
            "plan_id": plan_id,
            "trial_days": 14,
            "success_url": f"{settings.FRONTEND_URL}/success",
            "cancel_url": f"{settings.FRONTEND_URL}/cancel"
        })
        return subscription
    except Exception as e:
        logger.error(f"Failed to create subscription: {e}")
        raise

async def handle_webhook(payload: dict, signature: str):
    """处理Creem.io Webhook"""
    if not creem_client.webhooks.verify(payload, signature):
        raise ValueError("Invalid webhook signature")

    event_type = payload.get("type")
    data = payload.get("data")

    if event_type == "subscription.created":
        await update_user_subscription(data["customer_id"], data)
    elif event_type == "subscription.cancelled":
        await cancel_user_subscription(data["customer_id"])
```

**前端支付流程**

```typescript
// components/payment/SubscriptionButton.tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";

export function SubscriptionButton({ planId }: { planId: string }) {
  const [loading, setLoading] = useState(false);

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/v1/payments/create-subscription", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ planId }),
      });

      const { checkout_url } = await response.json();
      window.location.href = checkout_url;
    } catch (error) {
      console.error("Subscription failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button onClick={handleSubscribe} disabled={loading}>
      {loading ? "处理中..." : "升级套餐"}
    </Button>
  );
}
```

10.3 优化的项目结构

**前端结构 (适配 60-120px 窄边栏)**

```
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (main)/
│   │   │   ├── layout.tsx              # 三栏布局 (窄边栏设计)
│   │   │   ├── chat/
│   │   │   │   ├── page.tsx            # 对话列表
│   │   │   │   └── [id]/page.tsx       # 对话详情
│   │   │   ├── contacts/
│   │   │   │   ├── page.tsx            # 联系人/Agent列表
│   │   │   │   ├── search/page.tsx     # Agent搜索
│   │   │   │   └── [id]/page.tsx       # Agent详情
│   │   │   ├── files/page.tsx          # 文件管理
│   │   │   ├── timeline/page.tsx       # 朋友圈
│   │   │   └── plugins/page.tsx        # 插件工具
│   │   └── api/
│   │       ├── auth/[...nextauth].ts   # NextAuth集成Supabase
│   │       └── webhooks/
│   │           └── creem.ts           # Creem.io webhook处理
│   ├── components/
│   │   ├── layout/
│   │   │   ├── CompactSidebar.tsx     # 60-120px窄边栏
│   │   │   ├── ExpandableNav.tsx      # 可展开导航
│   │   │   ├── MiddlePanel.tsx        # 中间面板
│   │   │   └── ContentArea.tsx        # 内容区域
│   │   ├── chat/
│   │   │   ├── RealtimeChat.tsx       # Supabase实时聊天
│   │   │   ├── MessageStream.tsx      # AI流式响应
│   │   │   └── TypingIndicator.tsx    # 输入状态
│   │   ├── contacts/
│   │   │   ├── AgentSearch.tsx        # 向量搜索UI
│   │   │   ├── AgentRecommend.tsx     # AI推荐
│   │   │   └── ContactManager.tsx     # 联系人管理
│   │   └── payment/
│   │       ├── SubscriptionCard.tsx   # 订阅卡片
│   │       └── BillingHistory.tsx     # 账单历史
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts              # Supabase客户端
│   │   │   ├── server.ts              # 服务端客户端
│   │   │   └── types.ts               # 数据库类型
│   │   ├── payment/
│   │   │   └── creem.ts               # Creem.io客户端
│   │   └── ai/
│   │       ├── embeddings.ts          # 向量嵌入
│   │       └── streaming.ts           # 流式响应
│   └── types/
│       ├── supabase.ts                # 自动生成的类型
│       ├── payment.ts                 # 支付相关类型
│       └── ai.ts                      # AI相关类型
```

**后端结构 (Supabase + FastAPI)**

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── auth.py                    # Supabase Auth集成
│   │   ├── agents.py                  # AI Agent管理
│   │   ├── chat.py                    # 聊天API
│   │   ├── payments.py                # Creem.io集成
│   │   └── webhooks.py                # Webhook处理
│   ├── core/
│   │   ├── supabase.py                # Supabase配置
│   │   ├── payment.py                 # Creem.io配置
│   │   └── ai.py                      # AI服务配置
│   ├── services/
│   │   ├── agent_service.py           # Agent业务逻辑
│   │   ├── chat_service.py            # 聊天服务
│   │   ├── payment_service.py         # 支付服务
│   │   └── embedding_service.py       # 向量嵌入服务
│   ├── ai/
│   │   ├── agents/                    # LangGraph智能体
│   │   ├── tools/                     # LangChain工具
│   │   └── memory/                    # 记忆管理
│   └── workers/
│       ├── embedding_worker.py        # 向量化任务
│       └── notification_worker.py     # 通知任务
├── supabase/
│   ├── migrations/                    # 数据库迁移
│   ├── functions/                     # Edge Functions
│   └── seed.sql                       # 初始数据
└── docker-compose.yml                 # 本地开发环境
```

10.4 开发工作流

**本地开发环境启动**

```bash
# 1. 启动Supabase本地环境
npx supabase start

# 2. 运行数据库迁移
npx supabase db reset

# 3. 启动前端开发服务器
cd frontend && npm run dev

# 4. 启动后端API服务器
cd backend && uvicorn app.main:app --reload

# 5. 启动AI服务worker
cd backend && arq app.workers.WorkerSettings
```

**部署流程**

```bash
# 1. 部署Supabase生产环境
npx supabase link --project-ref your-project-ref
npx supabase db push

# 2. 部署前端到Vercel
vercel --prod

# 3. 部署后端API (可选择云平台)
# Railway, Render, 或其他支持Python的平台
```

11. 性能优化策略

    11.1 数据库优化

- 使用 Supabase 的连接池和缓存
- 针对高频查询创建物化视图
- 使用 pgvector 的 HNSW 索引优化向量搜索
- 实施数据分区策略（按时间分区消息表）

  11.2 实时性能优化

- 使用 Supabase Realtime 的频道订阅
- 实施智能的订阅范围限制
- 客户端状态管理优化（React Query + Zustand）

  11.3 AI 响应优化

- 流式响应降低首次响应时间
- 智能缓存常见 AI 回复
- 使用边缘函数处理简单 AI 任务
- 实施 AI 响应的预取策略

  11.4 成本控制

- Supabase 使用量监控和告警
- AI API 调用的智能限流
- Creem.io 的费用追踪和优化
- 实施用户套餐的使用量限制

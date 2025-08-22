# 基于业务流程的LangGraph架构重新设计

## 📋 业务流程澄清

### 核心业务流程
```
Agent市场浏览 → 添加为Contact → 创建Conversation → 邀请更多Agents → 多Agent协作
```

### 数据模型层次关系
1. **agents表** - 智能体定义/模板（Agent市场中的商品）
2. **contacts表** - 用户添加的智能体实例（个人化配置）
3. **conversations表** - 对话室
4. **conversation_participants表** - 对话参与者（多个contacts）
5. **LangGraph工作流** - 基于对话参与者动态创建

## 🏗️ 重新设计的数据架构

### 1. 核心数据模型关系

```sql
-- Agent定义表 (市场中的智能体模板)
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,              -- 智能体唯一标识
    display_name VARCHAR(255) NOT NULL,             -- 展示名称
    description TEXT,                               -- 描述
    creator_id UUID REFERENCES users(id),           -- 创建者
    
    -- 智能体能力定义
    system_prompt TEXT NOT NULL,                    -- 系统提示词
    personality_config JSONB DEFAULT '{}',          -- 性格配置
    model_preferences JSONB DEFAULT '{}',           -- 模型偏好
    available_tools JSONB DEFAULT '[]',             -- 可用工具列表
    capabilities JSONB DEFAULT '[]',                -- 能力标签
    
    -- 市场属性
    category VARCHAR(100),                          -- 分类
    tags JSONB DEFAULT '[]',                        -- 标签
    is_public BOOLEAN DEFAULT true,                 -- 是否公开
    is_verified BOOLEAN DEFAULT false,              -- 是否认证
    price_tier VARCHAR(50) DEFAULT 'free',          -- 价格层级
    
    -- LangGraph节点定义
    node_type VARCHAR(50) DEFAULT 'agent',          -- 节点类型
    node_config JSONB DEFAULT '{}',                 -- 节点配置
    execution_timeout INTEGER DEFAULT 300,         -- 执行超时（秒）
    max_concurrent_instances INTEGER DEFAULT 10,    -- 最大并发实例
    
    -- 统计信息
    download_count INTEGER DEFAULT 0,              -- 下载次数
    rating_average DECIMAL(3,2) DEFAULT 0.0,       -- 平均评分
    usage_count INTEGER DEFAULT 0,                 -- 使用次数
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Contact表 (用户个人的智能体实例)
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    agent_id UUID REFERENCES agents(id) NOT NULL,
    
    -- 个人化配置
    custom_name VARCHAR(255),                       -- 用户自定义名称
    custom_avatar_url VARCHAR(500),                 -- 自定义头像
    custom_system_prompt TEXT,                      -- 自定义系统提示
    custom_personality JSONB DEFAULT '{}',          -- 自定义性格
    custom_tools JSONB DEFAULT '[]',                -- 自定义工具配置
    
    -- Contact实例配置
    is_favorite BOOLEAN DEFAULT false,              -- 是否收藏
    conversation_style VARCHAR(100),                -- 对话风格偏好
    memory_retention_days INTEGER DEFAULT 30,       -- 记忆保留天数
    interaction_frequency VARCHAR(50) DEFAULT 'normal', -- 互动频率
    
    -- LangGraph实例配置
    instance_config JSONB DEFAULT '{}',             -- 实例特定配置
    resource_limits JSONB DEFAULT '{}',             -- 资源限制
    permissions JSONB DEFAULT '[]',                 -- 权限设置
    
    -- 关系状态
    status VARCHAR(50) DEFAULT 'active',            -- active/inactive/archived
    added_at TIMESTAMP DEFAULT NOW(),
    last_interaction_at TIMESTAMP,
    
    UNIQUE(user_id, agent_id)                       -- 用户不能重复添加同一个agent
);

-- Conversation参与者表 (对话室中的智能体实例)
CREATE TABLE conversation_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) NOT NULL,
    contact_id UUID REFERENCES contacts(id) NOT NULL,        -- 引用具体的contact实例
    user_id UUID REFERENCES users(id) NOT NULL,              -- 冗余字段，方便查询
    
    -- 参与配置
    role VARCHAR(50) DEFAULT 'participant',                  -- participant/moderator/observer
    join_type VARCHAR(50) DEFAULT 'invited',                 -- invited/mentioned/auto
    
    -- 对话中的特殊配置
    conversation_permissions JSONB DEFAULT '[]',             -- 该对话中的权限
    notification_settings JSONB DEFAULT '{}',               -- 通知设置
    
    -- LangGraph工作流中的角色
    workflow_priority INTEGER DEFAULT 50,                    -- 工作流中的优先级(1-100)
    max_response_length INTEGER,                             -- 最大响应长度
    response_delay_ms INTEGER DEFAULT 0,                     -- 响应延迟
    
    joined_at TIMESTAMP DEFAULT NOW(),
    left_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- LangGraph工作流执行表
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) NOT NULL,
    trigger_message_id UUID REFERENCES messages(id),         -- 触发消息
    
    -- 工作流配置
    workflow_type VARCHAR(100) NOT NULL,                     -- mention_routing/group_discussion/sequential etc.
    participant_contacts JSONB NOT NULL,                     -- 参与的contact IDs
    routing_strategy VARCHAR(100) DEFAULT 'auto',            -- auto/parallel/sequential/consensus
    
    -- 执行状态
    status VARCHAR(50) DEFAULT 'running',                    -- running/completed/failed/timeout
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_duration_ms INTEGER,
    
    -- 结果数据
    input_data JSONB NOT NULL,                               -- 输入数据
    output_data JSONB,                                       -- 输出数据
    execution_path JSONB DEFAULT '[]',                       -- 执行路径追踪
    error_details JSONB,                                     -- 错误详情
    
    -- 成本统计
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    
    metadata JSONB DEFAULT '{}'
);

-- 节点执行记录表
CREATE TABLE node_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_execution_id UUID REFERENCES workflow_executions(id) NOT NULL,
    contact_id UUID REFERENCES contacts(id) NOT NULL,        -- 执行节点的contact
    
    -- 节点信息
    node_id VARCHAR(100) NOT NULL,                          -- LangGraph中的节点ID
    node_type VARCHAR(50) NOT NULL,                         -- agent/tool/decision/aggregator
    execution_order INTEGER,                                -- 执行顺序
    
    -- 执行数据
    input_state JSONB,                                      -- 输入状态
    output_state JSONB,                                     -- 输出状态
    
    -- 执行状态
    status VARCHAR(50) DEFAULT 'pending',                   -- pending/running/completed/failed
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    
    -- 模型调用信息
    model_used VARCHAR(100),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0.0,
    
    -- 错误处理
    error_message TEXT,
    error_type VARCHAR(100),
    
    metadata JSONB DEFAULT '{}'
);

-- 工具执行记录表  
CREATE TABLE tool_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_execution_id UUID REFERENCES node_executions(id) NOT NULL,
    
    -- 工具信息
    tool_name VARCHAR(100) NOT NULL,
    tool_function VARCHAR(100) NOT NULL,
    
    -- 执行数据
    input_parameters JSONB,
    output_result JSONB,
    
    -- 执行状态
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    
    -- 错误信息
    error_message TEXT,
    error_type VARCHAR(100),
    
    metadata JSONB DEFAULT '{}'
);

-- 对话记忆关联表
CREATE TABLE conversation_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) NOT NULL,
    contact_id UUID REFERENCES contacts(id),                -- 哪个contact的记忆，NULL表示共享记忆
    
    -- 记忆分类
    memory_type VARCHAR(50) NOT NULL,                       -- individual/shared/contextual
    memory_category VARCHAR(100),                           -- preference/knowledge/pattern/entity
    
    -- 记忆内容
    content TEXT NOT NULL,
    summary TEXT,                                           -- 记忆摘要
    keywords JSONB DEFAULT '[]',                            -- 关键词
    
    -- 记忆属性
    importance_score DECIMAL(3,2) DEFAULT 0.5,             -- 重要性评分 0-1
    confidence_score DECIMAL(3,2) DEFAULT 1.0,             -- 置信度评分 0-1
    access_frequency INTEGER DEFAULT 0,                    -- 访问频率
    
    -- 时效性
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,                                   -- 过期时间
    last_accessed_at TIMESTAMP DEFAULT NOW(),
    
    -- 元数据
    source_message_id UUID REFERENCES messages(id),        -- 来源消息
    extraction_method VARCHAR(100),                        -- 提取方法
    metadata JSONB DEFAULT '{}'
);
```

### 2. 索引优化策略

```sql
-- 性能优化索引
CREATE INDEX idx_contacts_user_agent ON contacts(user_id, agent_id);
CREATE INDEX idx_conversation_participants_conversation ON conversation_participants(conversation_id);
CREATE INDEX idx_conversation_participants_contact ON conversation_participants(contact_id);
CREATE INDEX idx_workflow_executions_conversation ON workflow_executions(conversation_id);
CREATE INDEX idx_node_executions_workflow ON node_executions(workflow_execution_id);
CREATE INDEX idx_node_executions_contact ON node_executions(contact_id);
CREATE INDEX idx_conversation_memories_conversation ON conversation_memories(conversation_id);
CREATE INDEX idx_conversation_memories_contact ON conversation_memories(contact_id);

-- 复合索引
CREATE INDEX idx_contacts_user_status ON contacts(user_id, status);
CREATE INDEX idx_participants_conversation_active ON conversation_participants(conversation_id, is_active);
CREATE INDEX idx_memories_conversation_type ON conversation_memories(conversation_id, memory_type);
```

## 🔄 LangGraph节点管理重新设计

### 1. 节点类型定义

```python
from enum import Enum

class LangGraphNodeType(str, Enum):
    """LangGraph节点类型"""
    AGENT = "agent"                    # 智能体节点
    ROUTER = "router"                  # 路由节点  
    AGGREGATOR = "aggregator"          # 聚合节点
    DECISION = "decision"              # 决策节点
    TOOL_EXECUTOR = "tool_executor"    # 工具执行节点
    MEMORY_RETRIEVER = "memory_retriever"  # 记忆检索节点
    VALIDATOR = "validator"            # 验证节点

class WorkflowType(str, Enum):
    """工作流类型"""
    SINGLE_AGENT = "single_agent"              # 单智能体对话
    MENTION_ROUTING = "mention_routing"         # @mention路由
    PARALLEL_DISCUSSION = "parallel_discussion" # 并行讨论
    SEQUENTIAL_PROCESSING = "sequential_processing" # 顺序处理
    CONSENSUS_BUILDING = "consensus_building"   # 共识构建
    DEBATE_MODE = "debate_mode"                # 辩论模式
    BRAINSTORMING = "brainstorming"            # 头脑风暴
```

### 2. 动态工作流构建器

```python
class DynamicWorkflowBuilder:
    """基于对话参与者动态构建LangGraph工作流"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def build_workflow_for_conversation(
        self, 
        conversation_id: UUID,
        trigger_message: str
    ) -> LangGraphWorkflow:
        """为特定对话构建工作流"""
        
        # 1. 获取对话参与者
        participants = await self._get_active_participants(conversation_id)
        
        # 2. 分析消息，确定工作流类型
        workflow_type = await self._analyze_workflow_type(trigger_message, participants)
        
        # 3. 根据参与者和工作流类型构建图
        if workflow_type == WorkflowType.MENTION_ROUTING:
            return await self._build_mention_routing_workflow(trigger_message, participants)
        elif workflow_type == WorkflowType.PARALLEL_DISCUSSION:
            return await self._build_parallel_discussion_workflow(participants)
        elif workflow_type == WorkflowType.SEQUENTIAL_PROCESSING:
            return await self._build_sequential_workflow(participants)
        else:
            return await self._build_default_workflow(participants)
    
    async def _get_active_participants(self, conversation_id: UUID) -> List[ContactInstance]:
        """获取对话中的活跃参与者"""
        query = """
        SELECT 
            cp.*,
            c.agent_id,
            c.custom_name,
            c.custom_system_prompt,
            c.instance_config,
            a.name as agent_name,
            a.display_name,
            a.system_prompt,
            a.model_preferences,
            a.node_config
        FROM conversation_participants cp
        JOIN contacts c ON cp.contact_id = c.id
        JOIN agents a ON c.agent_id = a.id
        WHERE cp.conversation_id = :conversation_id 
        AND cp.is_active = true
        ORDER BY cp.workflow_priority DESC
        """
        
        result = await self.db_session.execute(
            text(query), 
            {"conversation_id": conversation_id}
        )
        
        return [ContactInstance(**row) for row in result.fetchall()]
    
    async def _build_mention_routing_workflow(
        self, 
        message: str, 
        participants: List[ContactInstance]
    ) -> LangGraphWorkflow:
        """构建@mention路由工作流"""
        
        from langgraph import StateGraph
        from .states import ConversationState
        
        workflow = StateGraph(ConversationState)
        
        # 添加路由节点
        workflow.add_node("mention_router", self._create_mention_router(message))
        
        # 为每个参与者添加智能体节点
        mentioned_agents = self._extract_mentions(message)
        for participant in participants:
            if participant.agent_name in mentioned_agents:
                workflow.add_node(
                    f"agent_{participant.contact_id}",
                    self._create_agent_node(participant)
                )
        
        # 添加聚合节点
        workflow.add_node("response_aggregator", self._create_response_aggregator())
        
        # 定义路由逻辑
        workflow.add_conditional_edges(
            "mention_router",
            self._route_to_mentioned_agents,
            {f"agent_{p.contact_id}": f"agent_{p.contact_id}" 
             for p in participants if p.agent_name in mentioned_agents}
        )
        
        # 聚合响应
        for participant in participants:
            if participant.agent_name in mentioned_agents:
                workflow.add_edge(f"agent_{participant.contact_id}", "response_aggregator")
        
        workflow.set_entry_point("mention_router")
        workflow.add_edge("response_aggregator", "__end__")
        
        return workflow.compile()
    
    async def _build_parallel_discussion_workflow(
        self, 
        participants: List[ContactInstance]
    ) -> LangGraphWorkflow:
        """构建并行讨论工作流"""
        
        workflow = StateGraph(ConversationState)
        
        # 添加并行智能体节点
        for participant in participants:
            workflow.add_node(
                f"agent_{participant.contact_id}",
                self._create_agent_node(participant)
            )
        
        # 添加讨论协调器
        workflow.add_node("discussion_coordinator", self._create_discussion_coordinator())
        
        # 添加共识构建器
        workflow.add_node("consensus_builder", self._create_consensus_builder())
        
        # 所有智能体并行处理
        workflow.set_entry_point("discussion_coordinator")
        
        for participant in participants:
            workflow.add_edge("discussion_coordinator", f"agent_{participant.contact_id}")
            workflow.add_edge(f"agent_{participant.contact_id}", "consensus_builder")
        
        workflow.add_edge("consensus_builder", "__end__")
        
        return workflow.compile()
    
    def _create_agent_node(self, participant: ContactInstance):
        """创建智能体节点"""
        
        async def agent_processor(state: ConversationState) -> ConversationState:
            # 获取个人化配置
            system_prompt = participant.custom_system_prompt or participant.system_prompt
            model_prefs = participant.instance_config.get("model_preferences", participant.model_preferences)
            
            # 获取记忆上下文
            memory_context = await self._get_participant_memory(
                participant.contact_id, 
                state.conversation_id,
                state.messages[-1]["content"]
            )
            
            # 构建提示
            enhanced_prompt = self._build_enhanced_prompt(
                system_prompt,
                memory_context,
                state.conversation_context
            )
            
            # 调用LLM
            response = await self._call_llm(
                enhanced_prompt,
                state.messages,
                model_prefs
            )
            
            # 更新状态
            state.agent_responses[str(participant.contact_id)] = {
                "agent_name": participant.custom_name or participant.display_name,
                "response": response,
                "participant_id": participant.contact_id,
                "timestamp": datetime.utcnow()
            }
            
            # 记录节点执行
            await self._record_node_execution(
                state.workflow_execution_id,
                participant.contact_id,
                "agent",
                state.messages,
                response
            )
            
            return state
        
        return agent_processor
```

### 3. Contact实例管理器

```python
class ContactInstanceManager:
    """Contact实例管理器"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.contact_repo = ContactRepository(db_session)
        self.agent_repo = AgentRepository(db_session)
    
    async def add_agent_to_contacts(
        self, 
        user_id: UUID, 
        agent_id: UUID,
        custom_config: dict = None
    ) -> ContactInstance:
        """将Agent添加到用户联系人"""
        
        # 检查是否已经添加
        existing = await self.contact_repo.get_user_contact_by_agent(user_id, agent_id)
        if existing:
            raise ValueError("Agent already added to contacts")
        
        # 获取Agent定义
        agent_def = await self.agent_repo.get_by_id(agent_id)
        if not agent_def:
            raise ValueError("Agent not found")
        
        # 创建Contact实例
        contact_data = {
            "user_id": user_id,
            "agent_id": agent_id,
            "custom_name": custom_config.get("name") if custom_config else None,
            "custom_system_prompt": custom_config.get("system_prompt") if custom_config else None,
            "custom_personality": custom_config.get("personality", {}),
            "instance_config": {
                "model_preferences": custom_config.get("model_preferences", agent_def.model_preferences),
                "tools": custom_config.get("tools", agent_def.available_tools),
                "resource_limits": custom_config.get("resource_limits", {}),
                "permissions": custom_config.get("permissions", [])
            }
        }
        
        contact = await self.contact_repo.create(contact_data)
        
        return contact
    
    async def get_conversation_participants(
        self, 
        conversation_id: UUID
    ) -> List[ContactInstance]:
        """获取对话参与者的完整实例信息"""
        
        query = """
        SELECT 
            cp.*,
            c.*,
            a.name as agent_name,
            a.display_name as agent_display_name,
            a.system_prompt as agent_system_prompt,
            a.model_preferences as agent_model_preferences,
            a.available_tools as agent_available_tools,
            a.node_config as agent_node_config
        FROM conversation_participants cp
        JOIN contacts c ON cp.contact_id = c.id
        JOIN agents a ON c.agent_id = a.id
        WHERE cp.conversation_id = :conversation_id 
        AND cp.is_active = true
        ORDER BY cp.workflow_priority DESC, cp.joined_at ASC
        """
        
        result = await self.db_session.execute(
            text(query),
            {"conversation_id": conversation_id}
        )
        
        participants = []
        for row in result.fetchall():
            participant = ContactInstance(
                contact_id=row.contact_id,
                user_id=row.user_id,
                agent_id=row.agent_id,
                agent_name=row.agent_name,
                display_name=row.custom_name or row.agent_display_name,
                system_prompt=row.custom_system_prompt or row.agent_system_prompt,
                model_preferences=row.instance_config.get("model_preferences", row.agent_model_preferences),
                available_tools=row.instance_config.get("tools", row.agent_available_tools),
                instance_config=row.instance_config,
                conversation_role=row.role,
                workflow_priority=row.workflow_priority
            )
            participants.append(participant)
        
        return participants
    
    async def add_participant_to_conversation(
        self,
        conversation_id: UUID,
        contact_id: UUID,
        user_id: UUID,
        role: str = "participant"
    ) -> ConversationParticipant:
        """添加Contact到对话"""
        
        # 验证Contact属于该用户
        contact = await self.contact_repo.get_user_contact(user_id, contact_id)
        if not contact:
            raise ValueError("Contact not found or not owned by user")
        
        # 检查是否已经是参与者
        existing = await self._get_conversation_participant(conversation_id, contact_id)
        if existing and existing.is_active:
            raise ValueError("Contact already in conversation")
        
        # 添加参与者
        participant_data = {
            "conversation_id": conversation_id,
            "contact_id": contact_id,
            "user_id": user_id,
            "role": role,
            "join_type": "invited",
            "workflow_priority": 50,  # 默认优先级
            "is_active": True
        }
        
        participant = await self.conversation_participant_repo.create(participant_data)
        
        # 如果是多参与者对话，可能需要重建工作流
        participants_count = await self._count_active_participants(conversation_id)
        if participants_count > 1:
            await self._trigger_workflow_rebuild(conversation_id)
        
        return participant
```

### 4. 记忆系统集成

```python
class ConversationMemoryManager:
    """对话记忆管理器"""
    
    def __init__(self, db_session, mem0_client=None):
        self.db_session = db_session
        self.mem0_client = mem0_client
    
    async def get_participant_memory_context(
        self,
        contact_id: UUID,
        conversation_id: UUID,
        query: str,
        max_items: int = 10
    ) -> dict:
        """获取参与者的记忆上下文"""
        
        memory_context = {
            "individual": [],  # Contact个人记忆
            "shared": [],      # 对话共享记忆  
            "contextual": []   # 上下文相关记忆
        }
        
        if self.mem0_client:
            # 使用Mem0进行智能记忆检索
            try:
                # 个人记忆
                individual_memories = await self.mem0_client.search(
                    query=query,
                    user_id=f"contact_{contact_id}",
                    limit=max_items//3
                )
                memory_context["individual"] = individual_memories
                
                # 共享记忆
                shared_memories = await self.mem0_client.search(
                    query=query,
                    user_id=f"conversation_{conversation_id}",
                    limit=max_items//3
                )
                memory_context["shared"] = shared_memories
                
            except Exception as e:
                logger.warning(f"Mem0 retrieval failed, falling back to database: {e}")
        
        # 数据库记忆检索作为补充或备选
        db_memories = await self._get_database_memories(
            contact_id, conversation_id, query, max_items
        )
        
        # 合并和去重
        memory_context = self._merge_and_deduplicate_memories(
            memory_context, db_memories
        )
        
        return memory_context
    
    async def store_interaction_memory(
        self,
        conversation_id: UUID,
        contact_id: UUID,
        user_message: str,
        agent_response: str,
        interaction_metadata: dict = None
    ):
        """存储交互记忆"""
        
        # 分析重要性和分类
        importance_score = await self._calculate_importance_score(user_message, agent_response)
        memory_category = await self._categorize_memory(user_message, agent_response)
        
        # 存储到Mem0
        if self.mem0_client:
            try:
                # 个人记忆
                await self.mem0_client.add(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": agent_response}
                    ],
                    user_id=f"contact_{contact_id}",
                    metadata={
                        "conversation_id": str(conversation_id),
                        "importance_score": importance_score,
                        "category": memory_category
                    }
                )
                
                # 如果重要，也存储为共享记忆
                if importance_score > 0.7:
                    await self.mem0_client.add(
                        messages=[
                            {"role": "user", "content": user_message},
                            {"role": "assistant", "content": agent_response}
                        ],
                        user_id=f"conversation_{conversation_id}",
                        metadata={
                            "source_contact": str(contact_id),
                            "importance_score": importance_score,
                            "category": memory_category
                        }
                    )
                
            except Exception as e:
                logger.error(f"Failed to store memory in Mem0: {e}")
        
        # 同时存储到数据库
        await self._store_database_memory(
            conversation_id, contact_id, user_message, agent_response, 
            importance_score, memory_category, interaction_metadata
        )
```

## 📊 重新设计的实施计划

基于新的业务流程理解，实施计划调整为：

### 阶段1: 数据模型重构 (Week 1-2)
1. **扩展现有表结构**
2. **创建LangGraph执行记录表**
3. **建立Contact实例管理**

### 阶段2: 核心服务开发 (Week 2-4) 
1. **动态工作流构建器**
2. **Contact实例管理器**
3. **参与者记忆系统**

### 阶段3: 对话流程集成 (Week 3-5)
1. **1v1对话LangGraph集成**
2. **多参与者群聊工作流**
3. **实时参与者管理**

### 阶段4: 高级协作功能 (Week 4-6)
1. **多种协作模式**
2. **智能路由决策**
3. **共识构建机制**

这个重新设计更好地反映了您的实际业务流程，将智能体定义与实例分离，支持用户个性化配置，并基于对话参与者动态构建LangGraph工作流。
# LangGraph 集成架构

> 基于Contact实例的动态多智能体工作流引擎设计

## 📋 目录
- [核心概念](#核心概念)
- [工作流类型](#工作流类型)
- [节点系统设计](#节点系统设计)
- [动态工作流构建](#动态工作流构建)
- [状态管理](#状态管理)
- [执行追踪](#执行追踪)
- [集成实现](#集成实现)

## 🎯 核心概念

### 1. Contact中心化的工作流
```python
# 核心设计理念
Contact实例 = Agent定义 + 用户个性化配置
工作流节点 = Contact实例 + 执行上下文
动态工作流 = 基于对话参与者的Contact列表构建
```

### 2. LangGraph状态定义
```python
from langgraph import StateGraph
from typing import TypedDict, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ConversationState(TypedDict):
    """对话状态定义"""
    # 基础信息
    conversation_id: UUID
    workflow_execution_id: UUID
    current_message: str
    message_history: List[Dict[str, Any]]
    
    # 参与者信息
    active_contacts: List[Dict[str, Any]]  # Contact实例列表
    mentioned_contacts: List[UUID]         # 被@mention的Contact IDs
    
    # 执行状态
    current_step: str
    execution_path: List[str]
    contact_responses: Dict[str, Any]      # Contact响应结果
    
    # 记忆上下文
    shared_memory: List[Dict[str, Any]]    # 共享记忆
    contact_memories: Dict[str, List[Dict[str, Any]]]  # Contact个人记忆
    
    # 元数据
    workflow_type: str
    routing_strategy: str
    started_at: datetime
    metadata: Dict[str, Any]
```

## 🔄 工作流类型

### 1. 单Contact对话 (Single Contact)
```python
async def build_single_contact_workflow(contact: ContactInstance) -> StateGraph:
    """构建单Contact对话工作流"""
    
    workflow = StateGraph(ConversationState)
    
    # 添加Contact处理节点
    workflow.add_node("contact_processor", create_contact_node(contact))
    
    # 添加响应格式化节点
    workflow.add_node("response_formatter", format_single_response)
    
    # 定义流程
    workflow.set_entry_point("contact_processor")
    workflow.add_edge("contact_processor", "response_formatter")
    workflow.add_edge("response_formatter", "__end__")
    
    return workflow.compile()
```

### 2. @Mention路由 (Mention Routing)
```python
async def build_mention_routing_workflow(
    message: str, 
    contacts: List[ContactInstance]
) -> StateGraph:
    """构建@mention路由工作流"""
    
    workflow = StateGraph(ConversationState)
    
    # 解析@mention的Contact
    mentioned_contacts = extract_mentioned_contacts(message, contacts)
    
    # 添加路由节点
    workflow.add_node("mention_router", create_mention_router(mentioned_contacts))
    
    # 为每个被提及的Contact添加处理节点
    for contact in mentioned_contacts:
        node_id = f"contact_{contact.id}"
        workflow.add_node(node_id, create_contact_node(contact))
    
    # 添加响应聚合节点
    workflow.add_node("response_aggregator", aggregate_contact_responses)
    
    # 定义路由逻辑
    workflow.set_entry_point("mention_router")
    
    # 路由到被提及的Contact
    for contact in mentioned_contacts:
        workflow.add_edge("mention_router", f"contact_{contact.id}")
        workflow.add_edge(f"contact_{contact.id}", "response_aggregator")
    
    workflow.add_edge("response_aggregator", "__end__")
    
    return workflow.compile()
```

### 3. 并行讨论 (Parallel Discussion)
```python
async def build_parallel_discussion_workflow(
    contacts: List[ContactInstance]
) -> StateGraph:
    """构建并行讨论工作流"""
    
    workflow = StateGraph(ConversationState)
    
    # 添加讨论协调器
    workflow.add_node("discussion_coordinator", coordinate_parallel_discussion)
    
    # 为每个Contact添加并行处理节点
    for contact in contacts:
        node_id = f"contact_{contact.id}"
        workflow.add_node(node_id, create_contact_node(contact))
    
    # 添加共识构建器
    workflow.add_node("consensus_builder", build_consensus)
    
    # 定义并行执行流程
    workflow.set_entry_point("discussion_coordinator")
    
    # 所有Contact并行处理
    for contact in contacts:
        workflow.add_edge("discussion_coordinator", f"contact_{contact.id}")
        workflow.add_edge(f"contact_{contact.id}", "consensus_builder")
    
    workflow.add_edge("consensus_builder", "__end__")
    
    return workflow.compile()
```

### 4. 顺序处理 (Sequential Processing)
```python
async def build_sequential_workflow(
    contacts: List[ContactInstance]
) -> StateGraph:
    """构建顺序处理工作流"""
    
    workflow = StateGraph(ConversationState)
    
    # 按优先级排序Contact
    sorted_contacts = sorted(contacts, key=lambda c: c.workflow_priority, reverse=True)
    
    # 添加顺序处理节点
    for i, contact in enumerate(sorted_contacts):
        node_id = f"contact_{contact.id}"
        workflow.add_node(node_id, create_contact_node(contact))
        
        if i == 0:
            workflow.set_entry_point(node_id)
        else:
            prev_node = f"contact_{sorted_contacts[i-1].id}"
            workflow.add_edge(prev_node, node_id)
    
    # 最后一个节点连接到结束
    workflow.add_edge(f"contact_{sorted_contacts[-1].id}", "__end__")
    
    return workflow.compile()
```

## 🏗️ 节点系统设计

### 1. Contact智能体节点
```python
def create_contact_node(contact: ContactInstance):
    """创建基于Contact实例的智能体节点"""
    
    async def contact_processor(state: ConversationState) -> ConversationState:
        # 获取Contact的个性化配置
        system_prompt = contact.custom_system_prompt or contact.agent_system_prompt
        model_config = contact.instance_config.get(
            "model_preferences", 
            contact.agent_model_preferences
        )
        
        # 获取Contact的记忆上下文
        memory_context = await get_contact_memory_context(
            contact.id,
            state.conversation_id,
            state.current_message
        )
        
        # 构建增强提示
        enhanced_prompt = build_enhanced_prompt(
            system_prompt,
            memory_context,
            state.message_history
        )
        
        # 应用Contact的工具权限
        available_tools = get_contact_available_tools(contact)
        
        # 调用LLM
        try:
            response = await call_llm_with_tools(
                model=model_config.get("default_model", "gpt-4-turbo"),
                messages=build_message_sequence(enhanced_prompt, state.current_message),
                tools=available_tools,
                **model_config
            )
            
            # 记录Token使用
            await record_contact_token_usage(
                contact.id,
                state.workflow_execution_id,
                response.usage
            )
            
            # 更新状态
            state.contact_responses[str(contact.id)] = {
                "contact_id": contact.id,
                "contact_name": contact.custom_name or contact.agent_display_name,
                "agent_id": contact.agent_id,
                "response": response.content,
                "tool_calls": response.tool_calls,
                "tokens_used": response.usage.total_tokens,
                "timestamp": datetime.utcnow()
            }
            
            # 存储新的记忆
            await store_contact_interaction_memory(
                contact.id,
                state.conversation_id,
                state.current_message,
                response.content
            )
            
        except Exception as e:
            # 记录执行错误
            await record_contact_execution_error(
                contact.id,
                state.workflow_execution_id,
                str(e)
            )
            
            state.contact_responses[str(contact.id)] = {
                "contact_id": contact.id,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.utcnow()
            }
        
        # 更新执行路径
        state.execution_path.append(f"contact_{contact.id}")
        
        return state
    
    return contact_processor
```

### 2. 路由节点
```python
async def create_mention_router(mentioned_contacts: List[ContactInstance]):
    """创建@mention路由节点"""
    
    async def mention_router(state: ConversationState) -> ConversationState:
        # 解析@mention内容
        mentions = extract_mentions_from_message(state.current_message)
        
        # 匹配到具体的Contact实例
        routed_contacts = []
        for mention in mentions:
            contact = find_contact_by_mention(mention, mentioned_contacts)
            if contact:
                routed_contacts.append(contact.id)
        
        # 更新状态
        state.mentioned_contacts = routed_contacts
        state.current_step = "routing_to_contacts"
        state.metadata["routing_decisions"] = {
            "mentions_found": mentions,
            "contacts_routed": routed_contacts,
            "routing_strategy": "mention_based"
        }
        
        return state
    
    return mention_router
```

### 3. 聚合节点
```python
async def aggregate_contact_responses(state: ConversationState) -> ConversationState:
    """聚合多个Contact的响应"""
    
    successful_responses = []
    failed_responses = []
    
    for contact_id, response in state.contact_responses.items():
        if "error" in response:
            failed_responses.append(response)
        else:
            successful_responses.append(response)
    
    # 构建聚合响应
    if successful_responses:
        if len(successful_responses) == 1:
            # 单个响应，直接返回
            aggregated_response = successful_responses[0]["response"]
        else:
            # 多个响应，构建协作格式
            aggregated_response = format_collaborative_response(successful_responses)
    else:
        # 所有响应都失败
        aggregated_response = "抱歉，所有智能体都无法处理您的请求。"
    
    # 更新状态
    state.current_step = "response_aggregated"
    state.metadata["aggregation_summary"] = {
        "successful_count": len(successful_responses),
        "failed_count": len(failed_responses),
        "total_tokens": sum(r.get("tokens_used", 0) for r in successful_responses)
    }
    
    return state

def format_collaborative_response(responses: List[Dict]) -> str:
    """格式化协作响应"""
    
    formatted_parts = []
    for response in responses:
        contact_name = response["contact_name"]
        content = response["response"]
        
        formatted_parts.append(f"**{contact_name}**:\n{content}")
    
    return "\n\n---\n\n".join(formatted_parts)
```

## 🔧 动态工作流构建

### 1. 工作流构建器
```python
class DynamicWorkflowBuilder:
    """基于Contact参与者的动态工作流构建器"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.contact_manager = ContactInstanceManager(db_session)
    
    async def build_workflow_for_conversation(
        self,
        conversation_id: UUID,
        trigger_message: str
    ) -> StateGraph:
        """为对话构建工作流"""
        
        # 1. 获取对话中的活跃Contact参与者
        active_contacts = await self.contact_manager.get_conversation_participants(
            conversation_id
        )
        
        # 2. 分析消息确定工作流类型
        workflow_type = await self._analyze_workflow_type(
            trigger_message, active_contacts
        )
        
        # 3. 根据类型构建相应的工作流
        if workflow_type == "single_contact":
            return await self._build_single_contact_workflow(active_contacts[0])
        elif workflow_type == "mention_routing":
            return await build_mention_routing_workflow(trigger_message, active_contacts)
        elif workflow_type == "parallel_discussion":
            return await build_parallel_discussion_workflow(active_contacts)
        elif workflow_type == "sequential_processing":
            return await build_sequential_workflow(active_contacts)
        else:
            return await self._build_default_workflow(active_contacts)
    
    async def _analyze_workflow_type(
        self,
        message: str,
        contacts: List[ContactInstance]
    ) -> str:
        """分析确定工作流类型"""
        
        # 检查@mention
        mentions = extract_mentions_from_message(message)
        if mentions:
            return "mention_routing"
        
        # 检查参与者数量
        if len(contacts) == 1:
            return "single_contact"
        elif len(contacts) <= 3:
            return "parallel_discussion"
        else:
            return "sequential_processing"
    
    async def rebuild_workflow_on_participant_change(
        self,
        conversation_id: UUID,
        current_execution_id: UUID
    ):
        """参与者变更时重建工作流"""
        
        # 暂停当前执行
        await self._pause_workflow_execution(current_execution_id)
        
        # 获取最新参与者列表
        updated_contacts = await self.contact_manager.get_conversation_participants(
            conversation_id
        )
        
        # 构建新的工作流
        new_workflow = await self.build_workflow_for_conversation(
            conversation_id,
            "参与者变更重建工作流"
        )
        
        # 恢复执行状态
        await self._resume_workflow_with_new_graph(
            current_execution_id,
            new_workflow
        )
```

### 2. 工作流类型智能识别
```python
async def intelligent_workflow_analysis(
    message: str,
    contacts: List[ContactInstance],
    conversation_history: List[Dict]
) -> Dict[str, Any]:
    """智能分析工作流类型"""
    
    analysis_result = {
        "workflow_type": "parallel_discussion",  # 默认
        "routing_strategy": "auto",
        "estimated_participants": len(contacts),
        "reasoning": []
    }
    
    # 1. @mention分析
    mentions = extract_mentions_from_message(message)
    if mentions:
        analysis_result["workflow_type"] = "mention_routing"
        analysis_result["routing_strategy"] = "mention_based"
        analysis_result["reasoning"].append("检测到@mention，使用路由工作流")
    
    # 2. 问题复杂度分析
    complexity_score = await analyze_message_complexity(message)
    if complexity_score > 0.8:
        analysis_result["workflow_type"] = "sequential_processing"
        analysis_result["reasoning"].append("问题复杂度高，建议顺序处理")
    
    # 3. Contact能力匹配
    capability_match = await analyze_contact_capability_match(message, contacts)
    if capability_match["high_match_count"] == 1:
        analysis_result["workflow_type"] = "single_contact"
        analysis_result["reasoning"].append("单个Contact高度匹配")
    
    # 4. 历史协作模式学习
    historical_pattern = await analyze_historical_collaboration(
        contacts, conversation_history
    )
    if historical_pattern["preferred_mode"]:
        analysis_result["workflow_type"] = historical_pattern["preferred_mode"]
        analysis_result["reasoning"].append("基于历史协作模式推荐")
    
    return analysis_result
```

## 💾 状态管理

### 1. 状态持久化
```python
class WorkflowStateManager:
    """工作流状态管理器"""
    
    async def save_workflow_state(
        self,
        execution_id: UUID,
        state: ConversationState
    ):
        """保存工作流状态"""
        
        state_snapshot = {
            "conversation_id": str(state.conversation_id),
            "current_step": state.current_step,
            "execution_path": state.execution_path,
            "contact_responses": state.contact_responses,
            "metadata": state.metadata,
            "snapshot_time": datetime.utcnow().isoformat()
        }
        
        await self.db_session.execute("""
            UPDATE workflow_executions 
            SET 
                execution_path = :execution_path,
                metadata = jsonb_set(metadata, '{state_snapshots}', 
                                   COALESCE(metadata->'state_snapshots', '[]'::jsonb) || :snapshot::jsonb)
            WHERE id = :execution_id
        """, {
            "execution_id": execution_id,
            "execution_path": state.execution_path,
            "snapshot": json.dumps(state_snapshot)
        })
    
    async def restore_workflow_state(
        self,
        execution_id: UUID
    ) -> ConversationState:
        """恢复工作流状态"""
        
        result = await self.db_session.execute("""
            SELECT execution_path, metadata
            FROM workflow_executions
            WHERE id = :execution_id
        """, {"execution_id": execution_id})
        
        execution_data = result.fetchone()
        if not execution_data:
            raise ValueError(f"Workflow execution {execution_id} not found")
        
        # 从最新状态快照恢复
        snapshots = execution_data.metadata.get("state_snapshots", [])
        if snapshots:
            latest_snapshot = snapshots[-1]
            return ConversationState(**latest_snapshot)
        
        # 如果没有快照，创建基础状态
        return ConversationState(
            execution_path=execution_data.execution_path,
            contact_responses={},
            metadata=execution_data.metadata
        )
```

### 2. 检查点机制
```python
async def create_workflow_checkpoint(
    execution_id: UUID,
    state: ConversationState,
    checkpoint_reason: str
):
    """创建工作流检查点"""
    
    checkpoint_data = {
        "execution_id": str(execution_id),
        "checkpoint_time": datetime.utcnow().isoformat(),
        "reason": checkpoint_reason,
        "state_data": {
            "current_step": state.current_step,
            "execution_path": state.execution_path,
            "contact_responses": state.contact_responses,
            "metadata": state.metadata
        }
    }
    
    # 保存到数据库
    await db.execute("""
        INSERT INTO workflow_checkpoints 
        (execution_id, checkpoint_data, created_at)
        VALUES (:execution_id, :checkpoint_data, NOW())
    """, {
        "execution_id": execution_id,
        "checkpoint_data": json.dumps(checkpoint_data)
    })
```

## 📊 执行追踪

### 1. 完整执行链追踪
```python
class WorkflowExecutionTracker:
    """工作流执行追踪器"""
    
    async def start_workflow_execution(
        self,
        conversation_id: UUID,
        workflow_type: str,
        participant_contacts: List[UUID],
        input_data: Dict
    ) -> UUID:
        """开始工作流执行追踪"""
        
        execution_record = WorkflowExecution(
            conversation_id=conversation_id,
            workflow_type=workflow_type,
            participant_contacts=participant_contacts,
            routing_strategy="auto",
            status="running",
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        
        result = await self.execution_repo.create(execution_record)
        return result.id
    
    async def track_node_execution(
        self,
        workflow_execution_id: UUID,
        contact_id: UUID,
        node_id: str,
        node_type: str,
        input_state: Dict,
        output_state: Dict,
        duration_ms: int,
        tokens_used: int = 0,
        cost_usd: float = 0.0
    ):
        """追踪节点执行"""
        
        node_execution = NodeExecution(
            workflow_execution_id=workflow_execution_id,
            contact_id=contact_id,
            node_id=node_id,
            node_type=node_type,
            input_state=input_state,
            output_state=output_state,
            status="completed",
            started_at=datetime.utcnow() - timedelta(milliseconds=duration_ms),
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            prompt_tokens=tokens_used // 2,  # 估算
            completion_tokens=tokens_used // 2,
            cost_usd=cost_usd
        )
        
        await self.node_execution_repo.create(node_execution)
    
    async def get_execution_trace(
        self,
        workflow_execution_id: UUID
    ) -> Dict[str, Any]:
        """获取完整执行追踪"""
        
        # 获取工作流执行信息
        workflow = await self.execution_repo.get_by_id(workflow_execution_id)
        
        # 获取所有节点执行
        nodes = await self.node_execution_repo.get_by_workflow(workflow_execution_id)
        
        # 获取工具调用
        for node in nodes:
            node.tool_calls = await self.tool_execution_repo.get_by_node(node.id)
        
        # 构建追踪报告
        return {
            "workflow": workflow,
            "execution_path": workflow.execution_path,
            "node_executions": nodes,
            "total_duration": workflow.total_duration_ms,
            "total_tokens": workflow.total_tokens,
            "total_cost": workflow.total_cost_usd,
            "success_rate": self._calculate_success_rate(nodes)
        }
```

### 2. 实时状态推送
```python
class WorkflowStatusBroadcaster:
    """工作流状态实时推送"""
    
    async def broadcast_workflow_started(
        self,
        conversation_id: UUID,
        execution_id: UUID,
        participants: List[Dict]
    ):
        """推送工作流开始状态"""
        
        message = {
            "type": "workflow_started",
            "conversation_id": str(conversation_id),
            "execution_id": str(execution_id),
            "participants": participants,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.broadcast_to_conversation(
            conversation_id, message
        )
    
    async def broadcast_contact_processing(
        self,
        conversation_id: UUID,
        contact_id: UUID,
        contact_name: str,
        status: str
    ):
        """推送Contact处理状态"""
        
        message = {
            "type": "contact_processing",
            "conversation_id": str(conversation_id),
            "contact_id": str(contact_id),
            "contact_name": contact_name,
            "status": status,  # "started", "processing", "completed", "failed"
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.websocket_manager.broadcast_to_conversation(
            conversation_id, message
        )
```

## 🔗 集成实现

### 1. FastAPI集成
```python
from fastapi import APIRouter, Depends, BackgroundTasks
from .services.langgraph.workflow_engine import WorkflowEngine

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
async def process_chat_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """处理聊天消息，支持多Contact协作"""
    
    # 检查是否需要启动工作流
    conversation = await get_conversation(request.conversation_id, db)
    participants = await get_conversation_participants(request.conversation_id, db)
    
    if len(participants) > 1 or "@" in request.message:
        # 多Contact协作模式
        workflow_engine = WorkflowEngine(db)
        
        # 异步执行工作流
        background_tasks.add_task(
            workflow_engine.execute_workflow,
            request.conversation_id,
            request.message,
            current_user.id
        )
        
        return {
            "status": "workflow_started",
            "message": "多智能体协作处理中...",
            "estimated_duration": "10-30秒"
        }
    else:
        # 单Contact模式，直接处理
        return await process_single_contact_message(request, db)
```

### 2. 错误处理和恢复
```python
class WorkflowErrorHandler:
    """工作流错误处理器"""
    
    async def handle_workflow_error(
        self,
        execution_id: UUID,
        error: Exception,
        current_state: ConversationState
    ):
        """处理工作流执行错误"""
        
        # 记录错误详情
        await self._record_error_details(execution_id, error, current_state)
        
        # 尝试错误恢复
        if isinstance(error, ContactTimeoutError):
            await self._handle_contact_timeout(execution_id, error.contact_id)
        elif isinstance(error, LLMRateLimitError):
            await self._handle_rate_limit_error(execution_id, error)
        elif isinstance(error, MemoryRetrievalError):
            await self._handle_memory_error(execution_id, error)
        else:
            # 未知错误，进入安全模式
            await self._enter_safe_mode(execution_id, current_state)
    
    async def _handle_contact_timeout(self, execution_id: UUID, contact_id: UUID):
        """处理Contact超时"""
        
        # 移除超时的Contact，继续执行其他Contact
        await self.workflow_manager.remove_participant_and_continue(
            execution_id, contact_id
        )
        
        # 通知用户
        await self.notification_service.notify_contact_timeout(contact_id)
```

## 📚 相关文档

- **[架构概览](architecture-overview.md)** - 系统整体架构
- **[数据库设计](database-design.md)** - LangGraph相关数据模型
- **[实施计划](implementation-plan.md)** - LangGraph集成实施步骤
- **[部署指南](deployment-guide.md)** - LangGraph运行环境配置

---

> 📝 **LangGraph版本**: 0.0.40+  
> 🔄 **最后更新**: 2025-08-22  
> 🏷️ **集成版本**: v2.0 (Contact实例化工作流)
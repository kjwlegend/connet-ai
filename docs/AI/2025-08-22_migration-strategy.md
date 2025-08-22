# LangGraph 系统迁移策略

## 📋 迁移概述

基于现有 BFF 架构，采用**渐进式迁移策略**，确保在不影响现有功能的前提下，逐步集成 LangGraph 多智能体协作系统。

## 🎯 迁移目标

### 核心目标
1. **零停机迁移** - 现有功能持续可用
2. **向后兼容** - 现有 API 接口保持不变
3. **特性开关** - 支持新旧系统平滑切换
4. **数据完整性** - 保证数据迁移的完整性和一致性

### 功能目标
1. **@mention 路由** - 新增动态智能体调用能力
2. **多智能体协作** - 支持并行和串行协作模式
3. **完整追溯** - 每个执行步骤可追溯和分析
4. **Token 统计** - 精确的使用量统计和成本控制

## 🚀 迁移阶段规划

### 阶段 1: 基础设施准备 (Week 1-2)
**目标**: 准备 LangGraph 集成的基础设施，不影响现有服务

#### 1.1 数据库扩展
```sql
-- 添加 LangGraph 相关表，保持现有表不变
CREATE TABLE workflow_executions (...);
CREATE TABLE node_executions (...);
CREATE TABLE tool_executions (...);
CREATE TABLE token_usage_logs (...);

-- 扩展现有 agents 表，添加 LangGraph 字段
ALTER TABLE agents ADD COLUMN node_type VARCHAR(50) DEFAULT 'agent';
ALTER TABLE agents ADD COLUMN execution_config JSONB DEFAULT '{}';
ALTER TABLE agents ADD COLUMN dependencies JSONB DEFAULT '[]';
```

#### 1.2 环境变量和配置
```python
# config/settings.py 扩展
class Settings(BaseSettings):
    # ... 现有配置保持不变 ...
    
    # LangGraph 功能开关
    LANGGRAPH_ENABLED: bool = Field(default=False, env="LANGGRAPH_ENABLED")
    LANGGRAPH_DEBUG: bool = Field(default=False, env="LANGGRAPH_DEBUG")
    
    # LangGraph 配置
    LANGGRAPH_CHECKPOINT_DB_URL: str = Field(default="", env="LANGGRAPH_CHECKPOINT_DB_URL")
    LANGGRAPH_MAX_CONCURRENT_WORKFLOWS: int = Field(default=10)
    LANGGRAPH_DEFAULT_TIMEOUT: int = Field(default=300)  # 5分钟
    
    # Mem0 集成配置
    MEM0_API_KEY: str = Field(default="", env="MEM0_API_KEY")
    MEM0_BASE_URL: str = Field(default="https://api.mem0.ai", env="MEM0_BASE_URL")
```

#### 1.3 依赖管理
```toml
# pyproject.toml 添加新依赖
[project.dependencies]
# ... 现有依赖保持不变 ...

# LangGraph 相关依赖
langgraph = "^0.0.40"
langchain = "^0.1.0"
langsmith = "^0.1.0"  # 可选，用于调试

# Mem0 集成
mem0ai = "^0.1.0"

# 监控和追踪
opentelemetry-api = "^1.20.0"
opentelemetry-sdk = "^1.20.0"
```

### 阶段 2: 核心服务并行开发 (Week 2-4)
**目标**: 在不影响现有服务的情况下，并行开发 LangGraph 核心服务

#### 2.1 LangGraph 服务开发
```python
# services/langgraph/workflow_engine.py
class WorkflowEngine:
    """LangGraph 工作流引擎，与现有服务隔离"""
    
    def __init__(self, settings: Settings):
        self.enabled = settings.LANGGRAPH_ENABLED
        self.graph = None
        if self.enabled:
            self.graph = self._build_langgraph()
    
    async def process_chat_request(self, request: ChatRequest) -> ChatResponse:
        """处理聊天请求，支持回退到现有系统"""
        if not self.enabled or not self._should_use_langgraph(request):
            # 回退到现有系统
            return await self._fallback_to_legacy(request)
        
        # 使用 LangGraph 处理
        return await self._process_with_langgraph(request)
```

#### 2.2 特性开关集成
```python
# api/v1/endpoints/ai_chat.py 修改
@router.post("/")
async def chat_with_agent(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
) -> ChatResponse:
    """聊天接口 - 支持 LangGraph 和传统模式切换"""
    
    # 检查是否启用 LangGraph 且有 @mention
    mentions = extract_mentions(request.messages[-1].content) if request.messages else []
    
    if settings.LANGGRAPH_ENABLED and mentions:
        # 使用新的 LangGraph 系统
        workflow_engine = WorkflowEngine(settings)
        return await workflow_engine.process_chat_request(request)
    else:
        # 使用现有传统系统 (保持原有逻辑不变)
        return await _legacy_chat_handler(request, current_user, db)

async def _legacy_chat_handler(request, current_user, db):
    """现有的聊天处理逻辑，保持不变"""
    # ... 现有的所有逻辑保持不变 ...
    # 只是移动到这个函数中，便于管理
```

#### 2.3 监控集成
```python
# services/monitoring/execution_tracer.py
class ExecutionTracer:
    """执行追踪，同时支持新旧系统"""
    
    def __init__(self, legacy_logger):
        self.legacy_logger = legacy_logger  # 复用现有日志系统
    
    async def trace_langgraph_execution(self, workflow_id: str):
        """LangGraph 执行追踪"""
        # 记录到新的追踪系统
        await self._record_to_db(workflow_id)
        
        # 同时记录到现有日志系统，保持兼容性
        self.legacy_logger.info(f"LangGraph workflow {workflow_id} started")
```

### 阶段 3: 智能体系统整合 (Week 3-5)
**目标**: 将现有智能体系统与 LangGraph 节点系统整合

#### 3.1 现有智能体服务增强
```python
# services/ai_agent_service.py 增强
class AIAgentService(BaseService):
    """增强现有服务，支持 LangGraph 集成"""
    
    def __init__(self, session, settings: Settings):
        super().__init__(session)
        self.agent_repo = AgentRepository(session)
        
        # 新增 LangGraph 管理器 (可选)
        self.langgraph_manager = None
        if settings.LANGGRAPH_ENABLED:
            from services.langgraph.node_registry import NodeRegistry
            self.langgraph_manager = NodeRegistry(session)
    
    async def create_agent(self, agent_data: AIAgentCreate, user_id: UUID) -> AIAgentResponse:
        """创建智能体 - 保持现有接口，内部增强"""
        
        # 现有逻辑完全保持不变
        agent = await self.agent_repo.create_agent(agent_data, user_id)
        
        # 新增: 如果启用 LangGraph，注册为节点
        if self.langgraph_manager:
            try:
                await self.langgraph_manager.register_agent_node(agent)
            except Exception as e:
                # 失败不影响智能体创建，只记录日志
                logger.warning(f"Failed to register agent as LangGraph node: {e}")
        
        return AIAgentResponse.model_validate(agent)
    
    async def update_agent(self, agent_id: UUID, agent_data: AIAgentUpdate, user_id: UUID):
        """更新智能体 - 保持现有接口，内部增强"""
        
        # 现有更新逻辑保持不变
        updated_agent = await self.agent_repo.update_agent(agent_id, agent_data, user_id)
        
        # 新增: 更新 LangGraph 节点配置
        if self.langgraph_manager and updated_agent:
            try:
                await self.langgraph_manager.update_agent_node(updated_agent)
            except Exception as e:
                logger.warning(f"Failed to update LangGraph node: {e}")
        
        return updated_agent
```

#### 3.2 智能体注册系统
```python
# agents/registry.py
class AgentRegistry:
    """智能体注册器，桥接现有系统和 LangGraph"""
    
    def __init__(self, db_session, node_registry=None):
        self.db_session = db_session
        self.node_registry = node_registry  # LangGraph 节点注册中心
        self._builtin_agents = {}
        self._load_builtin_agents()
    
    def _load_builtin_agents(self):
        """加载内置智能体"""
        from agents.builtin.coder_agent import CoderAgent
        from agents.builtin.analyst_agent import AnalystAgent
        from agents.builtin.writer_agent import WriterAgent
        from agents.builtin.researcher_agent import ResearcherAgent
        
        self._builtin_agents = {
            "coder": CoderAgent,
            "analyst": AnalystAgent,
            "writer": WriterAgent,
            "researcher": ResearcherAgent
        }
    
    async def get_agent_by_mention(self, mention: str) -> Optional[BaseAgent]:
        """根据 @mention 获取智能体实例"""
        
        # 1. 先查找内置智能体
        if mention in self._builtin_agents:
            return self._builtin_agents[mention]()
        
        # 2. 查找数据库中的自定义智能体
        agent_repo = AgentRepository(self.db_session)
        agent_model = await agent_repo.get_agent_by_name(mention)
        
        if agent_model:
            return await self._create_dynamic_agent(agent_model)
        
        return None
    
    async def _create_dynamic_agent(self, agent_model):
        """基于数据库配置创建动态智能体"""
        from agents.base_agent import BaseAgent
        
        class DynamicAgent(BaseAgent):
            def __init__(self, model):
                self.model = model
                super().__init__(
                    agent_id=model.name,
                    display_name=model.display_name,
                    system_prompt=model.system_prompt,
                    model_preferences=model.model_preferences
                )
        
        return DynamicAgent(agent_model)
```

### 阶段 4: 记忆系统优化 (Week 4-6)
**目标**: 优化现有记忆系统，集成 Mem0 和 LangGraph 状态管理

#### 4.1 记忆服务增强
```python
# services/ai_memory_service.py 增强
class AIMemoryService(BaseService):
    """增强现有记忆服务"""
    
    def __init__(self, session, settings: Settings):
        super().__init__(session)
        self.memory_repo = AIMemoryRepositoryImpl(session)
        self.summary_repo = AIConversationSummaryRepositoryImpl(session)
        
        # 新增 Mem0 集成
        self.mem0_client = None
        if settings.MEM0_API_KEY:
            from services.external.mem0_service import Mem0Service
            self.mem0_client = Mem0Service(settings.MEM0_API_KEY)
    
    async def get_contextual_memories(
        self,
        user_id: UUID,
        conversation_id: UUID,
        current_context: str,
        max_memories: int = 10
    ) -> List[MemoryResponse]:
        """获取上下文相关记忆 - 优先使用 Mem0，回退到数据库"""
        
        if self.mem0_client:
            try:
                # 使用 Mem0 进行智能记忆检索
                mem0_memories = await self.mem0_client.search_memories(
                    user_id=str(user_id),
                    query=current_context,
                    limit=max_memories
                )
                
                if mem0_memories:
                    return self._convert_mem0_to_memory_response(mem0_memories)
            
            except Exception as e:
                logger.warning(f"Mem0 search failed, falling back to database: {e}")
        
        # 回退到现有数据库查询逻辑
        return await self._get_contextual_memories_from_db(
            user_id, conversation_id, current_context, max_memories
        )
    
    async def _get_contextual_memories_from_db(self, user_id, conversation_id, context, max_memories):
        """现有的数据库记忆查询逻辑，保持不变"""
        # ... 现有逻辑完全保持不变 ...
        pass
```

#### 4.2 Mem0 服务集成
```python
# services/external/mem0_service.py
class Mem0Service:
    """Mem0 记忆服务集成"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.mem0.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = self._create_client()
    
    async def search_memories(self, user_id: str, query: str, limit: int = 10):
        """搜索记忆"""
        try:
            response = await self.client.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            return response.get('memories', [])
        except Exception as e:
            logger.error(f"Mem0 search failed: {e}")
            raise
    
    async def add_memory(self, user_id: str, content: str, metadata: dict = None):
        """添加记忆"""
        try:
            response = await self.client.add(
                messages=[{"role": "user", "content": content}],
                user_id=user_id,
                metadata=metadata or {}
            )
            return response
        except Exception as e:
            logger.error(f"Mem0 add memory failed: {e}")
            raise
```

### 阶段 5: API 接口升级 (Week 5-7)
**目标**: 升级 API 接口支持新功能，保持向后兼容

#### 5.1 智能体管理接口扩展
```python
# api/v1/endpoints/ai_agents.py 扩展
@router.post("/nodes/register")
async def register_agent_node(
    agent_id: UUID,
    node_config: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
):
    """注册智能体为 LangGraph 节点 - 新增接口"""
    
    if not settings.LANGGRAPH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LangGraph is not enabled"
        )
    
    # ... 节点注册逻辑 ...

@router.get("/nodes")
async def list_agent_nodes(
    current_user: UserResponse = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
):
    """列出所有可用的智能体节点 - 新增接口"""
    
    if not settings.LANGGRAPH_ENABLED:
        return {"nodes": [], "langgraph_enabled": False}
    
    # ... 节点列表逻辑 ...

# 现有接口保持完全不变
@router.post("/")
async def create_agent(...):
    """现有创建接口保持不变"""
    # ... 现有逻辑完全保持不变 ...
```

#### 5.2 新增工作流管理接口
```python
# api/v1/endpoints/workflows.py - 全新接口
from fastapi import APIRouter, Depends, HTTPException
from schemas.workflows import WorkflowExecutionResponse, WorkflowStatusResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get("/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> WorkflowStatusResponse:
    """获取工作流状态"""
    
    execution_repo = WorkflowExecutionRepository(db)
    workflow = await execution_repo.get_by_id(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowStatusResponse.model_validate(workflow)

@router.get("/{workflow_id}/trace")
async def get_workflow_trace(
    workflow_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """获取工作流执行追踪"""
    
    tracer = ExecutionTracer(db)
    trace_data = await tracer.get_full_trace(workflow_id)
    
    return {
        "workflow_id": workflow_id,
        "trace": trace_data,
        "generated_at": datetime.utcnow()
    }
```

### 阶段 6: 监控和分析 (Week 6-8)
**目标**: 完善监控和分析系统，支持新旧系统对比

#### 6.1 分析统计接口
```python
# api/v1/endpoints/analytics.py - 全新接口
@router.get("/usage/comparison")
async def get_usage_comparison(
    start_date: datetime,
    end_date: datetime,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """获取新旧系统使用对比"""
    
    metrics_service = MetricsService(db)
    
    # 传统系统使用统计
    legacy_stats = await metrics_service.get_legacy_usage_stats(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # LangGraph 系统使用统计
    langgraph_stats = await metrics_service.get_langgraph_usage_stats(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return {
        "period": {"start": start_date, "end": end_date},
        "legacy_system": legacy_stats,
        "langgraph_system": langgraph_stats,
        "comparison": {
            "performance_improvement": langgraph_stats.avg_response_time / legacy_stats.avg_response_time,
            "feature_usage": {
                "multi_agent_conversations": langgraph_stats.multi_agent_count,
                "tool_calls": langgraph_stats.tool_execution_count
            }
        }
    }

@router.get("/token-usage")
async def get_token_usage_analytics(
    period: str = "7d",  # 7d, 30d, 90d
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """获取 Token 使用分析"""
    
    token_service = TokenUsageService(db)
    
    usage_data = await token_service.get_usage_analytics(
        user_id=current_user.id,
        period=period
    )
    
    return {
        "period": period,
        "total_tokens": usage_data.total_tokens,
        "cost_breakdown": usage_data.cost_breakdown,
        "usage_by_agent": usage_data.agent_usage,
        "trends": usage_data.daily_trends
    }
```

#### 6.2 实时监控集成
```python
# services/monitoring/performance_monitor.py
class PerformanceMonitor:
    """性能监控，同时监控新旧系统"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.metrics_collector = MetricsCollector()
    
    async def monitor_chat_request(self, request_type: str, duration: float, success: bool):
        """监控聊天请求性能"""
        
        # 记录到数据库
        await self.metrics_collector.record_metric(
            metric_type="chat_performance",
            tags={
                "request_type": request_type,  # "legacy" or "langgraph"
                "success": success
            },
            value=duration
        )
        
        # 如果是 LangGraph 请求且性能异常，记录详细信息
        if request_type == "langgraph" and (duration > 10000 or not success):
            await self._record_performance_anomaly(request_type, duration, success)
    
    async def _record_performance_anomaly(self, request_type, duration, success):
        """记录性能异常"""
        logger.warning(
            f"Performance anomaly detected",
            extra={
                "request_type": request_type,
                "duration_ms": duration,
                "success": success,
                "timestamp": datetime.utcnow()
            }
        )
```

### 阶段 7: 生产部署和切换 (Week 7-8)
**目标**: 安全地在生产环境中部署和逐步启用新功能

#### 7.1 部署策略
```yaml
# docker-compose.yml 扩展
version: '3.8'
services:
  bff:
    # ... 现有配置保持不变 ...
    environment:
      # ... 现有环境变量保持不变 ...
      
      # LangGraph 功能开关
      LANGGRAPH_ENABLED: ${LANGGRAPH_ENABLED:-false}
      LANGGRAPH_DEBUG: ${LANGGRAPH_DEBUG:-false}
      
      # Mem0 集成
      MEM0_API_KEY: ${MEM0_API_KEY:-}
      
      # 监控配置
      ENABLE_PERFORMANCE_MONITORING: ${ENABLE_PERFORMANCE_MONITORING:-true}
  
  # 新增 LangGraph 检查点数据库 (可选)
  langgraph-db:
    image: postgres:15
    environment:
      POSTGRES_DB: langgraph_checkpoints
      POSTGRES_USER: langgraph
      POSTGRES_PASSWORD: ${LANGGRAPH_DB_PASSWORD}
    volumes:
      - langgraph_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    profiles:
      - langgraph  # 只在启用 LangGraph 时启动

volumes:
  langgraph_data:
```

#### 7.2 渐进式启用策略
```python
# 生产环境启用策略
class FeatureRolloutManager:
    """功能发布管理器"""
    
    def __init__(self, settings: Settings, db_session):
        self.settings = settings
        self.db_session = db_session
        self.rollout_percentage = self._get_rollout_percentage()
    
    def should_enable_langgraph_for_user(self, user_id: UUID) -> bool:
        """判断是否为用户启用 LangGraph"""
        
        # 全局开关未启用
        if not self.settings.LANGGRAPH_ENABLED:
            return False
        
        # 基于用户ID进行灰度发布
        user_hash = int(str(user_id).replace('-', ''), 16)
        user_percentage = user_hash % 100
        
        return user_percentage < self.rollout_percentage
    
    def _get_rollout_percentage(self) -> int:
        """获取发布百分比"""
        # 可以从数据库配置或环境变量获取
        return int(os.getenv("LANGGRAPH_ROLLOUT_PERCENTAGE", "0"))

# 在聊天接口中使用
@router.post("/")
async def chat_with_agent(request: ChatRequest, ...):
    rollout_manager = FeatureRolloutManager(settings, db)
    
    mentions = extract_mentions(request.messages[-1].content) if request.messages else []
    use_langgraph = (
        mentions and 
        rollout_manager.should_enable_langgraph_for_user(current_user.id)
    )
    
    if use_langgraph:
        return await _langgraph_chat_handler(request, current_user, db)
    else:
        return await _legacy_chat_handler(request, current_user, db)
```

### 阶段 8: 监控和优化 (Week 8+)
**目标**: 持续监控系统表现，优化性能和用户体验

#### 8.1 A/B 测试框架
```python
# services/monitoring/ab_testing.py
class ABTestingService:
    """A/B 测试服务"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def record_experiment_result(
        self,
        user_id: UUID,
        experiment_name: str,
        variant: str,
        success_metric: float,
        metadata: dict = None
    ):
        """记录实验结果"""
        
        result = ExperimentResult(
            user_id=user_id,
            experiment_name=experiment_name,
            variant=variant,  # "legacy" or "langgraph"
            success_metric=success_metric,
            metadata=metadata or {},
            recorded_at=datetime.utcnow()
        )
        
        self.db_session.add(result)
        await self.db_session.commit()
    
    async def get_experiment_analysis(self, experiment_name: str) -> dict:
        """获取实验分析结果"""
        
        # 查询实验数据
        results = await self._query_experiment_results(experiment_name)
        
        # 统计分析
        legacy_results = [r for r in results if r.variant == "legacy"]
        langgraph_results = [r for r in results if r.variant == "langgraph"]
        
        return {
            "experiment": experiment_name,
            "sample_sizes": {
                "legacy": len(legacy_results),
                "langgraph": len(langgraph_results)
            },
            "success_metrics": {
                "legacy": self._calculate_metrics(legacy_results),
                "langgraph": self._calculate_metrics(langgraph_results)
            },
            "statistical_significance": self._calculate_significance(
                legacy_results, langgraph_results
            )
        }
```

#### 8.2 自动化回退机制
```python
# services/monitoring/auto_fallback.py
class AutoFallbackManager:
    """自动回退管理器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.error_threshold = 0.05  # 5% 错误率阈值
        self.response_time_threshold = 10000  # 10秒响应时间阈值
    
    async def check_system_health(self) -> dict:
        """检查系统健康状态"""
        
        # 检查 LangGraph 系统性能
        langgraph_health = await self._check_langgraph_health()
        
        # 如果 LangGraph 系统异常，自动禁用
        if (langgraph_health.error_rate > self.error_threshold or 
            langgraph_health.avg_response_time > self.response_time_threshold):
            
            await self._trigger_emergency_fallback("performance_degradation")
        
        return {
            "langgraph_healthy": langgraph_health.healthy,
            "auto_fallback_triggered": not langgraph_health.healthy,
            "metrics": langgraph_health.metrics
        }
    
    async def _trigger_emergency_fallback(self, reason: str):
        """触发紧急回退"""
        
        # 禁用 LangGraph
        await self._disable_langgraph_globally()
        
        # 发送告警
        await self._send_alert(
            f"Emergency fallback triggered: {reason}",
            severity="critical"
        )
        
        logger.critical(f"Emergency fallback to legacy system triggered: {reason}")
```

## 🔒 风险控制措施

### 1. 数据安全
```python
# 数据迁移安全措施
class SafeMigration:
    """安全迁移工具"""
    
    async def backup_before_migration(self):
        """迁移前备份"""
        # 备份现有数据
        # 创建回滚点
        pass
    
    async def validate_migration(self):
        """验证迁移结果"""
        # 数据完整性检查
        # 功能可用性测试
        pass
    
    async def rollback_if_needed(self):
        """必要时回滚"""
        # 检测到问题时自动回滚
        pass
```

### 2. 性能保护
```python
# 性能保护措施
class PerformanceGuard:
    """性能保护器"""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            expected_exception=Exception
        )
    
    @circuit_breaker
    async def protected_langgraph_call(self, request):
        """受保护的 LangGraph 调用"""
        # 如果连续失败，自动切换到传统系统
        return await langgraph_system.process(request)
```

### 3. 监控告警
```python
# 监控告警系统
class AlertManager:
    """告警管理器"""
    
    async def monitor_migration_health(self):
        """监控迁移健康状态"""
        
        # 检查关键指标
        metrics = await self._collect_key_metrics()
        
        # 触发告警条件
        if metrics.error_rate > 0.01:  # 1% 错误率
            await self._send_alert("High error rate detected", "warning")
        
        if metrics.response_time_p99 > 5000:  # P99 超过 5 秒
            await self._send_alert("High response time detected", "warning")
```

## 📊 成功指标

### 关键性能指标 (KPI)
1. **系统可用性**: > 99.9%
2. **API 响应时间**: P95 < 2秒
3. **错误率**: < 0.1%
4. **功能完整性**: 100% 向后兼容

### 业务指标
1. **@mention 使用率**: 目标 > 30%
2. **多智能体协作成功率**: 目标 > 95%
3. **用户满意度**: 目标 > 4.5/5.0
4. **Token 使用效率**: 提升 20%

### 技术指标
1. **代码覆盖率**: > 80%
2. **部署成功率**: > 99%
3. **回滚时间**: < 5分钟
4. **监控覆盖率**: > 95%

## 📅 时间线总结

| 阶段 | 周期 | 主要任务 | 成功标准 |
|------|------|----------|----------|
| 阶段1 | Week 1-2 | 基础设施准备 | 数据库扩展完成，配置部署成功 |
| 阶段2 | Week 2-4 | 核心服务开发 | LangGraph 引擎可用，特性开关正常 |
| 阶段3 | Week 3-5 | 智能体整合 | 现有智能体兼容，节点注册成功 |
| 阶段4 | Week 4-6 | 记忆系统优化 | Mem0 集成完成，性能提升 |
| 阶段5 | Week 5-7 | API 接口升级 | 新接口可用，向后兼容保持 |
| 阶段6 | Week 6-8 | 监控分析 | 完整监控部署，分析报告可用 |
| 阶段7 | Week 7-8 | 生产部署 | 生产环境稳定，灰度发布成功 |
| 阶段8 | Week 8+ | 持续优化 | 性能目标达成，用户反馈良好 |

这个迁移策略确保了在不影响现有系统稳定性的前提下，平滑地引入 LangGraph 多智能体协作功能。
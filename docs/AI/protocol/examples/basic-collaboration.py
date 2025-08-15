#!/usr/bin/env python3
"""
基础协作示例 (Basic Collaboration Example)

本示例展示了两个智能体如何使用多智能体协作协议进行基本的任务协作。
包含消息传递、任务分配、结果共享等核心功能。

功能演示:
1. 智能体注册和能力发布
2. 协作会话建立
3. 任务分配和执行
4. 结果共享和整合
5. 记忆存储和检索
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 协议相关的数据结构定义
class AgentCapabilityType(Enum):
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    KNOWLEDGE = "knowledge"
    TOOL_USAGE = "tool_usage"
    REASONING = "reasoning"

class MessageType(Enum):
    COLLABORATION_REQUEST = "collaboration_request"
    TASK_ASSIGNMENT = "task_assignment"
    RESULT_SHARING = "result_sharing"
    STATUS_UPDATE = "status_update"
    MEMORY_SHARE = "memory_share"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentCapability:
    """智能体能力定义"""
    name: str
    type: AgentCapabilityType
    description: str
    proficiency_level: float  # 0.0 - 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "proficiency_level": self.proficiency_level
        }

@dataclass
class AgentMessage:
    """智能体消息"""
    id: str
    type: MessageType
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class CollaborationTask:
    """协作任务"""
    task_id: str
    title: str
    description: str
    requirements: List[str]
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "assigned_agent": self.assigned_agent,
            "status": self.status.value,
            "result": self.result
        }

class MessageBroker:
    """简单的消息代理实现"""
    
    def __init__(self):
        self.message_queue: Dict[str, List[AgentMessage]] = {}
        self.subscribers: Dict[str, List[str]] = {}  # topic -> agent_ids
    
    async def publish_message(self, message: AgentMessage) -> bool:
        """发布消息"""
        try:
            # 添加到接收者的消息队列
            if message.recipient_id not in self.message_queue:
                self.message_queue[message.recipient_id] = []
            
            self.message_queue[message.recipient_id].append(message)
            
            print(f"📨 消息已发送: {message.sender_id} -> {message.recipient_id}")
            print(f"   类型: {message.type.value}")
            print(f"   内容: {json.dumps(message.content, ensure_ascii=False, indent=2)}")
            
            return True
        except Exception as e:
            print(f"❌ 消息发送失败: {e}")
            return False
    
    async def get_messages(self, agent_id: str) -> List[AgentMessage]:
        """获取智能体的消息"""
        messages = self.message_queue.get(agent_id, [])
        self.message_queue[agent_id] = []  # 清空已获取的消息
        return messages
    
    async def subscribe_topic(self, agent_id: str, topic: str):
        """订阅主题"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        if agent_id not in self.subscribers[topic]:
            self.subscribers[topic].append(agent_id)
    
    async def broadcast_to_topic(self, topic: str, message: AgentMessage):
        """向主题广播消息"""
        subscribers = self.subscribers.get(topic, [])
        for subscriber_id in subscribers:
            message.recipient_id = subscriber_id
            await self.publish_message(message)

class MemoryManager:
    """简单的记忆管理器实现"""
    
    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.access_log: List[Dict[str, Any]] = []
    
    async def store_memory(self, agent_id: str, memory_id: str, content: str, 
                          metadata: Dict[str, Any] = None) -> bool:
        """存储记忆"""
        try:
            memory = {
                "memory_id": memory_id,
                "creator_id": agent_id,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "access_count": 0
            }
            
            self.memories[memory_id] = memory
            
            print(f"🧠 记忆已存储: {memory_id}")
            print(f"   创建者: {agent_id}")
            print(f"   内容: {content[:100]}...")
            
            return True
        except Exception as e:
            print(f"❌ 记忆存储失败: {e}")
            return False
    
    async def retrieve_memory(self, requester_id: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """检索记忆"""
        if memory_id not in self.memories:
            return None
        
        memory = self.memories[memory_id].copy()
        memory["access_count"] += 1
        
        # 记录访问日志
        self.access_log.append({
            "requester_id": requester_id,
            "memory_id": memory_id,
            "accessed_at": datetime.utcnow().isoformat()
        })
        
        print(f"🔍 记忆已检索: {memory_id}")
        print(f"   请求者: {requester_id}")
        
        return memory
    
    async def search_memories(self, requester_id: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """搜索记忆"""
        results = []
        
        for memory_id, memory in self.memories.items():
            content = memory["content"].lower()
            if any(keyword.lower() in content for keyword in keywords):
                results.append(memory)
        
        print(f"🔎 记忆搜索完成: 找到 {len(results)} 条相关记忆")
        print(f"   请求者: {requester_id}")
        print(f"   关键词: {keywords}")
        
        return results

class BaseAgent:
    """基础智能体类"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.message_broker: Optional[MessageBroker] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.active_tasks: Dict[str, CollaborationTask] = {}
        self.collaboration_sessions: Dict[str, Dict[str, Any]] = {}
    
    def connect_to_infrastructure(self, message_broker: MessageBroker, 
                                memory_manager: MemoryManager):
        """连接到基础设施"""
        self.message_broker = message_broker
        self.memory_manager = memory_manager
        print(f"🔗 {self.name} 已连接到协作基础设施")
    
    async def register_capabilities(self):
        """注册智能体能力"""
        print(f"📋 {self.name} 正在注册能力:")
        for capability in self.capabilities:
            print(f"   - {capability.name}: {capability.description} (熟练度: {capability.proficiency_level:.2f})")
    
    async def send_message(self, recipient_id: str, message_type: MessageType, 
                          content: Dict[str, Any]) -> bool:
        """发送消息"""
        if not self.message_broker:
            print(f"❌ {self.name}: 消息代理未连接")
            return False
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        return await self.message_broker.publish_message(message)
    
    async def process_messages(self):
        """处理接收到的消息"""
        if not self.message_broker:
            return
        
        messages = await self.message_broker.get_messages(self.agent_id)
        
        for message in messages:
            await self.handle_message(message)
    
    async def handle_message(self, message: AgentMessage):
        """处理单个消息"""
        print(f"📬 {self.name} 收到消息:")
        print(f"   来自: {message.sender_id}")
        print(f"   类型: {message.type.value}")
        
        if message.type == MessageType.COLLABORATION_REQUEST:
            await self.handle_collaboration_request(message)
        elif message.type == MessageType.TASK_ASSIGNMENT:
            await self.handle_task_assignment(message)
        elif message.type == MessageType.RESULT_SHARING:
            await self.handle_result_sharing(message)
        elif message.type == MessageType.MEMORY_SHARE:
            await self.handle_memory_share(message)
        else:
            print(f"⚠️  未知消息类型: {message.type.value}")
    
    async def handle_collaboration_request(self, message: AgentMessage):
        """处理协作请求"""
        request_content = message.content
        session_id = request_content.get("session_id")
        
        print(f"🤝 {self.name} 收到协作请求 (会话: {session_id})")
        
        # 简单的协作接受逻辑
        response = {
            "session_id": session_id,
            "accepted": True,
            "capabilities": [cap.to_dict() for cap in self.capabilities]
        }
        
        await self.send_message(
            message.sender_id,
            MessageType.STATUS_UPDATE,
            response
        )
    
    async def handle_task_assignment(self, message: AgentMessage):
        """处理任务分配"""
        task_data = message.content.get("task")
        
        if not task_data:
            print(f"❌ {self.name}: 任务数据缺失")
            return
        
        task = CollaborationTask(
            task_id=task_data["task_id"],
            title=task_data["title"],
            description=task_data["description"],
            requirements=task_data["requirements"],
            assigned_agent=self.agent_id,
            status=TaskStatus.ASSIGNED
        )
        
        self.active_tasks[task.task_id] = task
        
        print(f"📋 {self.name} 接受任务: {task.title}")
        
        # 开始执行任务
        await self.execute_task(task)
    
    async def execute_task(self, task: CollaborationTask):
        """执行任务 - 子类需要重写此方法"""
        print(f"⚙️  {self.name} 开始执行任务: {task.title}")
        
        # 更新任务状态
        task.status = TaskStatus.IN_PROGRESS
        
        # 模拟任务执行
        await asyncio.sleep(2)
        
        # 设置任务结果
        task.result = {
            "message": f"任务 '{task.title}' 已由 {self.name} 完成",
            "completed_at": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id
        }
        task.status = TaskStatus.COMPLETED
        
        print(f"✅ {self.name} 完成任务: {task.title}")
        
        # 存储任务完成的记忆
        await self.store_task_memory(task)
    
    async def handle_result_sharing(self, message: AgentMessage):
        """处理结果分享"""
        result = message.content.get("result")
        task_id = message.content.get("task_id")
        
        print(f"📊 {self.name} 收到结果分享:")
        print(f"   任务ID: {task_id}")
        print(f"   结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    async def handle_memory_share(self, message: AgentMessage):
        """处理记忆分享"""
        memory_id = message.content.get("memory_id")
        
        if self.memory_manager and memory_id:
            memory = await self.memory_manager.retrieve_memory(self.agent_id, memory_id)
            if memory:
                print(f"🧠 {self.name} 接收到共享记忆: {memory_id}")
    
    async def store_task_memory(self, task: CollaborationTask):
        """存储任务记忆"""
        if not self.memory_manager:
            return
        
        memory_content = f"完成任务: {task.title}. 描述: {task.description}. 结果: {json.dumps(task.result, ensure_ascii=False)}"
        memory_id = f"task_memory_{task.task_id}_{self.agent_id}"
        
        metadata = {
            "task_id": task.task_id,
            "agent_id": self.agent_id,
            "task_type": "collaboration",
            "tags": ["task_completion", "collaboration"]
        }
        
        await self.memory_manager.store_memory(
            self.agent_id, memory_id, memory_content, metadata
        )

class DataAnalystAgent(BaseAgent):
    """数据分析师智能体"""
    
    def __init__(self):
        capabilities = [
            AgentCapability("data_analysis", AgentCapabilityType.COMPUTATION, "数据分析和统计", 0.9),
            AgentCapability("visualization", AgentCapabilityType.COMPUTATION, "数据可视化", 0.8),
            AgentCapability("pattern_recognition", AgentCapabilityType.REASONING, "模式识别", 0.85)
        ]
        super().__init__("data_analyst_001", "数据分析师 Alice", capabilities)
    
    async def execute_task(self, task: CollaborationTask):
        """执行数据分析任务"""
        print(f"📊 {self.name} 开始数据分析任务: {task.title}")
        
        task.status = TaskStatus.IN_PROGRESS
        
        # 模拟数据分析过程
        print(f"   🔍 正在分析数据...")
        await asyncio.sleep(3)
        
        print(f"   📈 生成统计报告...")
        await asyncio.sleep(2)
        
        # 生成分析结果
        analysis_result = {
            "data_points_analyzed": 1000,
            "patterns_found": [
                "用户活跃度在周末达到峰值",
                "年轻用户群体更偏爱移动端",
                "产品A的转化率比产品B高30%"
            ],
            "recommendations": [
                "增加周末的营销活动",
                "优化移动端用户体验",
                "重点推广产品A"
            ],
            "confidence_score": 0.92
        }
        
        task.result = {
            "analysis": analysis_result,
            "completed_at": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "processing_time_seconds": 5
        }
        task.status = TaskStatus.COMPLETED
        
        print(f"✅ {self.name} 完成数据分析任务")
        
        # 存储分析记忆
        await self.store_task_memory(task)

class ResearcherAgent(BaseAgent):
    """研究员智能体"""
    
    def __init__(self):
        capabilities = [
            AgentCapability("research", AgentCapabilityType.KNOWLEDGE, "信息研究和整理", 0.95),
            AgentCapability("synthesis", AgentCapabilityType.REASONING, "信息综合分析", 0.88),
            AgentCapability("fact_checking", AgentCapabilityType.REASONING, "事实核查", 0.90)
        ]
        super().__init__("researcher_001", "研究员 Bob", capabilities)
    
    async def execute_task(self, task: CollaborationTask):
        """执行研究任务"""
        print(f"🔬 {self.name} 开始研究任务: {task.title}")
        
        task.status = TaskStatus.IN_PROGRESS
        
        # 模拟研究过程
        print(f"   📚 正在收集资料...")
        await asyncio.sleep(2)
        
        print(f"   🔍 正在分析文献...")
        await asyncio.sleep(3)
        
        print(f"   📝 正在整理报告...")
        await asyncio.sleep(2)
        
        # 生成研究结果
        research_result = {
            "sources_reviewed": 25,
            "key_findings": [
                "多智能体系统在协作效率上比单智能体提升40%",
                "记忆共享机制能够减少重复工作30%",
                "共识算法的选择对系统性能有显著影响"
            ],
            "recommendations": [
                "采用分层记忆架构提升记忆检索效率",
                "实现动态共识机制适应不同场景",
                "建立智能体信誉系统提升协作质量"
            ],
            "research_quality": 0.89
        }
        
        task.result = {
            "research": research_result,
            "completed_at": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "research_depth": "comprehensive"
        }
        task.status = TaskStatus.COMPLETED
        
        print(f"✅ {self.name} 完成研究任务")
        
        # 存储研究记忆
        await self.store_task_memory(task)

class CollaborationOrchestrator:
    """协作编排器"""
    
    def __init__(self, message_broker: MessageBroker, memory_manager: MemoryManager):
        self.message_broker = message_broker
        self.memory_manager = memory_manager
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.registered_agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """注册智能体"""
        self.registered_agents[agent.agent_id] = agent
        agent.connect_to_infrastructure(self.message_broker, self.memory_manager)
        print(f"🎯 协作编排器已注册智能体: {agent.name}")
    
    async def initiate_collaboration(self, session_title: str, 
                                   description: str, 
                                   required_capabilities: List[str]) -> str:
        """发起协作"""
        session_id = str(uuid.uuid4())
        
        print(f"\n🚀 发起协作会话: {session_title}")
        print(f"   会话ID: {session_id}")
        print(f"   描述: {description}")
        print(f"   需要的能力: {required_capabilities}")
        
        # 选择合适的智能体
        selected_agents = await self.select_agents(required_capabilities)
        
        if not selected_agents:
            print("❌ 没有找到合适的智能体")
            return session_id
        
        # 创建协作会话
        session = {
            "session_id": session_id,
            "title": session_title,
            "description": description,
            "participants": [agent.agent_id for agent in selected_agents],
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "tasks": []
        }
        
        self.active_sessions[session_id] = session
        
        # 向选中的智能体发送协作请求
        for agent in selected_agents:
            await self.send_collaboration_request(agent.agent_id, session)
        
        return session_id
    
    async def select_agents(self, required_capabilities: List[str]) -> List[BaseAgent]:
        """选择合适的智能体"""
        selected_agents = []
        
        for agent in self.registered_agents.values():
            agent_capabilities = [cap.name for cap in agent.capabilities]
            
            # 简单的能力匹配
            if any(req_cap in agent_capabilities for req_cap in required_capabilities):
                selected_agents.append(agent)
        
        print(f"🎯 选中 {len(selected_agents)} 个智能体参与协作")
        for agent in selected_agents:
            print(f"   - {agent.name}")
        
        return selected_agents
    
    async def send_collaboration_request(self, agent_id: str, session: Dict[str, Any]):
        """发送协作请求"""
        content = {
            "session_id": session["session_id"],
            "title": session["title"],
            "description": session["description"],
            "participants": session["participants"]
        }
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.COLLABORATION_REQUEST,
            sender_id="orchestrator",
            recipient_id=agent_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        await self.message_broker.publish_message(message)
    
    async def assign_task(self, session_id: str, task_title: str, 
                         task_description: str, requirements: List[str], 
                         assigned_agent_id: str):
        """分配任务"""
        if session_id not in self.active_sessions:
            print(f"❌ 协作会话不存在: {session_id}")
            return
        
        task_id = str(uuid.uuid4())
        
        task = {
            "task_id": task_id,
            "title": task_title,
            "description": task_description,
            "requirements": requirements,
            "assigned_agent": assigned_agent_id,
            "status": "assigned",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # 添加到会话任务列表
        self.active_sessions[session_id]["tasks"].append(task)
        
        # 发送任务分配消息
        content = {
            "session_id": session_id,
            "task": task
        }
        
        message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.TASK_ASSIGNMENT,
            sender_id="orchestrator",
            recipient_id=assigned_agent_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        await self.message_broker.publish_message(message)
        
        print(f"📋 任务已分配: {task_title} -> {assigned_agent_id}")
    
    async def share_results_between_agents(self, session_id: str):
        """在智能体间共享结果"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        participants = session["participants"]
        
        print(f"\n📊 在协作会话中共享结果 (会话: {session_id})")
        
        # 获取所有完成的任务结果
        completed_tasks = []
        for agent_id in participants:
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                for task_id, task in agent.active_tasks.items():
                    if task.status == TaskStatus.COMPLETED and task.result:
                        completed_tasks.append(task)
        
        # 向所有参与者分享结果
        for task in completed_tasks:
            for agent_id in participants:
                if agent_id != task.assigned_agent:  # 不发送给执行者自己
                    content = {
                        "session_id": session_id,
                        "task_id": task.task_id,
                        "result": task.result,
                        "from_agent": task.assigned_agent
                    }
                    
                    message = AgentMessage(
                        id=str(uuid.uuid4()),
                        type=MessageType.RESULT_SHARING,
                        sender_id="orchestrator",
                        recipient_id=agent_id,
                        content=content,
                        timestamp=datetime.utcnow()
                    )
                    
                    await self.message_broker.publish_message(message)
        
        print(f"✅ 已共享 {len(completed_tasks)} 个任务的结果")

async def demo_basic_collaboration():
    """基础协作演示"""
    print("=" * 60)
    print("🎯 多智能体协作协议 - 基础协作演示")
    print("=" * 60)
    
    # 创建基础设施
    message_broker = MessageBroker()
    memory_manager = MemoryManager()
    orchestrator = CollaborationOrchestrator(message_broker, memory_manager)
    
    # 创建智能体
    data_analyst = DataAnalystAgent()
    researcher = ResearcherAgent()
    
    # 注册智能体
    orchestrator.register_agent(data_analyst)
    orchestrator.register_agent(researcher)
    
    # 注册智能体能力
    await data_analyst.register_capabilities()
    await researcher.register_capabilities()
    
    print("\n" + "="*60)
    
    # 发起协作
    session_id = await orchestrator.initiate_collaboration(
        session_title="多智能体协作效果研究",
        description="研究多智能体协作在提升工作效率方面的效果",
        required_capabilities=["data_analysis", "research", "synthesis"]
    )
    
    # 等待智能体处理协作请求
    await asyncio.sleep(1)
    
    # 处理协作请求消息
    await data_analyst.process_messages()
    await researcher.process_messages()
    
    print("\n" + "="*60)
    
    # 分配任务
    await orchestrator.assign_task(
        session_id=session_id,
        task_title="用户行为数据分析",
        task_description="分析用户在多智能体系统中的行为模式和偏好",
        requirements=["data_analysis", "pattern_recognition"],
        assigned_agent_id=data_analyst.agent_id
    )
    
    await orchestrator.assign_task(
        session_id=session_id,
        task_title="多智能体协作文献研究",
        task_description="研究多智能体协作的最新理论和实践",
        requirements=["research", "synthesis"],
        assigned_agent_id=researcher.agent_id
    )
    
    # 等待任务分配消息处理
    await asyncio.sleep(1)
    
    # 处理任务分配消息
    await data_analyst.process_messages()
    await researcher.process_messages()
    
    print("\n" + "="*60)
    
    # 等待任务执行完成
    print("⏳ 等待任务执行...")
    await asyncio.sleep(8)  # 等待任务完成
    
    print("\n" + "="*60)
    
    # 共享结果
    await orchestrator.share_results_between_agents(session_id)
    
    # 处理结果分享消息
    await asyncio.sleep(1)
    await data_analyst.process_messages()
    await researcher.process_messages()
    
    print("\n" + "="*60)
    print("🎊 协作演示完成!")
    
    # 显示最终状态
    print(f"\n📊 会话状态:")
    session = orchestrator.active_sessions[session_id]
    print(f"   会话ID: {session['session_id']}")
    print(f"   标题: {session['title']}")
    print(f"   参与者: {len(session['participants'])} 个")
    print(f"   任务数: {len(session['tasks'])} 个")
    
    print(f"\n🧠 记忆存储状态:")
    print(f"   总记忆数: {len(memory_manager.memories)}")
    print(f"   访问日志: {len(memory_manager.access_log)} 条")
    
    # 演示记忆搜索
    print(f"\n🔍 记忆搜索演示:")
    search_results = await memory_manager.search_memories(
        "demo_user", ["协作", "分析", "研究"]
    )
    print(f"   找到 {len(search_results)} 条相关记忆")

if __name__ == "__main__":
    # 运行基础协作演示
    asyncio.run(demo_basic_collaboration())

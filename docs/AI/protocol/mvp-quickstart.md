# MVP 快速开始指南

## 🎯 目标

用最简单的方式在 1-2 周内构建并运行基于 Mem0 的多智能体协作系统。

## 📋 前置条件

- Python 3.8+
- Redis 服务器
- Mem0 API 密钥（可选，用于托管服务）

## 🚀 第一步：环境准备

### 1. 创建项目目录

```bash
mkdir mvp-multi-agent-protocol
cd mvp-multi-agent-protocol
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install mem0ai redis asyncio aioredis fastapi uvicorn
```

### 3. 启动 Redis

```bash
# 使用 Docker
docker run -d -p 6379:6379 redis:7-alpine

# 或直接安装 Redis
# sudo apt-get install redis-server  # Ubuntu
# brew install redis                  # macOS
```

## 📝 第二步：核心代码实现

### 1. 创建智能体基础类 (mvp_agent.py)

```python
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Set
from mem0 import Memory
import redis.asyncio as aioredis

class MVPAgent:
    """MVP 智能体基础类"""

    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = "offline"

        # Mem0 记忆管理
        self.memory = Memory()

        # Redis 消息传递
        self.redis = None

        # 活跃会话
        self.active_sessions = set()

    async def initialize(self):
        """初始化智能体"""
        self.redis = await aioredis.from_url("redis://localhost:6379")
        await self._register_agent()
        asyncio.create_task(self._listen_for_messages())
        self.status = "online"
        print(f"✅ {self.name} 已上线")

    async def _register_agent(self):
        """注册智能体"""
        agent_info = {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status
        }
        await self.redis.hset("agents", self.agent_id, json.dumps(agent_info))
        await self.redis.sadd("online_agents", self.agent_id)

    async def send_message(self, recipient_id: str, message_type: str, content: Dict):
        """发送消息"""
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": self.agent_id,
            "recipient_id": recipient_id,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.redis.lpush(f"messages:{recipient_id}", json.dumps(message))
        await self.redis.publish(f"notify:{recipient_id}", "new_message")

    async def store_memory(self, content: str, session_id: str = None):
        """存储记忆到 Mem0"""
        messages = [{"role": "assistant", "content": content}]
        self.memory.add(messages, user_id=self.agent_id)

        if session_id:
            self.memory.add(messages, user_id=session_id)

    async def search_memory(self, query: str, session_id: str = None, limit: int = 3):
        """搜索记忆"""
        agent_memories = self.memory.search(query=query, user_id=self.agent_id, limit=limit)

        session_memories = []
        if session_id:
            session_memories = self.memory.search(query=query, user_id=session_id, limit=limit)

        return {
            "agent_memories": agent_memories,
            "session_memories": session_memories
        }

    async def _listen_for_messages(self):
        """监听消息"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"notify:{self.agent_id}")

        async for message in pubsub.listen():
            if message['type'] == 'message':
                await self._process_incoming_messages()

    async def _process_incoming_messages(self):
        """处理消息"""
        while True:
            raw_message = await self.redis.rpop(f"messages:{self.agent_id}")
            if not raw_message:
                break

            message = json.loads(raw_message)
            await self.handle_message(message)

    async def handle_message(self, message: Dict):
        """处理消息 - 子类重写"""
        print(f"{self.name} 收到消息: {message}")
```

### 2. 创建协作协调器 (mvp_coordinator.py)

```python
import asyncio
import json
import uuid
from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime
from mem0 import Memory
import redis.asyncio as aioredis

@dataclass
class CollaborationSession:
    session_id: str
    title: str
    participants: Set[str]
    status: str
    created_at: str
    tasks: List[Dict] = None

class MVPCollaborationCoordinator:
    """协作协调器"""

    def __init__(self):
        self.redis = None
        self.memory = Memory()
        self.active_sessions: Dict[str, CollaborationSession] = {}

    async def initialize(self):
        """初始化"""
        self.redis = await aioredis.from_url("redis://localhost:6379")
        print("🎯 协作协调器已启动")

    async def create_collaboration_session(
        self, title: str, required_capabilities: List[str], initiator_id: str
    ) -> str:
        """创建协作会话"""
        session_id = str(uuid.uuid4())

        # 查找智能体
        suitable_agents = await self._find_agents_by_capabilities(required_capabilities)

        if not suitable_agents:
            raise ValueError("没有找到合适的智能体")

        # 创建会话
        session = CollaborationSession(
            session_id=session_id,
            title=title,
            participants=set(suitable_agents + [initiator_id]),
            status="active",
            created_at=datetime.utcnow().isoformat(),
            tasks=[]
        )

        self.active_sessions[session_id] = session

        # 通知参与者
        await self._notify_participants(session)

        # 存储到 Mem0
        session_info = f"协作会话 '{title}' 已创建，参与者: {', '.join(session.participants)}"
        self.memory.add([{"role": "system", "content": session_info}], user_id=session_id)

        return session_id

    async def _find_agents_by_capabilities(self, capabilities: List[str]) -> List[str]:
        """查找智能体"""
        suitable_agents = []

        try:
            online_agents = await self.redis.smembers("online_agents")

            for agent_id in online_agents:
                agent_info_json = await self.redis.hget("agents", agent_id.decode())
                if agent_info_json:
                    agent_info = json.loads(agent_info_json)
                    agent_capabilities = agent_info.get("capabilities", [])

                    if any(cap in agent_capabilities for cap in capabilities):
                        suitable_agents.append(agent_id.decode())
        except Exception as e:
            print(f"查找智能体失败: {e}")

        return suitable_agents

    async def _notify_participants(self, session: CollaborationSession):
        """通知参与者"""
        notification = {
            "type": "collaboration_invite",
            "session_id": session.session_id,
            "title": session.title,
            "participants": list(session.participants)
        }

        for participant_id in session.participants:
            if participant_id.startswith("user_"):
                continue

            message = {
                "id": str(uuid.uuid4()),
                "sender_id": "system",
                "recipient_id": participant_id,
                "type": "collaboration_invite",
                "content": notification,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.redis.lpush(f"messages:{participant_id}", json.dumps(message))
            await self.redis.publish(f"notify:{participant_id}", "new_message")

    async def add_task(self, session_id: str, task_description: str, assigned_to: str = None):
        """添加任务"""
        if session_id not in self.active_sessions:
            raise ValueError("会话不存在")

        task = {
            "task_id": str(uuid.uuid4()),
            "description": task_description,
            "assigned_to": assigned_to,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        self.active_sessions[session_id].tasks.append(task)

        # 存储到 Mem0
        task_info = f"新任务: {task_description}"
        if assigned_to:
            task_info += f" (分配给: {assigned_to})"

        self.memory.add([{"role": "system", "content": task_info}], user_id=session_id)

        # 通知智能体
        if assigned_to and not assigned_to.startswith("user_"):
            await self._notify_task_assignment(session_id, task, assigned_to)

    async def _notify_task_assignment(self, session_id: str, task: Dict, assigned_to: str):
        """通知任务分配"""
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": "system",
            "recipient_id": assigned_to,
            "type": "task_assignment",
            "content": {"session_id": session_id, "task": task},
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.redis.lpush(f"messages:{assigned_to}", json.dumps(message))
        await self.redis.publish(f"notify:{assigned_to}", "new_message")

    async def get_session_context(self, session_id: str, query: str = "") -> Dict:
        """获取会话上下文"""
        if not query:
            query = "协作会话的所有活动和任务"

        memories = self.memory.search(query=query, user_id=session_id, limit=10)

        return {
            "session_id": session_id,
            "memories": memories,
            "session_info": self.active_sessions.get(session_id)
        }
```

### 3. 创建示例智能体 (demo_agents.py)

```python
from mvp_agent import MVPAgent
import asyncio

class CodeAgent(MVPAgent):
    """代码智能体"""

    def __init__(self):
        super().__init__(
            agent_id="code_agent_001",
            name="代码助手",
            capabilities=["code_generation", "code_review", "debugging"]
        )

    async def handle_message(self, message: dict):
        """处理消息"""
        print(f"🤖 {self.name} 收到: {message['type']}")

        if message["type"] == "collaboration_invite":
            await self._handle_collaboration_invite(message["content"])
        elif message["type"] == "task_assignment":
            await self._handle_task_assignment(message["content"])

    async def _handle_collaboration_invite(self, content: dict):
        """处理协作邀请"""
        session_id = content["session_id"]
        self.active_sessions.add(session_id)
        print(f"✅ {self.name} 加入会话: {content['title']}")

        await self.store_memory(f"加入协作: {content['title']}", session_id)

    async def _handle_task_assignment(self, content: dict):
        """处理任务分配"""
        task = content["task"]
        session_id = content["session_id"]

        print(f"📋 {self.name} 收到任务: {task['description']}")

        # 模拟处理
        await asyncio.sleep(1)

        code_result = f"""
# 根据任务生成的代码
import pandas as pd

def process_data(filename):
    df = pd.read_csv(filename)
    return df.describe()
"""

        await self.store_memory(f"任务: {task['description']}\n代码: {code_result}", session_id)
        print(f"✅ {self.name} 完成任务")

class AnalysisAgent(MVPAgent):
    """分析智能体"""

    def __init__(self):
        super().__init__(
            agent_id="analysis_agent_001",
            name="数据分析师",
            capabilities=["data_analysis", "report_generation"]
        )

    async def handle_message(self, message: dict):
        """处理消息"""
        print(f"📊 {self.name} 收到: {message['type']}")

        if message["type"] == "collaboration_invite":
            await self._handle_collaboration_invite(message["content"])
        elif message["type"] == "task_assignment":
            await self._handle_task_assignment(message["content"])

    async def _handle_collaboration_invite(self, content: dict):
        """处理协作邀请"""
        session_id = content["session_id"]
        self.active_sessions.add(session_id)
        print(f"✅ {self.name} 加入会话: {content['title']}")

        await self.store_memory(f"加入协作: {content['title']}", session_id)

    async def _handle_task_assignment(self, content: dict):
        """处理任务分配"""
        task = content["task"]
        session_id = content["session_id"]

        print(f"📋 {self.name} 收到任务: {task['description']}")

        # 搜索相关记忆
        memories = await self.search_memory("代码", session_id)

        analysis_result = f"""
分析报告:
1. 代码质量: 良好
2. 性能评估: 适合中小型数据
3. 优化建议: 添加错误处理
4. 相关记忆: {len(memories.get('session_memories', []))}条
"""

        await self.store_memory(f"分析: {task['description']}\n结果: {analysis_result}", session_id)
        print(f"✅ {self.name} 完成分析")
```

### 4. 创建演示脚本 (demo.py)

```python
import asyncio
from mvp_coordinator import MVPCollaborationCoordinator
from demo_agents import CodeAgent, AnalysisAgent

async def run_demo():
    """运行演示"""
    print("🚀 启动多智能体协作演示")
    print("=" * 40)

    # 1. 初始化
    coordinator = MVPCollaborationCoordinator()
    await coordinator.initialize()

    # 2. 创建智能体
    code_agent = CodeAgent()
    analysis_agent = AnalysisAgent()

    await code_agent.initialize()
    await analysis_agent.initialize()

    await asyncio.sleep(1)  # 等待注册完成

    # 3. 创建协作会话
    session_id = await coordinator.create_collaboration_session(
        title="数据处理项目",
        required_capabilities=["code_generation", "data_analysis"],
        initiator_id="user_001"
    )

    print(f"✅ 会话创建: {session_id}")

    # 4. 添加任务
    await coordinator.add_task(
        session_id,
        "生成CSV数据处理代码",
        assigned_to=code_agent.agent_id
    )

    await coordinator.add_task(
        session_id,
        "分析代码性能",
        assigned_to=analysis_agent.agent_id
    )

    # 5. 等待处理
    await asyncio.sleep(3)

    # 6. 获取结果
    context = await coordinator.get_session_context(session_id)

    print(f"\n📊 会话总结:")
    print(f"记忆数量: {len(context['memories']['results']) if context['memories'] else 0}")

    if context['session_info']:
        info = context['session_info']
        print(f"标题: {info.title}")
        print(f"参与者: {len(info.participants)}")
        print(f"任务数: {len(info.tasks)}")

    print("\n🎉 演示完成!")

if __name__ == "__main__":
    asyncio.run(run_demo())
```

## 🎮 第三步：运行演示

```bash
# 确保 Redis 运行中
redis-cli ping  # 应该返回 PONG

# 运行演示
python demo.py
```

## 📊 预期输出

```
🚀 启动多智能体协作演示
========================================
🎯 协作协调器已启动
✅ 代码助手 已上线
✅ 数据分析师 已上线
✅ 会话创建: abcd1234-5678-90ef-ghij-klmnopqrstuv
🤖 代码助手 收到: collaboration_invite
✅ 代码助手 加入会话: 数据处理项目
📊 数据分析师 收到: collaboration_invite
✅ 数据分析师 加入会话: 数据处理项目
📋 代码助手 收到任务: 生成CSV数据处理代码
✅ 代码助手 完成任务
📋 数据分析师 收到任务: 分析代码性能
✅ 数据分析师 完成分析

📊 会话总结:
记忆数量: 4
标题: 数据处理项目
参与者: 3
任务数: 2

🎉 演示完成!
```

## ✅ 成功指标

- ✅ 智能体成功注册和发现
- ✅ 消息传递正常工作
- ✅ 协作会话创建成功
- ✅ Mem0 记忆存储和检索正常
- ✅ 任务分配和执行完整

## 🔮 下一步

1. **添加 Web 界面**: 使用 FastAPI 创建可视化界面
2. **更多智能体**: 添加不同类型的智能体
3. **错误处理**: 增强异常处理和重试机制
4. **配置管理**: 添加配置文件支持
5. **部署优化**: Docker 容器化部署

## 🆘 故障排除

### Redis 连接失败

```bash
# 检查Redis状态
redis-cli ping

# 重启Redis
docker restart <redis-container-id>
```

### Mem0 API 问题

```bash
# 设置API密钥（如果使用托管服务）
export MEM0_API_KEY="your_api_key"

# 或使用本地部署
# 查看 Mem0 文档进行本地配置
```

### 端口冲突

```bash
# 检查端口使用
lsof -i :6379

# 修改Redis端口
docker run -d -p 6380:6379 redis:7-alpine
# 然后在代码中修改连接URL
```

---

这个快速开始指南让您能在短时间内体验完整的多智能体协作流程，为后续扩展奠定基础。

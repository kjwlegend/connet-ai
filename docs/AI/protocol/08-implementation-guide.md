# 实现指南 (Implementation Guide) - MVP 优先版

## 🎯 概览

本指南提供基于 **Mem0** 的多智能体协作协议 **MVP 实现指导**，专注于快速构建最小可执行方案，利用成熟的开源解决方案避免重复造轮子。

> **重要**: 本版本基于 [Mem0](https://github.com/mem0ai/mem0) 项目重新设计，大幅简化了原有的复杂架构，聚焦于 1-2 周内可交付的 MVP 方案。

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆协议实现模板
git clone https://github.com/connet-ai/multi-agent-protocol.git
cd multi-agent-protocol

# 安装依赖
pip install -r requirements.txt
npm install  # 如果包含前端组件

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 2. 基础组件实现 (MVP 版本)

#### 2.1 智能体基础类 (基于 Mem0)

```python
# mvp_agent.py
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from mem0 import Memory  # 使用 Mem0 替代自定义记忆管理
import redis.asyncio as aioredis

class MVPAgent:
    """MVP 智能体基础类 - 极简设计，集成 Mem0"""

    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.status = "offline"

        # 使用 Mem0 进行记忆管理
        self.memory = Memory()

        # 简化的消息传递 (Redis)
        self.redis = None

        # 活跃协作会话
        self.active_sessions = set()

    async def initialize(self):
        """初始化智能体 (MVP 简化版)"""
        # 连接 Redis (简化的消息传递)
        self.redis = await aioredis.from_url("redis://localhost:6379")

        # 注册智能体到发现服务
        await self._register_agent()

        # 启动消息监听
        asyncio.create_task(self._listen_for_messages())

        self.status = "online"
        print(f"智能体 {self.name} 已上线")

    async def _register_agent(self):
        """注册智能体到发现服务"""
        agent_info = {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "status": self.status
        }
        await self.redis.hset("agents", self.agent_id, json.dumps(agent_info))
        await self.redis.sadd("online_agents", self.agent_id)

    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务 - 子类必须实现"""
        pass

    @abstractmethod
    async def handle_collaboration_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理协作请求 - 子类必须实现"""
        pass

    async def send_message(self, recipient_id: str, message_type: str, content: Dict):
        """发送消息 (简化版)"""
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": self.agent_id,
            "recipient_id": recipient_id,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        # 发送到 Redis 队列
        await self.redis.lpush(f"messages:{recipient_id}", json.dumps(message))

        # 通知接收者
        await self.redis.publish(f"notify:{recipient_id}", "new_message")

    async def store_memory(self, content: str, session_id: str = None):
        """存储记忆到 Mem0 (简化版)"""
        messages = [{"role": "assistant", "content": content}]

        # 存储到不同级别的记忆
        self.memory.add(messages, user_id=self.agent_id)  # Agent 级记忆

        if session_id:
            self.memory.add(messages, user_id=session_id)  # Session 级记忆

    async def search_memory(self, query: str, session_id: str = None, limit: int = 3):
        """从 Mem0 搜索相关记忆"""
        # 搜索 Agent 级记忆
        agent_memories = self.memory.search(
            query=query,
            user_id=self.agent_id,
            limit=limit
        )

        session_memories = []
        if session_id:
            # 搜索 Session 级记忆
            session_memories = self.memory.search(
                query=query,
                user_id=session_id,
                limit=limit
            )

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
        """处理收到的消息"""
        while True:
            raw_message = await self.redis.rpop(f"messages:{self.agent_id}")
            if not raw_message:
                break

            message = json.loads(raw_message)
            await self.handle_message(message)

    async def handle_message(self, message: Dict):
        """处理消息 - 子类实现"""
        print(f"{self.name} 收到消息: {message}")

    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态 (简化版)"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "capabilities": self.capabilities,
            "active_sessions": list(self.active_sessions),
            "timestamp": datetime.utcnow().isoformat()
        }

# 示例智能体实现
class CodeAgent(MVPAgent):
    """代码智能体示例"""

    def __init__(self):
        super().__init__(
            agent_id="code_agent_001",
            name="代码助手",
            capabilities=["code_generation", "code_review", "debugging"]
        )

    async def handle_message(self, message: Dict):
        """处理收到的消息"""
        if message["type"] == "collaboration_invite":
            await self._handle_collaboration_invite(message["content"])
        elif message["type"] == "code_request":
            await self._handle_code_request(message["content"])

    async def _handle_code_request(self, content: Dict):
        """处理代码请求"""
        request = content["request"]
        session_id = content.get("session_id")

        # 搜索相关记忆
        memories = await self.search_memory(request, session_id)

        # 生成代码 (简化实现)
        code_response = f"# 根据请求 '{request}' 生成的代码\nprint('Hello from Code Agent!')"

        # 存储结果到记忆
        await self.store_memory(
            f"代码请求: {request}\n生成代码: {code_response}",
            session_id
        )

        # 发送响应
        await self.send_message(
            content["requester_id"],
            "code_response",
            {"code": code_response, "request": request}
        )
```

#### 2.2 协作协调器 (基于 Mem0)

```python
# mvp_coordinator.py - 完整的协作协调器实现
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
    """协作会话"""
    session_id: str
    title: str
    participants: Set[str]
    status: str  # active, completed, failed
    created_at: str
    tasks: List[Dict] = None

class MVPCollaborationCoordinator:
    """MVP 协作协调器 - 基于 Mem0 的简化实现"""

    def __init__(self):
        self.redis = None
        self.memory = Memory()  # Mem0 全局记忆管理
        self.active_sessions: Dict[str, CollaborationSession] = {}

    async def initialize(self):
        """初始化协调器"""
        self.redis = await aioredis.from_url("redis://localhost:6379")
        print("协作协调器已启动")

    async def create_collaboration_session(
        self,
        title: str,
        required_capabilities: List[str],
        initiator_id: str
    ) -> str:
        """创建协作会话"""
        session_id = str(uuid.uuid4())

        # 查找具备所需能力的智能体
        suitable_agents = await self._find_agents_by_capabilities(required_capabilities)

        if len(suitable_agents) < 1:  # MVP: 至少需要1个智能体
            raise ValueError("没有找到合适的智能体来完成协作")

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

        # 存储会话信息到 Mem0
        session_info = f"协作会话 '{title}' 已创建，参与者: {', '.join(session.participants)}"
        self.memory.add(
            [{"role": "system", "content": session_info}],
            user_id=session_id
        )

        return session_id

    async def _find_agents_by_capabilities(self, capabilities: List[str]) -> List[str]:
        """根据能力查找智能体"""
        suitable_agents = []

        try:
            # 获取所有在线智能体
            online_agents = await self.redis.smembers("online_agents")

            for agent_id in online_agents:
                agent_info_json = await self.redis.hget("agents", agent_id.decode())
                if agent_info_json:
                    agent_info = json.loads(agent_info_json)
                    agent_capabilities = agent_info.get("capabilities", [])

                    # 检查是否有匹配的能力
                    if any(cap in agent_capabilities for cap in capabilities):
                        suitable_agents.append(agent_id.decode())
        except Exception as e:
            print(f"查找智能体失败: {e}")

        return suitable_agents

    async def _notify_participants(self, session: CollaborationSession):
        """通知参与者加入协作"""
        notification = {
            "type": "collaboration_invite",
            "session_id": session.session_id,
            "title": session.title,
            "participants": list(session.participants)
        }

        for participant_id in session.participants:
            if participant_id.startswith("user_"):  # 跳过用户通知
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

    async def add_task_to_session(
        self,
        session_id: str,
        task_description: str,
        assigned_to: str = None
    ):
        """向会话添加任务"""
        if session_id not in self.active_sessions:
            raise ValueError("协作会话不存在")

        task = {
            "task_id": str(uuid.uuid4()),
            "description": task_description,
            "assigned_to": assigned_to,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        session = self.active_sessions[session_id]
        session.tasks.append(task)

        # 存储任务信息到 Mem0
        task_info = f"新任务: {task_description}"
        if assigned_to:
            task_info += f" (分配给: {assigned_to})"

        self.memory.add(
            [{"role": "system", "content": task_info}],
            user_id=session_id
        )

        # 通知被分配的智能体
        if assigned_to and not assigned_to.startswith("user_"):
            await self._notify_task_assignment(session_id, task, assigned_to)

    async def _notify_task_assignment(self, session_id: str, task: Dict, assigned_to: str):
        """通知任务分配"""
        message = {
            "id": str(uuid.uuid4()),
            "sender_id": "system",
            "recipient_id": assigned_to,
            "type": "task_assignment",
            "content": {
                "session_id": session_id,
                "task": task
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        await self.redis.lpush(f"messages:{assigned_to}", json.dumps(message))
        await self.redis.publish(f"notify:{assigned_to}", "new_message")

    async def get_session_context(self, session_id: str, query: str = "") -> Dict:
        """获取会话上下文（使用 Mem0）"""
        if not query:
            query = "协作会话的所有活动和任务"

        # 从 Mem0 搜索会话相关记忆
        memories = self.memory.search(
            query=query,
            user_id=session_id,
            limit=10
        )

        return {
            "session_id": session_id,
            "memories": memories,
            "session_info": self.active_sessions.get(session_id)
        }

    async def get_all_sessions(self) -> Dict[str, CollaborationSession]:
        """获取所有活动会话"""
        return self.active_sessions

    async def complete_session(self, session_id: str):
        """完成协作会话"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].status = "completed"

            # 记录会话完成
            completion_info = f"协作会话 '{self.active_sessions[session_id].title}' 已完成"
            self.memory.add(
                [{"role": "system", "content": completion_info}],
                user_id=session_id
            )
```

#### 2.3 MVP 演示脚本

基于 Mem0 的简化实现不需要复杂的自定义记忆管理，我们直接利用 Mem0 的成熟解决方案。

```python
# mvp_demo.py
import asyncio
import json
import uuid
from datetime import datetime
from mvp_agent import MVPAgent
from mvp_coordinator import MVPCollaborationCoordinator

# 示例智能体实现
class CodeAgent(MVPAgent):
    """代码智能体示例"""

    def __init__(self):
        super().__init__(
            agent_id="code_agent_001",
            name="代码助手",
            capabilities=["code_generation", "code_review", "debugging"]
        )

    async def _create_tables(self):
        """创建数据库表"""
        async with self.pg_pool.acquire() as conn:
            # 创建记忆表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id VARCHAR(64) PRIMARY KEY,
                    agent_id VARCHAR(64) NOT NULL,
                    title VARCHAR(200),
                    content TEXT NOT NULL,
                    memory_type VARCHAR(20) NOT NULL,
                    access_level VARCHAR(20) NOT NULL,
                    quality_score FLOAT DEFAULT 0.5,
                    trust_score FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    metadata JSONB
                )
            ''')

            # 创建访问控制表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_access (
                    memory_id VARCHAR(64),
                    agent_id VARCHAR(64),
                    access_type VARCHAR(20),
                    granted_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY (memory_id, agent_id)
                )
            ''')

            # 创建记忆关系表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS memory_relations (
                    memory_id_1 VARCHAR(64),
                    memory_id_2 VARCHAR(64),
                    relation_type VARCHAR(50),
                    strength FLOAT DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT NOW(),
                    PRIMARY KEY (memory_id_1, memory_id_2)
                )
            ''')

    async def store_memory(self, memory: Dict[str, Any]) -> bool:
        """存储记忆"""
        try:
            async with self.pg_pool.acquire() as conn:
                # 插入记忆记录
                await conn.execute('''
                    INSERT INTO memories (
                        memory_id, agent_id, title, content, memory_type,
                        access_level, quality_score, trust_score, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (memory_id) DO UPDATE SET
                        content = $4,
                        updated_at = NOW(),
                        metadata = $9
                ''',
                    memory["memory_id"],
                    memory["agent_id"],
                    memory.get("title", ""),
                    memory["content"],
                    memory["type"],
                    memory.get("access_level", "private"),
                    memory.get("quality_score", 0.5),
                    memory.get("trust_score", 0.5),
                    json.dumps(memory.get("metadata", {}))
                )

            # 生成并存储向量嵌入
            await self._store_embedding(memory["memory_id"], memory["content"])

            # 缓存到 Redis
            await self._cache_memory(memory)

            print(f"记忆已存储: {memory['memory_id']}")
            return True

        except Exception as e:
            print(f"记忆存储失败: {e}")
            return False

    async def retrieve_memory(self, memory_id: str, requester_id: str) -> Optional[Dict[str, Any]]:
        """检索记忆"""
        try:
            # 检查访问权限
            if not await self._check_access_permission(memory_id, requester_id):
                print(f"访问被拒绝: {requester_id} -> {memory_id}")
                return None

            # 首先尝试从缓存获取
            cached_memory = await self._get_cached_memory(memory_id)
            if cached_memory:
                await self._log_memory_access(memory_id, requester_id)
                return cached_memory

            # 从数据库获取
            async with self.pg_pool.acquire() as conn:
                row = await conn.fetchrow('''
                    SELECT * FROM memories WHERE memory_id = $1
                ''', memory_id)

                if row:
                    memory = dict(row)
                    memory['metadata'] = json.loads(memory['metadata'] or '{}')

                    # 缓存结果
                    await self._cache_memory(memory)

                    # 记录访问日志
                    await self._log_memory_access(memory_id, requester_id)

                    return memory

            return None

        except Exception as e:
            print(f"记忆检索失败: {e}")
            return None

    async def search_memories(self, query: str, requester_id: str,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """搜索记忆"""
        try:
            # 生成查询向量
            query_vector = await self._generate_embedding(query)

            # 向量相似度搜索
            similar_memory_ids = await self._vector_search(query_vector, limit * 2)

            # 获取记忆详情并过滤权限
            results = []
            for memory_id, similarity in similar_memory_ids:
                if await self._check_access_permission(memory_id, requester_id):
                    memory = await self.retrieve_memory(memory_id, requester_id)
                    if memory:
                        memory['similarity_score'] = similarity
                        results.append(memory)

                if len(results) >= limit:
                    break

            print(f"搜索完成: 找到 {len(results)} 条相关记忆")
            return results

        except Exception as e:
            print(f"记忆搜索失败: {e}")
            return []

    async def _check_access_permission(self, memory_id: str, requester_id: str) -> bool:
        """检查访问权限"""
        try:
            async with self.pg_pool.acquire() as conn:
                # 检查是否为创建者
                creator_row = await conn.fetchrow('''
                    SELECT agent_id FROM memories WHERE memory_id = $1
                ''', memory_id)

                if creator_row and creator_row['agent_id'] == requester_id:
                    return True

                # 检查显式授权
                access_row = await conn.fetchrow('''
                    SELECT 1 FROM memory_access
                    WHERE memory_id = $1 AND agent_id = $2
                ''', memory_id, requester_id)

                if access_row:
                    return True

                # 检查公共访问
                public_row = await conn.fetchrow('''
                    SELECT access_level FROM memories
                    WHERE memory_id = $1 AND access_level = 'public'
                ''', memory_id)

                return bool(public_row)

        except Exception as e:
            print(f"权限检查失败: {e}")
            return False

    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # 简化实现 - 实际应该使用真实的嵌入模型
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # 转换为向量 (示例)
        vector = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, min(len(text_hash), 128), 2)]
        return vector

    async def _store_embedding(self, memory_id: str, content: str):
        """存储向量嵌入"""
        embedding = await self._generate_embedding(content)
        # 存储到向量数据库
        # await self.vector_client.store_vector(memory_id, embedding)

    async def _vector_search(self, query_vector: List[float], limit: int) -> List[Tuple[str, float]]:
        """向量相似度搜索"""
        # 简化实现 - 实际应该使用向量数据库
        return [("memory_1", 0.8), ("memory_2", 0.7)]  # 示例结果

    async def _cache_memory(self, memory: Dict[str, Any]):
        """缓存记忆到 Redis"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            cache_key = f"memory:{memory['memory_id']}"
            await redis.setex(cache_key, 3600, json.dumps(memory, default=str))
        except Exception as e:
            print(f"记忆缓存失败: {e}")

    async def _get_cached_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """从缓存获取记忆"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            cache_key = f"memory:{memory_id}"
            cached_data = await redis.get(cache_key)

            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None

    async def _log_memory_access(self, memory_id: str, requester_id: str):
        """记录记忆访问日志"""
        try:
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            log_entry = {
                "memory_id": memory_id,
                "requester_id": requester_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            await redis.lpush("memory_access_log", json.dumps(log_entry))
        except Exception as e:
            print(f"访问日志记录失败: {e}")
```

## 🏗️ 部署架构

### 1. Docker 容器化部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  # API 网关
  api-gateway:
    build: ./gateway
    ports:
      - "80:80"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  # 协作服务
  collaboration-service:
    build: ./collaboration
    ports:
      - "8001:8001"
    environment:
      - POSTGRES_URL=postgresql://postgres:password@postgres:5432/collaboration
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # 记忆服务
  memory-service:
    build: ./memory
    ports:
      - "8002:8002"
    environment:
      - POSTGRES_URL=postgresql://postgres:password@postgres:5432/memory
      - REDIS_URL=redis://redis:6379
      - VECTOR_DB_URL=http://vector-db:8000
    depends_on:
      - postgres
      - redis
      - vector-db

  # 数据库
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: collaboration
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # 缓存
  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

  # 向量数据库
  vector-db:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - vector_data:/qdrant/storage

  # 监控
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  postgres_data:
  redis_data:
  vector_data:
```

### 2. Kubernetes 部署

```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: collaboration-service
  labels:
    app: collaboration-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: collaboration-service
  template:
    metadata:
      labels:
        app: collaboration-service
    spec:
      containers:
        - name: collaboration-service
          image: connet-ai/collaboration-service:latest
          ports:
            - containerPort: 8001
          env:
            - name: POSTGRES_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: postgres-url
            - name: REDIS_URL
              value: "redis://redis-service:6379"
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8001
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: collaboration-service
spec:
  selector:
    app: collaboration-service
  ports:
    - protocol: TCP
      port: 8001
      targetPort: 8001
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: collaboration-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: collaboration-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## 📊 监控和观察性

### 1. 指标收集

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# 定义指标
message_counter = Counter('agent_messages_total', 'Total messages', ['agent_id', 'message_type'])
task_duration = Histogram('agent_task_duration_seconds', 'Task duration', ['agent_id', 'task_type'])
active_agents = Gauge('active_agents_total', 'Number of active agents')
memory_operations = Counter('memory_operations_total', 'Memory operations', ['operation_type', 'status'])

def track_metrics(metric_type: str):
    """装饰器：自动收集指标"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # 记录成功指标
                if metric_type == 'task':
                    task_duration.labels(
                        agent_id=args[0].agent_id,
                        task_type=kwargs.get('task_type', 'unknown')
                    ).observe(time.time() - start_time)

                return result

            except Exception as e:
                # 记录错误指标
                if metric_type == 'memory':
                    memory_operations.labels(
                        operation_type=func.__name__,
                        status='error'
                    ).inc()
                raise

        return wrapper
    return decorator

class MetricsCollector:
    """指标收集器"""

    def __init__(self, port: int = 8000):
        self.port = port
        self.start_time = time.time()

    def start_metrics_server(self):
        """启动指标服务器"""
        start_http_server(self.port)
        print(f"指标服务器已启动: http://localhost:{self.port}/metrics")

    def record_message_sent(self, agent_id: str, message_type: str):
        """记录消息发送"""
        message_counter.labels(agent_id=agent_id, message_type=message_type).inc()

    def record_agent_online(self):
        """记录智能体上线"""
        active_agents.inc()

    def record_agent_offline(self):
        """记录智能体下线"""
        active_agents.dec()

    def get_system_health(self) -> dict:
        """获取系统健康状态"""
        uptime = time.time() - self.start_time
        return {
            "status": "healthy",
            "uptime_seconds": uptime,
            "active_agents": active_agents._value._value,
            "total_messages": sum(message_counter._metrics.values()),
            "timestamp": time.time()
        }
```

### 2. 日志配置

```python
# logging_config.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    """结构化日志记录器"""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # 创建处理器
        handler = logging.StreamHandler()
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        """记录信息日志"""
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """记录错误日志"""
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        self.logger.debug(message, extra=kwargs)

class StructuredFormatter(logging.Formatter):
    """结构化日志格式器"""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # 添加额外字段
        if hasattr(record, 'agent_id'):
            log_entry['agent_id'] = record.agent_id
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id
        if hasattr(record, 'trace_id'):
            log_entry['trace_id'] = record.trace_id

        return json.dumps(log_entry)
```

## 🔧 配置管理

### 1. 配置文件结构

```yaml
# config.yml
system:
  name: "multi-agent-protocol"
  version: "1.0.0"
  environment: "production"

services:
  collaboration:
    host: "0.0.0.0"
    port: 8001
    workers: 4
    timeout: 30

  memory:
    host: "0.0.0.0"
    port: 8002
    workers: 2
    cache_ttl: 3600

  gateway:
    host: "0.0.0.0"
    port: 80
    rate_limit: 1000
    cors_enabled: true

databases:
  postgres:
    host: "localhost"
    port: 5432
    database: "collaboration"
    pool_size: 20
    max_overflow: 30

  redis:
    host: "localhost"
    port: 6379
    db: 0
    pool_size: 10

  vector_db:
    host: "localhost"
    port: 6333
    collection: "memories"

security:
  jwt_secret: "${JWT_SECRET}"
  token_ttl: 3600
  rate_limit_per_minute: 100
  cors_origins:
    - "https://app.connet.ai"
    - "https://dashboard.connet.ai"

monitoring:
  metrics_port: 8000
  health_check_interval: 30
  log_level: "INFO"

  prometheus:
    enabled: true
    host: "localhost"
    port: 9090

  jaeger:
    enabled: true
    host: "localhost"
    port: 14268

features:
  memory_sharing: true
  real_time_collaboration: true
  distributed_consensus: true
  auto_scaling: true
```

### 2. 配置加载器

```python
# config_loader.py
import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 20

@dataclass
class ServiceConfig:
    host: str
    port: int
    workers: int = 1
    timeout: int = 30

class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = "config.yml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 环境变量替换
            config = self._replace_env_vars(config)

            return config
        except Exception as e:
            print(f"配置加载失败: {e}")
            return {}

    def _replace_env_vars(self, obj: Any) -> Any:
        """递归替换环境变量"""
        if isinstance(obj, dict):
            return {key: self._replace_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        else:
            return obj

    def get_database_config(self, db_name: str) -> Optional[DatabaseConfig]:
        """获取数据库配置"""
        db_config = self.config.get('databases', {}).get(db_name)
        if not db_config:
            return None

        return DatabaseConfig(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 5432),
            database=db_config.get('database', db_name),
            username=os.getenv(f"{db_name.upper()}_USER", 'postgres'),
            password=os.getenv(f"{db_name.upper()}_PASSWORD", ''),
            pool_size=db_config.get('pool_size', 20)
        )

    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """获取服务配置"""
        service_config = self.config.get('services', {}).get(service_name)
        if not service_config:
            return None

        return ServiceConfig(
            host=service_config.get('host', '0.0.0.0'),
            port=service_config.get('port', 8000),
            workers=service_config.get('workers', 1),
            timeout=service_config.get('timeout', 30)
        )

    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value
```

## 🚀 性能优化

### 1. 异步处理优化

```python
# async_optimization.py
import asyncio
from typing import List, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import aiofiles

class AsyncOptimizer:
    """异步处理优化器"""

    def __init__(self, max_workers: int = 10):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(100)  # 限制并发数

    async def batch_process(self, items: List[Any], processor: Callable,
                          batch_size: int = 10) -> List[Any]:
        """批量异步处理"""
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # 并行处理批次
            batch_tasks = [self._safe_process(processor, item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # 过滤成功结果
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)

        return results

    async def _safe_process(self, processor: Callable, item: Any) -> Any:
        """安全处理单个项目"""
        async with self.semaphore:
            try:
                if asyncio.iscoroutinefunction(processor):
                    return await processor(item)
                else:
                    # 在线程池中执行同步函数
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(self.executor, processor, item)
            except Exception as e:
                print(f"处理失败: {e}")
                return None

    async def parallel_io_operations(self, file_paths: List[str]) -> List[str]:
        """并行文件I/O操作"""
        async def read_file(file_path: str) -> str:
            try:
                async with aiofiles.open(file_path, 'r') as f:
                    return await f.read()
            except Exception as e:
                print(f"文件读取失败 {file_path}: {e}")
                return ""

        tasks = [read_file(path) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### 2. 内存优化

```python
# memory_optimization.py
import gc
import psutil
import weakref
from typing import Dict, Any, Optional
from functools import lru_cache

class MemoryOptimizer:
    """内存优化器"""

    def __init__(self, max_cache_size: int = 1000):
        self.max_cache_size = max_cache_size
        self.weak_refs: Dict[str, Any] = weakref.WeakValueDictionary()
        self.memory_threshold = 0.8  # 80% 内存使用率阈值

    @lru_cache(maxsize=1000)
    def cached_computation(self, key: str, data: str) -> str:
        """带缓存的计算"""
        # 模拟计算密集型操作
        return f"processed_{key}_{hash(data)}"

    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()

        return {
            "process_memory_mb": memory_info.rss / 1024 / 1024,
            "process_memory_percent": process.memory_percent(),
            "system_memory_percent": system_memory.percent,
            "available_memory_mb": system_memory.available / 1024 / 1024
        }

    def should_trigger_gc(self) -> bool:
        """判断是否应该触发垃圾回收"""
        memory_usage = self.get_memory_usage()
        return memory_usage["system_memory_percent"] > self.memory_threshold * 100

    def optimize_memory(self):
        """内存优化"""
        if self.should_trigger_gc():
            # 清理缓存
            self.cached_computation.cache_clear()

            # 手动垃圾回收
            gc.collect()

            print("执行内存优化")

    def store_weak_reference(self, key: str, obj: Any):
        """存储弱引用"""
        self.weak_refs[key] = obj

    def get_weak_reference(self, key: str) -> Optional[Any]:
        """获取弱引用对象"""
        return self.weak_refs.get(key)
```

## 🧪 测试策略

### 1. 单元测试

```python
# test_agent.py
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from your_protocol.agent_base import BaseAgent
from your_protocol.message_broker import MessageBroker

class TestAgent(BaseAgent):
    """测试用智能体"""

    async def process_task(self, task):
        return {"result": f"processed_{task['id']}"}

    async def handle_collaboration_request(self, request):
        return {"accepted": True}

@pytest.fixture
async def test_agent():
    """测试智能体fixture"""
    agent = TestAgent("test_agent", "Test Agent", {})
    await agent.initialize()
    return agent

@pytest.fixture
async def message_broker():
    """消息代理fixture"""
    broker = MessageBroker()
    await broker.initialize()
    return broker

@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """测试智能体初始化"""
    assert test_agent.agent_id == "test_agent"
    assert test_agent.name == "Test Agent"
    assert test_agent.status == "ready"

@pytest.mark.asyncio
async def test_message_sending(test_agent, message_broker):
    """测试消息发送"""
    test_agent.message_broker = message_broker

    result = await test_agent.send_message(
        "recipient_123",
        "test_message",
        {"data": "test"}
    )

    assert result is True

@pytest.mark.asyncio
async def test_task_processing(test_agent):
    """测试任务处理"""
    task = {"id": "task_123", "type": "test"}
    result = await test_agent.process_task(task)

    assert result["result"] == "processed_task_123"

@pytest.mark.asyncio
async def test_collaboration_request(test_agent):
    """测试协作请求处理"""
    request = {"session_id": "session_123", "participants": ["agent1", "agent2"]}
    result = await test_agent.handle_collaboration_request(request)

    assert result["accepted"] is True
```

### 2. 集成测试

```python
# test_integration.py
import pytest
import asyncio
from your_protocol.collaboration_orchestrator import CollaborationOrchestrator
from your_protocol.message_broker import MessageBroker
from your_protocol.memory_manager import MemoryManager

@pytest.fixture
async def integration_setup():
    """集成测试环境设置"""
    # 创建组件
    message_broker = MessageBroker("redis://localhost:6379")
    memory_manager = MemoryManager(
        "postgresql://localhost/test_db",
        "redis://localhost:6379",
        "http://localhost:6333"
    )
    orchestrator = CollaborationOrchestrator(message_broker, memory_manager)

    # 初始化
    await message_broker.initialize()
    await memory_manager.initialize()

    return {
        "message_broker": message_broker,
        "memory_manager": memory_manager,
        "orchestrator": orchestrator
    }

@pytest.mark.asyncio
async def test_end_to_end_collaboration(integration_setup):
    """端到端协作测试"""
    components = integration_setup
    orchestrator = components["orchestrator"]

    # 创建测试智能体
    agent1 = TestAgent("agent1", "Agent 1", {})
    agent2 = TestAgent("agent2", "Agent 2", {})

    # 注册智能体
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)

    # 发起协作
    session_id = await orchestrator.initiate_collaboration(
        "Test Collaboration",
        "Integration test collaboration",
        ["computation", "analysis"]
    )

    assert session_id is not None
    assert session_id in orchestrator.active_sessions

@pytest.mark.asyncio
async def test_memory_sharing_workflow(integration_setup):
    """记忆共享工作流测试"""
    memory_manager = integration_setup["memory_manager"]

    # 存储记忆
    memory = {
        "memory_id": "test_memory_123",
        "agent_id": "agent1",
        "content": "Test memory content",
        "type": "semantic",
        "access_level": "public"
    }

    result = await memory_manager.store_memory(memory)
    assert result is True

    # 检索记忆
    retrieved = await memory_manager.retrieve_memory("test_memory_123", "agent2")
    assert retrieved is not None
    assert retrieved["content"] == "Test memory content"

    # 搜索记忆
    search_results = await memory_manager.search_memories("test", "agent2")
    assert len(search_results) > 0
```

### 3. 性能测试

```python
# test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.performance
@pytest.mark.asyncio
async def test_message_throughput(message_broker):
    """测试消息吞吐量"""
    start_time = time.time()
    message_count = 1000

    # 并发发送消息
    tasks = []
    for i in range(message_count):
        message = Message(
            id=f"msg_{i}",
            type="test",
            sender_id="sender",
            recipient_id="recipient",
            content={"data": f"test_{i}"},
            priority="medium",
            timestamp=datetime.utcnow()
        )
        tasks.append(message_broker.send_message(message))

    results = await asyncio.gather(*tasks)
    end_time = time.time()

    # 计算性能指标
    duration = end_time - start_time
    throughput = message_count / duration

    print(f"发送 {message_count} 条消息耗时: {duration:.2f} 秒")
    print(f"吞吐量: {throughput:.2f} 消息/秒")

    # 性能断言
    assert throughput > 100  # 期望每秒处理超过100条消息
    assert all(results)  # 所有消息都应该发送成功

@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_retrieval_speed(memory_manager):
    """测试记忆检索速度"""
    # 预先存储测试记忆
    memory_ids = []
    for i in range(100):
        memory = {
            "memory_id": f"perf_test_{i}",
            "agent_id": "test_agent",
            "content": f"Performance test memory {i}",
            "type": "semantic",
            "access_level": "public"
        }
        await memory_manager.store_memory(memory)
        memory_ids.append(memory["memory_id"])

    # 测试检索性能
    start_time = time.time()

    retrieval_tasks = []
    for memory_id in memory_ids:
        task = memory_manager.retrieve_memory(memory_id, "test_agent")
        retrieval_tasks.append(task)

    results = await asyncio.gather(*retrieval_tasks)
    end_time = time.time()

    # 计算性能指标
    duration = end_time - start_time
    retrieval_rate = len(memory_ids) / duration

    print(f"检索 {len(memory_ids)} 条记忆耗时: {duration:.2f} 秒")
    print(f"检索速率: {retrieval_rate:.2f} 记忆/秒")

    # 性能断言
    assert retrieval_rate > 50  # 期望每秒检索超过50条记忆
    assert all(result is not None for result in results)
```

## 📚 最佳实践

### 1. 智能体设计原则

- **单一职责**: 每个智能体应该有明确的职责范围
- **松耦合**: 智能体间通过标准协议通信，避免直接依赖
- **容错设计**: 具备错误处理和恢复能力
- **可观测性**: 提供充分的日志和指标
- **可扩展性**: 支持能力的动态扩展

### 2. 性能优化建议

- **连接池**: 使用数据库和缓存连接池
- **批量操作**: 合并小的数据库操作
- **异步处理**: 使用异步 I/O 和并发处理
- **缓存策略**: 合理使用多级缓存
- **资源监控**: 监控 CPU、内存和网络使用

### 3. 安全考虑

- **身份验证**: 强制使用 JWT 或证书认证
- **权限控制**: 实现细粒度的权限管理
- **数据加密**: 传输和存储数据加密
- **审计日志**: 记录所有关键操作
- **速率限制**: 防止滥用和攻击

---

本实现指南提供了多智能体协作协议的完整实现路径，包括核心组件开发、部署策略、测试方法和最佳实践。按照本指南，您可以构建一个高性能、可扩展的多智能体协作系统。

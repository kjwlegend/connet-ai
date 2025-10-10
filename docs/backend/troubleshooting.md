# Connet.AI 故障排除指南

> 常见问题诊断和解决方案

## 📋 目录
- [系统诊断](#系统诊断)
- [数据库问题](#数据库问题)
- [LangGraph相关问题](#langgraph相关问题)
- [Contact管理问题](#contact管理问题)
- [性能问题](#性能问题)
- [API接口问题](#api接口问题)
- [监控和日志](#监控和日志)

## 🔍 系统诊断

### 健康检查命令
```bash
# 检查应用健康状态
curl http://localhost:8000/api/health

# 检查数据库连接
psql -h localhost -U connet_ai -d connet_ai -c "SELECT version();"

# 检查Redis连接
redis-cli ping

# 检查LangGraph功能
python -c "
import os
os.environ['LANGGRAPH_ENABLED'] = 'true'
from app.modules.ai.workflows.workflow_engine import WorkflowEngine
print('LangGraph OK')
"
```

### 服务状态检查
```bash
# Docker环境
docker-compose ps
docker-compose logs -f app

# 系统服务
sudo systemctl status connet-ai
sudo systemctl status postgresql
sudo systemctl status redis
sudo systemctl status nginx

# 进程监控
ps aux | grep -E "(uvicorn|postgres|redis)"
netstat -tlnp | grep -E "(8000|5432|6379)"
```

## 🗄️ 数据库问题

### 连接问题

#### 问题: 数据库连接超时
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 exceeded
```

**诊断步骤**:
```bash
# 检查连接池状态
python -c "
from app.core.db import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
print(f'Overflow: {engine.pool.overflow()}')
"

# 检查活跃连接
psql -U connet_ai -d connet_ai -c "
SELECT pid, usename, application_name, client_addr, state, query_start 
FROM pg_stat_activity 
WHERE state = 'active';
"
```

**解决方案**:
```python
# 增加连接池大小
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# 设置连接超时
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

#### 问题: 迁移失败
```
alembic.util.exc.CommandError: Can't locate revision identified by 'abc123'
```

**解决方案**:
```bash
# 检查迁移历史
alembic history

# 重置到最新版本
alembic stamp head

# 手动运行迁移
alembic upgrade head --sql > migration.sql
psql -U connet_ai -d connet_ai -f migration.sql
```

### 性能问题

#### 问题: 查询缓慢
**诊断步骤**:
```sql
-- 启用慢查询日志
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- 查看最耗时的查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 检查索引使用情况
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('contacts', 'workflow_executions', 'node_executions');
```

**解决方案**:
```sql
-- 创建缺失的索引
CREATE INDEX CONCURRENTLY idx_contacts_user_agent ON contacts(user_id, agent_id);
CREATE INDEX CONCURRENTLY idx_workflow_executions_conversation ON workflow_executions(conversation_id);

-- 更新表统计信息
ANALYZE contacts;
ANALYZE workflow_executions;
ANALYZE node_executions;
```

### 数据完整性问题

#### 问题: 外键约束冲突
```
psycopg2.IntegrityError: foreign key constraint fails
```

**诊断和修复**:
```sql
-- 检查孤立记录
SELECT c.id, c.agent_id 
FROM contacts c 
LEFT JOIN agents a ON c.agent_id = a.id 
WHERE a.id IS NULL AND c.agent_id IS NOT NULL;

-- 修复孤立的Contact记录
UPDATE contacts 
SET agent_id = (SELECT id FROM agents WHERE name = 'legacy_default' LIMIT 1)
WHERE agent_id NOT IN (SELECT id FROM agents) AND agent_id IS NOT NULL;
```

## 🔄 LangGraph相关问题

### 工作流执行失败

#### 问题: LangGraph导入错误
```
ImportError: No module named 'langgraph'
```

**解决方案**:
```bash
# 检查LangGraph安装
pip show langgraph

# 重新安装
pip install --upgrade langgraph==0.0.40

# 验证安装
python -c "import langgraph; print(langgraph.__version__)"
```

#### 问题: 工作流构建失败
```
ValueError: Node 'contact_123' not found in workflow
```

**诊断步骤**:
```python
# 检查Contact参与者
async def debug_workflow_participants(conversation_id):
    from app.services.contact_service import ContactService
    
    contact_service = ContactService()
    participants = await contact_service.get_conversation_participants(conversation_id)
    
    print(f"Found {len(participants)} participants:")
    for p in participants:
        print(f"- Contact {p.id}: {p.custom_name or p.agent_display_name}")
        print(f"  Agent: {p.agent_id}, Status: {p.status}")
    
    return participants

# 运行诊断
import asyncio
asyncio.run(debug_workflow_participants("your-conversation-id"))
```

**解决方案**:
```python
# 添加参与者验证
async def validate_workflow_participants(participants):
    """验证工作流参与者"""
    
    valid_participants = []
    for participant in participants:
        if participant.status == "active" and participant.agent_id:
            valid_participants.append(participant)
        else:
            logger.warning(f"Skipping invalid participant: {participant.id}")
    
    if not valid_participants:
        raise ValueError("No valid participants found for workflow")
    
    return valid_participants
```

### 节点执行超时

#### 问题: Contact节点执行超时
```
TimeoutError: Node execution exceeded 30 seconds
```

**诊断步骤**:
```python
# 检查节点执行历史
async def check_node_execution_history(contact_id):
    result = await db.execute("""
        SELECT 
            ne.node_id,
            ne.status,
            ne.duration_ms,
            ne.retry_count,
            ne.error_message,
            ne.started_at,
            ne.completed_at
        FROM node_executions ne
        WHERE ne.contact_id = :contact_id
        ORDER BY ne.started_at DESC
        LIMIT 10
    """, {"contact_id": contact_id})
    
    for row in result.fetchall():
        print(f"Node: {row.node_id}, Status: {row.status}, Duration: {row.duration_ms}ms")
        if row.error_message:
            print(f"  Error: {row.error_message}")
```

**解决方案**:
```python
# 配置超时和重试
CONTACT_EXECUTION_CONFIG = {
    "timeout_ms": 60000,  # 增加到60秒
    "max_retries": 3,
    "retry_delay_ms": 1000,
    "exponential_backoff": True
}

# 实现超时处理
async def execute_contact_with_timeout(contact, message, timeout=60):
    try:
        result = await asyncio.wait_for(
            execute_contact_node(contact, message),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"Contact {contact.id} execution timeout after {timeout}s")
        return {"error": "execution_timeout", "contact_id": contact.id}
```

### 记忆系统问题

#### 问题: Mem0连接失败
```
ConnectionError: Failed to connect to Mem0 API
```

**诊断步骤**:
```python
# 测试Mem0连接
async def test_mem0_connection():
    try:
        from mem0 import Memory
        import os
        
        # 检查API密钥
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            print("ERROR: MEM0_API_KEY not set")
            return False
        
        # 测试连接
        m = Memory(api_key=api_key)
        result = await m.search("test", user_id="test_user")
        print("Mem0 connection successful")
        return True
        
    except Exception as e:
        print(f"Mem0 connection failed: {e}")
        return False

# 运行测试
import asyncio
asyncio.run(test_mem0_connection())
```

**解决方案**:
```python
# 实现Mem0备选方案
class MemoryService:
    def __init__(self):
        self.mem0_enabled = bool(os.getenv("MEM0_API_KEY"))
        self.fallback_to_database = True
    
    async def search_memories(self, query, user_id, limit=10):
        """搜索记忆，支持回退到数据库"""
        
        if self.mem0_enabled:
            try:
                return await self._search_with_mem0(query, user_id, limit)
            except Exception as e:
                logger.warning(f"Mem0 search failed, falling back to database: {e}")
        
        if self.fallback_to_database:
            return await self._search_with_database(query, user_id, limit)
        
        return []
```

## 👥 Contact管理问题

### Contact实例化问题

#### 问题: Agent添加到Contact失败
```
IntegrityError: duplicate key value violates unique constraint "unique_user_agent"
```

**解决方案**:
```python
# 检查现有Contact
async def safe_add_agent_to_contacts(user_id, agent_id, custom_config=None):
    """安全地添加Agent到Contact"""
    
    # 检查是否已存在
    existing = await contact_repo.get_user_contact_by_agent(user_id, agent_id)
    if existing:
        if existing.status == "archived":
            # 重新激活已归档的Contact
            await contact_repo.update(existing.id, {"status": "active"})
            return existing
        else:
            raise ValueError(f"Agent {agent_id} already added to user {user_id} contacts")
    
    # 创建新的Contact实例
    return await contact_repo.create_contact_instance(user_id, agent_id, custom_config)
```

#### 问题: Contact配置无效
```
ValidationError: Invalid instance_config format
```

**诊断和修复**:
```python
# 验证Contact配置
def validate_contact_config(instance_config):
    """验证Contact实例配置"""
    
    required_fields = ["model_preferences"]
    for field in required_fields:
        if field not in instance_config:
            instance_config[field] = {}
    
    # 验证模型配置
    model_prefs = instance_config["model_preferences"]
    if "default_model" not in model_prefs:
        model_prefs["default_model"] = "gpt-4-turbo"
    
    # 验证工具配置
    if "tools" in instance_config:
        valid_tools = ["web_search", "calculator", "code_executor"]
        instance_config["tools"] = [
            tool for tool in instance_config["tools"] 
            if tool in valid_tools
        ]
    
    return instance_config

# 修复现有无效配置
async def fix_invalid_contact_configs():
    """修复无效的Contact配置"""
    
    invalid_contacts = await db.execute("""
        SELECT id, instance_config 
        FROM contacts 
        WHERE instance_config IS NULL 
           OR NOT (instance_config ? 'model_preferences')
    """)
    
    for contact in invalid_contacts:
        fixed_config = validate_contact_config(contact.instance_config or {})
        await db.execute("""
            UPDATE contacts 
            SET instance_config = :config 
            WHERE id = :contact_id
        """, {"config": json.dumps(fixed_config), "contact_id": contact.id})
```

### 参与者管理问题

#### 问题: 对话参与者状态不一致
```
ValueError: Active participant not found in conversation
```

**诊断脚本**:
```python
async def diagnose_participant_issues(conversation_id):
    """诊断对话参与者问题"""
    
    # 检查对话是否存在
    conversation = await db.execute("""
        SELECT id, title, status, created_at 
        FROM conversations 
        WHERE id = :id
    """, {"id": conversation_id})
    
    if not conversation.fetchone():
        print(f"Conversation {conversation_id} not found")
        return
    
    # 检查参与者状态
    participants = await db.execute("""
        SELECT 
            cp.id,
            cp.contact_id,
            cp.user_id,
            cp.is_active,
            cp.role,
            c.status as contact_status,
            u.email as user_email
        FROM conversation_participants cp
        JOIN contacts c ON cp.contact_id = c.id
        JOIN users u ON cp.user_id = u.id
        WHERE cp.conversation_id = :conversation_id
    """, {"conversation_id": conversation_id})
    
    print(f"Participants in conversation {conversation_id}:")
    for p in participants.fetchall():
        print(f"  User: {p.user_email}")
        print(f"  Contact: {p.contact_id} (status: {p.contact_status})")
        print(f"  Participant: active={p.is_active}, role={p.role}")
        print("  ---")
```

**修复方案**:
```python
async def fix_participant_inconsistencies(conversation_id):
    """修复参与者状态不一致"""
    
    # 清理无效参与者
    await db.execute("""
        UPDATE conversation_participants 
        SET is_active = false 
        WHERE conversation_id = :conversation_id 
          AND contact_id IN (
              SELECT cp.contact_id 
              FROM conversation_participants cp
              JOIN contacts c ON cp.contact_id = c.id
              WHERE c.status != 'active'
          )
    """, {"conversation_id": conversation_id})
    
    # 确保至少有一个活跃参与者
    active_count = await db.execute("""
        SELECT COUNT(*) as count
        FROM conversation_participants 
        WHERE conversation_id = :conversation_id AND is_active = true
    """, {"conversation_id": conversation_id})
    
    if active_count.fetchone().count == 0:
        # 重新激活最近的参与者
        await db.execute("""
            UPDATE conversation_participants 
            SET is_active = true 
            WHERE conversation_id = :conversation_id 
              AND id = (
                  SELECT id FROM conversation_participants 
                  WHERE conversation_id = :conversation_id 
                  ORDER BY joined_at DESC 
                  LIMIT 1
              )
        """, {"conversation_id": conversation_id})
```

## 🚀 性能问题

### 内存使用过高

#### 诊断步骤
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 检查Python内存使用
pip install memory-profiler
python -m memory_profiler -c "
from app.main import app
import uvicorn
print('Memory usage analysis complete')
"

# 检查对象引用
python -c "
import gc
import sys
from collections import Counter

# 统计对象类型
obj_types = Counter(type(obj).__name__ for obj in gc.get_objects())
for obj_type, count in obj_types.most_common(10):
    print(f'{obj_type}: {count}')
"
```

#### 解决方案
```python
# 优化内存使用
import gc
from functools import wraps

def memory_limit(max_mb=512):
    """内存使用限制装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行前清理内存
            gc.collect()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                # 执行后清理内存
                gc.collect()
        return wrapper
    return decorator

# 应用到高内存使用的函数
@memory_limit(max_mb=256)
async def process_large_workflow(workflow_data):
    # 大型工作流处理
    pass
```

### 数据库连接泄漏

#### 诊断步骤
```python
# 监控连接池状态
async def monitor_connection_pool():
    """监控数据库连接池"""
    
    from app.core.db import engine
    
    while True:
        pool = engine.pool
        print(f"Pool size: {pool.size()}")
        print(f"Checked out: {pool.checkedout()}")
        print(f"Overflow: {pool.overflow()}")
        print(f"Invalid: {pool.invalidated()}")
        print("---")
        
        await asyncio.sleep(10)

# 运行监控
import asyncio
asyncio.run(monitor_connection_pool())
```

#### 解决方案
```python
# 确保连接正确释放
from contextlib import asynccontextmanager

@asynccontextmanager
async def safe_db_session():
    """安全的数据库会话管理"""
    session = None
    try:
        session = get_db_session()
        yield session
        await session.commit()
    except Exception as e:
        if session:
            await session.rollback()
        raise
    finally:
        if session:
            await session.close()

# 使用方式
async def safe_database_operation():
    async with safe_db_session() as db:
        # 数据库操作
        result = await db.execute("SELECT * FROM contacts")
        return result.fetchall()
```

## 🔌 API接口问题

### 请求超时

#### 问题: API请求超时
```
HTTP 504 Gateway Timeout
```

**诊断步骤**:
```bash
# 检查Nginx配置
nginx -t
cat /etc/nginx/sites-available/connet-ai | grep timeout

# 检查应用响应时间
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# curl-format.txt内容:
#     time_namelookup:  %{time_namelookup}\n
#     time_connect:     %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#     time_pretransfer: %{time_pretransfer}\n
#     time_redirect:    %{time_redirect}\n
#     time_starttransfer: %{time_starttransfer}\n
#     ----------\n
#     time_total:       %{time_total}\n
```

**解决方案**:
```nginx
# 增加Nginx超时时间
proxy_read_timeout 300s;
proxy_connect_timeout 75s;
proxy_send_timeout 300s;

# 添加缓冲配置
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;
```

```python
# 应用层超时控制
import asyncio
from fastapi import HTTPException

async def with_timeout(coro, timeout_seconds=30):
    """为协程添加超时控制"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")

# 在API端点中使用
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    return await with_timeout(
        process_chat_message(request),
        timeout_seconds=60
    )
```

### 认证问题

#### 问题: JWT Token验证失败
```
HTTP 401 Unauthorized: Invalid token
```

**诊断步骤**:
```python
# 验证JWT配置
import jwt
from datetime import datetime

def debug_jwt_token(token):
    """调试JWT Token"""
    try:
        # 不验证签名，只解码查看内容
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"Token payload: {payload}")
        
        # 检查过期时间
        if 'exp' in payload:
            exp_time = datetime.fromtimestamp(payload['exp'])
            now = datetime.now()
            print(f"Token expires: {exp_time}")
            print(f"Current time: {now}")
            print(f"Token valid: {exp_time > now}")
        
        return payload
    except Exception as e:
        print(f"Token decode error: {e}")
        return None

# 使用方式
debug_jwt_token("your-jwt-token-here")
```

**解决方案**:
```python
# 改进JWT处理
from datetime import datetime, timedelta
import jwt

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, user_id: str, expires_delta: timedelta = None):
        """创建JWT Token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str):
        """验证JWT Token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

## 📊 监控和日志

### 日志分析

#### 查看错误日志
```bash
# 应用日志
tail -f /var/log/connet-ai/app.log | grep ERROR

# 系统日志
journalctl -u connet-ai -f

# Nginx日志
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log | grep -E "(4[0-9]{2}|5[0-9]{2})"

# 数据库日志
tail -f /var/log/postgresql/postgresql-15-main.log | grep ERROR
```

#### 结构化日志查询
```python
# 日志查询工具
import json
import re
from datetime import datetime, timedelta

def parse_log_file(log_file, start_time=None, level="ERROR"):
    """解析结构化日志文件"""
    
    if start_time is None:
        start_time = datetime.now() - timedelta(hours=1)
    
    errors = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                log_time = datetime.fromisoformat(log_entry['asctime'])
                
                if (log_time >= start_time and 
                    log_entry.get('levelname') == level):
                    errors.append(log_entry)
            except:
                # 处理非JSON行
                continue
    
    return errors

# 使用示例
recent_errors = parse_log_file('/var/log/connet-ai/app.log')
for error in recent_errors[:10]:
    print(f"{error['asctime']}: {error['message']}")
```

### 性能监控

#### 设置监控告警
```python
# 性能监控脚本
async def monitor_system_performance():
    """监控系统性能"""
    
    metrics = {
        "response_time": await measure_api_response_time(),
        "database_connections": await count_database_connections(),
        "memory_usage": get_memory_usage(),
        "error_rate": await calculate_error_rate()
    }
    
    # 检查告警条件
    alerts = []
    if metrics["response_time"] > 5000:  # 5秒
        alerts.append("High response time")
    
    if metrics["error_rate"] > 0.05:  # 5%
        alerts.append("High error rate")
    
    if metrics["memory_usage"] > 0.9:  # 90%
        alerts.append("High memory usage")
    
    if alerts:
        await send_alerts(alerts, metrics)
    
    return metrics

async def send_alerts(alerts, metrics):
    """发送告警通知"""
    message = f"⚠️ Connet.AI 告警: {', '.join(alerts)}\n"
    message += f"响应时间: {metrics['response_time']}ms\n"
    message += f"错误率: {metrics['error_rate']:.2%}\n"
    message += f"内存使用: {metrics['memory_usage']:.1%}"
    
    # 发送到Slack/钉钉/邮件等
    await notify_team(message)
```

## 🆘 紧急情况处理

### 系统完全不可用

#### 快速恢复步骤
```bash
#!/bin/bash
# emergency_recovery.sh

echo "🚨 开始紧急恢复程序..."

# 1. 检查基础服务
echo "检查基础服务状态..."
systemctl status postgresql
systemctl status redis
systemctl status nginx

# 2. 重启应用服务
echo "重启应用服务..."
systemctl restart connet-ai

# 3. 检查日志
echo "检查最近的错误日志..."
journalctl -u connet-ai --since "5 minutes ago" | grep ERROR

# 4. 验证服务可用性
echo "验证服务可用性..."
curl -f http://localhost:8000/api/health || echo "❌ 健康检查失败"

# 5. 如果服务仍不可用，启用维护模式
if ! curl -f http://localhost:8000/api/health; then
    echo "启用维护模式..."
    echo "系统维护中，请稍后再试" > /var/www/html/maintenance.html
    
    # 修改Nginx配置指向维护页面
    nginx -s reload
fi

echo "紧急恢复程序完成"
```

### 数据库故障

#### 数据库恢复步骤
```bash
# 数据库故障恢复
echo "开始数据库恢复..."

# 检查数据库状态
pg_isready -h localhost -p 5432

# 如果数据库无法启动，尝试修复
if [ $? -ne 0 ]; then
    echo "数据库无法连接，尝试修复..."
    
    # 停止PostgreSQL
    systemctl stop postgresql
    
    # 检查数据目录
    sudo -u postgres pg_controldata /var/lib/postgresql/15/main
    
    # 尝试启动单用户模式
    sudo -u postgres postgres --single -D /var/lib/postgresql/15/main template1
    
    # 重启PostgreSQL
    systemctl start postgresql
fi

# 验证数据完整性
psql -U connet_ai -d connet_ai -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
ORDER BY n_tup_ins DESC;
"
```

## 📞 获取帮助

### 技术支持联系方式
- **文档**: [故障排除Wiki](https://github.com/your-org/connet-ai/wiki/troubleshooting)
- **问题反馈**: [GitHub Issues](https://github.com/your-org/connet-ai/issues)
- **紧急支持**: support@yourdomain.com
- **开发团队**: dev-team@yourdomain.com

### 创建支持工单
```bash
# 收集系统信息脚本
#!/bin/bash
# collect_system_info.sh

echo "收集系统诊断信息..."
OUTPUT_FILE="connet-ai-diagnostics-$(date +%Y%m%d_%H%M%S).txt"

{
    echo "=== 系统信息 ==="
    uname -a
    free -h
    df -h
    
    echo -e "\n=== 服务状态 ==="
    systemctl status connet-ai --no-pager
    systemctl status postgresql --no-pager
    systemctl status redis --no-pager
    
    echo -e "\n=== 应用日志 (最近100行) ==="
    journalctl -u connet-ai --lines=100 --no-pager
    
    echo -e "\n=== 健康检查 ==="
    curl -s http://localhost:8000/api/health || echo "健康检查失败"
    
    echo -e "\n=== 数据库状态 ==="
    psql -U connet_ai -d connet_ai -c "\l" || echo "数据库连接失败"
    
} > $OUTPUT_FILE

echo "诊断信息已保存到: $OUTPUT_FILE"
echo "请将此文件发送给技术支持团队"
```

---

> 📝 **维护团队**: 运维团队  
> 🔄 **最后更新**: 2025-08-22  
> 📞 **紧急联系**: +1-xxx-xxx-xxxx

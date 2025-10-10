# Connet.AI 部署指南

> 生产环境部署和配置完整指南

## 📋 目录
- [环境要求](#环境要求)
- [环境变量配置](#环境变量配置)
- [数据库设置](#数据库设置)
- [外部服务配置](#外部服务配置)
- [应用部署](#应用部署)
- [监控配置](#监控配置)
- [故障排除](#故障排除)

## 🔧 环境要求

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **Python**: 3.11+
- **Node.js**: 18+ (前端)
- **内存**: 最少4GB，推荐8GB+
- **存储**: 最少20GB，推荐SSD 50GB+

### 必需服务
- **PostgreSQL**: 15+ (支持pgvector扩展)
- **Redis**: 7.0+
- **Docker**: 20.10+ (推荐)
- **Docker Compose**: 2.0+

## 🌍 环境变量配置

### 创建环境配置文件
```bash
# 复制环境变量模板
cp .env.example .env.production

# 编辑生产环境配置
nano .env.production
```

### 完整环境变量清单
```bash
# ====================
# 基础应用配置
# ====================
APP_NAME="Connet.AI"
APP_VERSION="2.0.0"
ENVIRONMENT="production"
DEBUG=false
LOG_LEVEL="INFO"

# ====================
# 服务器配置
# ====================
HOST="0.0.0.0"
PORT=8000
WORKERS=4
MAX_CONNECTIONS=1000

# ====================
# 数据库配置
# ====================
# 主数据库 (PostgreSQL)
DATABASE_URL="postgresql://username:password@localhost:5432/connet_ai"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
DATABASE_ECHO=false

# Redis缓存
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD=""
REDIS_MAX_CONNECTIONS=10

# ====================
# 安全配置
# ====================
# JWT密钥 (生产环境必须设置强密钥)
JWT_SECRET_KEY="your-super-secret-jwt-key-here"
JWT_ALGORITHM="HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 加密密钥
ENCRYPTION_KEY="your-32-character-encryption-key"

# CORS配置
ALLOWED_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
ALLOWED_METHODS="GET,POST,PUT,DELETE,OPTIONS"
ALLOWED_HEADERS="*"

# ====================
# Supabase配置
# ====================
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"

# ====================
# LLM提供商配置
# ====================
# OpenAI
OPENAI_API_KEY="sk-your-openai-api-key"
OPENAI_ORG_ID=""  # 可选

# Anthropic
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"

# Google
GOOGLE_API_KEY="your-google-api-key"
GOOGLE_CSE_ID="your-custom-search-engine-id"

# Azure
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-azure-openai-key"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# ====================
# 记忆系统配置 (Mem0)
# ====================
MEM0_API_KEY="your-mem0-api-key"
MEM0_BASE_URL="https://api.mem0.ai"

# ====================
# LangGraph配置
# ====================
LANGGRAPH_ENABLED=true
LANGGRAPH_DEBUG=false
LANGGRAPH_CHECKPOINT_DB_URL="postgresql://username:password@localhost:5432/langgraph_checkpoints"
LANGGRAPH_MAX_CONCURRENT_WORKFLOWS=10
LANGGRAPH_DEFAULT_TIMEOUT=300

# ====================
# 文件存储配置
# ====================
# 本地存储
UPLOAD_DIR="/var/uploads"
MAX_FILE_SIZE_MB=100

# Supabase存储
SUPABASE_STORAGE_BUCKET="user-files"

# ====================
# 邮件服务配置
# ====================
# SendGrid
SENDGRID_API_KEY="SG.your-sendgrid-api-key"
FROM_EMAIL="noreply@yourdomain.com"
FROM_NAME="Connet.AI"

# SMTP (备选)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_TLS=true

# ====================
# 监控和分析
# ====================
# Sentry错误跟踪
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project-id"

# Prometheus监控
ENABLE_METRICS=true
METRICS_PORT=9090

# ====================
# 性能配置
# ====================
# 缓存配置
CACHE_TTL_SECONDS=3600
CACHE_MAX_SIZE=1000

# 限流配置
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# ====================
# 特性开关
# ====================
FEATURE_LANGGRAPH_ENABLED=true
FEATURE_MULTI_AGENT_CHAT=true
FEATURE_VECTOR_SEARCH=true
FEATURE_REAL_TIME_UPDATES=true
```

## 🗄️ 数据库设置

### PostgreSQL安装和配置
```bash
# Ubuntu安装PostgreSQL 15
sudo apt update
sudo apt install postgresql-15 postgresql-contrib-15

# 创建数据库和用户
sudo -u postgres psql
CREATE USER connet_ai WITH PASSWORD 'your-strong-password';
CREATE DATABASE connet_ai OWNER connet_ai;
GRANT ALL PRIVILEGES ON DATABASE connet_ai TO connet_ai;

# 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### pgvector扩展安装
```bash
# 从源码编译安装pgvector
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# 重启PostgreSQL
sudo systemctl restart postgresql
```

### 数据库迁移
```bash
# 进入项目目录
cd bff

# 安装Python依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 验证迁移
python -c "
from app.core.db import get_session
from sqlalchemy import text
import asyncio

async def verify_db():
    async with get_session() as db:
        result = await db.execute(text('SELECT version()'))
        print(result.fetchone())

asyncio.run(verify_db())
"
```

### Redis安装和配置
```bash
# Ubuntu安装Redis
sudo apt install redis-server

# 配置Redis
sudo nano /etc/redis/redis.conf

# 修改配置
bind 127.0.0.1
port 6379
requirepass your-redis-password
maxmemory 2gb
maxmemory-policy allkeys-lru

# 重启Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

## 🔌 外部服务配置

### Supabase项目设置
1. **创建Supabase项目**
   - 访问 https://app.supabase.com
   - 创建新项目
   - 选择合适的地区

2. **配置认证**
   ```sql
   -- 在Supabase SQL编辑器中运行
   -- 配置JWT设置
   UPDATE auth.users SET email_confirmed_at = NOW() WHERE email_confirmed_at IS NULL;
   ```

3. **配置存储桶**
   ```javascript
   // 在Supabase存储中创建bucket
   const { data, error } = await supabase.storage.createBucket('user-files', {
     public: false,
     allowedMimeTypes: ['image/*', 'application/pdf', 'text/*'],
     fileSizeLimit: 104857600 // 100MB
   });
   ```

### LLM提供商API密钥获取

#### OpenAI
1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 设置使用限制和预算

#### Anthropic
1. 访问 https://console.anthropic.com/
2. 生成API密钥
3. 配置使用量监控

#### Google
1. 访问 https://console.cloud.google.com/
2. 启用Google AI API
3. 创建服务账号和API密钥

#### Azure OpenAI
1. 在Azure门户创建OpenAI资源
2. 获取端点和API密钥
3. 部署所需的模型

### Mem0配置
```bash
# 获取Mem0 API密钥
# 1. 访问 https://mem0.ai
# 2. 注册账户
# 3. 在控制台获取API密钥

# 测试Mem0连接
python -c "
import os
from mem0 import Memory

os.environ['MEM0_API_KEY'] = 'your-mem0-api-key'
m = Memory()
print('Mem0连接成功')
"
```

## 🚀 应用部署

### Docker部署方式

#### 1. 创建Docker配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Docker Compose配置
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://connet_ai:${DB_PASSWORD}@db:5432/connet_ai
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - upload_data:/var/uploads
    restart: unless-stopped

  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=connet_ai
      - POSTGRES_USER=connet_ai
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  upload_data:
```

#### 3. 部署命令
```bash
# 构建和启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app

# 执行数据库迁移
docker-compose exec app alembic upgrade head
```

### 传统部署方式

#### 1. 系统服务配置
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/connet-ai.service
```

```ini
[Unit]
Description=Connet.AI Backend Service
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/connet-ai
Environment=PATH=/opt/connet-ai/venv/bin
EnvironmentFile=/opt/connet-ai/.env.production
ExecStart=/opt/connet-ai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 2. Nginx反向代理配置
```nginx
# /etc/nginx/sites-available/connet-ai
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # 安全headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 上传文件大小限制
    client_max_body_size 100M;

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # WebSocket代理
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # 静态文件
    location /uploads/ {
        alias /var/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 前端应用 (如果使用Nginx托管)
    location / {
        root /var/www/connet-ai;
        try_files $uri $uri/ /index.html;
        expires 1d;
        add_header Cache-Control "public";
    }
}
```

#### 3. 启动服务
```bash
# 启用和启动服务
sudo systemctl enable connet-ai
sudo systemctl start connet-ai

# 启用和启动Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# 检查服务状态
sudo systemctl status connet-ai
sudo systemctl status nginx
```

## 📊 监控配置

### 应用监控
```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# 监控指标
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
langgraph_executions = Counter('langgraph_executions_total', 'Total LangGraph executions', ['status'])

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    request_duration.observe(duration)
    
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 健康检查端点
```python
# app/api/v1/endpoints/health.py
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """系统健康检查"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "checks": {}
    }
    
    # 数据库检查
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis检查
    try:
        redis_client = get_redis_client()
        await redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # LangGraph检查
    if settings.LANGGRAPH_ENABLED:
        try:
            # 简单的LangGraph健康检查
            health_status["checks"]["langgraph"] = "healthy"
        except Exception as e:
            health_status["checks"]["langgraph"] = f"unhealthy: {str(e)}"
    
    return health_status
```

### 日志配置
```python
# app/utils/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """配置生产环境日志"""
    
    # JSON格式化器
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler('/var/log/connet-ai/app.log')
    file_handler.setFormatter(formatter)
    
    # 根日志器配置
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 抑制第三方库的详细日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
```

## 🚨 故障排除

### 常见问题和解决方案

#### 1. 数据库连接问题
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 查看连接配置
sudo -u postgres psql -c "SHOW hba_file;"
sudo cat /etc/postgresql/15/main/pg_hba.conf

# 测试连接
psql -h localhost -U connet_ai -d connet_ai -c "SELECT version();"
```

#### 2. Redis连接问题
```bash
# 检查Redis状态
sudo systemctl status redis

# 测试连接
redis-cli ping

# 检查配置
redis-cli CONFIG GET "*"
```

#### 3. LangGraph执行问题
```python
# 调试LangGraph执行
import asyncio
from app.modules.ai.workflows.workflow_engine import WorkflowEngine

async def debug_langgraph():
    engine = WorkflowEngine()
    try:
        result = await engine.execute_simple_workflow("test message")
        print(f"成功: {result}")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(debug_langgraph())
```

#### 4. 内存使用过高
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 检查Python进程内存
pip install memory_profiler
python -m memory_profiler app/main.py
```

#### 5. 性能问题诊断
```bash
# 启用慢查询日志
echo "log_min_duration_statement = 1000" >> /etc/postgresql/15/main/postgresql.conf
sudo systemctl restart postgresql

# 查看慢查询
sudo tail -f /var/log/postgresql/postgresql-15-main.log | grep "duration:"

# 检查连接池
python -c "
from app.core.db import engine
print(f'Pool size: {engine.pool.size()}')
print(f'Checked out: {engine.pool.checkedout()}')
"
```

### 监控告警设置
```bash
# 创建监控脚本
cat > /opt/connet-ai/monitor.sh << 'EOF'
#!/bin/bash

# 检查服务状态
if ! systemctl is-active --quiet connet-ai; then
    echo "Connet.AI服务异常" | mail -s "服务告警" admin@yourdomain.com
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
if [ $DISK_USAGE -gt 85 ]; then
    echo "磁盘使用率: ${DISK_USAGE}%" | mail -s "磁盘告警" admin@yourdomain.com
fi

# 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "内存使用率: ${MEM_USAGE}%" | mail -s "内存告警" admin@yourdomain.com
fi
EOF

chmod +x /opt/connet-ai/monitor.sh

# 添加到crontab
echo "*/5 * * * * /opt/connet-ai/monitor.sh" | crontab -
```

### 备份和恢复
```bash
# 数据库备份
pg_dump -h localhost -U connet_ai connet_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis备份
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d_%H%M%S).rdb

# 应用文件备份
tar -czf backup_uploads_$(date +%Y%m%d_%H%M%S).tar.gz /var/uploads/

# 自动备份脚本
cat > /opt/connet-ai/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 数据库备份
pg_dump -h localhost -U connet_ai connet_ai | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Redis备份
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +7 -delete
EOF

chmod +x /opt/connet-ai/backup.sh

# 每天凌晨2点自动备份
echo "0 2 * * * /opt/connet-ai/backup.sh" | crontab -
```

## 📞 支持联系

### 技术支持
- **文档**: [GitHub Wiki](https://github.com/your-org/connet-ai/wiki)
- **问题反馈**: [GitHub Issues](https://github.com/your-org/connet-ai/issues)
- **社区讨论**: [Discord频道](https://discord.gg/your-channel)

### 紧急联系
- **系统故障**: support@yourdomain.com
- **安全问题**: security@yourdomain.com
- **紧急电话**: +1-xxx-xxx-xxxx

---

> 📝 **运维团队**: DevOps团队  
> 🔄 **最后更新**: 2025-08-22  
> 📋 **文档版本**: v2.0

# Connet.AI BFF - Docker 本地开发环境

这个文档介绍如何使用 Docker 快速部署 Connet.AI BFF 的本地开发环境。

## 🚀 快速开始

### 前提条件

确保你的系统已安装：

- [Docker](https://docs.docker.com/get-docker/) (版本 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (版本 2.0+)

### 一键启动

```bash
# 进入 BFF 目录
cd bff

# 启动基础服务 (FastAPI + PostgreSQL + Redis)
make docker-start

# 或者启动完整服务 (包含管理工具和代理)
make docker-start-full
```

## 📋 可用命令

### 基础命令

```bash
# 启动基础服务
make docker-start

# 启动完整服务 (包含开发工具)
make docker-start-full

# 停止服务
make docker-stop

# 完全清理 (删除数据和镜像)
make docker-clean

# 重启服务
make docker-restart

# 查看服务状态
make docker-status

# 进入容器 shell
make docker-shell

# 查看日志
make docker-logs
```

### 高级命令

```bash
# 使用脚本启动 (更多选项)
./scripts/docker-start.sh --help

# 只启动基础服务
./scripts/docker-start.sh

# 启动服务 + 开发工具
./scripts/docker-start.sh --with-tools

# 启动服务 + 开发工具
./scripts/docker-start.sh --with-tools

# 清理并重新启动
./scripts/docker-start.sh --clean
```

## 🌐 服务访问地址

### 主要服务

| 服务               | 地址                         | 描述            |
| ------------------ | ---------------------------- | --------------- |
| FastAPI 应用       | http://localhost:8000        | 主要 API 服务   |
| API 文档 (Swagger) | http://localhost:8000/docs   | 交互式 API 文档 |
| API 文档 (ReDoc)   | http://localhost:8000/redoc  | 另一种 API 文档 |
| 健康检查           | http://localhost:8000/health | 服务健康状态    |

### 数据库服务

| 服务       | 地址           | 凭据              |
| ---------- | -------------- | ----------------- |
| PostgreSQL | localhost:5432 | postgres/password |
| Redis      | localhost:6379 | 无密码            |

### 开发工具 (使用 `--with-tools`)

| 工具    | 地址                  | 凭据 | 描述     |
| ------- | --------------------- | ---- | -------- |
| MailHog | http://localhost:8025 | 无   | 邮件测试 |

## 🔧 配置

### 环境变量

Docker 环境使用预设的开发环境变量。如需自定义：

1. 复制环境变量模板：

```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，修改所需配置

3. 重启服务：

```bash
make docker-restart
```

### 主要配置项

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/connet_ai

# Redis 配置
REDIS_URL=redis://redis:6379/0

# JWT 密钥 (生产环境请更改)
JWT_SECRET_KEY=your-secret-key

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# 日志级别
LOG_LEVEL=INFO
```

## 📁 目录结构

```
bff/
├── docker-compose.local.yml    # Docker Compose 配置
├── Dockerfile                  # 应用镜像构建
├── docker/                     # Docker 相关配置
│   └── redis.conf              # Redis 配置
├── scripts/                    # 启动脚本
│   ├── docker-start.sh         # 启动脚本
│   └── docker-stop.sh          # 停止脚本
└── uploads/                    # 文件上传目录
```

## 🐛 常见问题

### 服务启动失败

1. **检查端口占用**：

```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432
netstat -tulpn | grep :6379
```

2. **查看详细日志**：

```bash
make docker-logs
# 或
docker-compose -f docker-compose.local.yml logs -f
```

3. **重新构建镜像**：

```bash
make docker-clean
make docker-start
```

### 数据库连接问题

1. **等待数据库启动**：
   数据库需要一些时间初始化，第一次启动可能需要等待 30-60 秒。

2. **检查数据库状态**：

```bash
docker-compose -f docker-compose.local.yml exec db pg_isready -U postgres
```

3. **手动运行迁移**：

```bash
docker-compose -f docker-compose.local.yml exec bff alembic upgrade head
```

### 权限问题

如果在 Linux/macOS 上遇到权限问题：

```bash
# 给脚本执行权限
chmod +x scripts/*.sh

# 创建上传目录
mkdir -p uploads logs
chmod 755 uploads logs
```

## 🧪 开发工作流

### 典型开发流程

1. **启动开发环境**：

```bash
make docker-start-full
```

2. **查看 API 文档**：
   打开 http://localhost:8000/docs

3. **开发和测试**：
   代码更改会自动重载（开发模式）

4. **查看数据库**：
   使用你喜欢的数据库客户端连接 localhost:5432 (postgres/password)

5. **停止环境**：

```bash
make docker-stop
```

### 代码热重载

在开发模式下，应用会监听代码变化并自动重载。修改 Python 文件后，无需重启容器。

### 数据持久化

- PostgreSQL 数据存储在 Docker 卷中，停止容器不会丢失数据
- Redis 数据也会持久化
- 如需清除所有数据，使用 `make docker-clean`

## 🔍 调试

### 进入容器调试

```bash
# 进入应用容器
make docker-shell

# 进入数据库容器
docker-compose -f docker-compose.local.yml exec db psql -U postgres -d connet_ai

# 进入 Redis 容器
docker-compose -f docker-compose.local.yml exec redis redis-cli

# 或者使用外部工具连接
# PostgreSQL: localhost:5432 (postgres/password)
# Redis: localhost:6379 (no password)
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker-compose.local.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.local.yml logs -f bff
docker-compose -f docker-compose.local.yml logs -f db
docker-compose -f docker-compose.local.yml logs -f redis
```

## 📚 更多资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Redis 文档](https://redis.io/documentation)

## 🤝 贡献

如果你发现问题或有改进建议，请：

1. 检查现有的 [Issues](https://github.com/your-repo/issues)
2. 创建新的 Issue 或 Pull Request
3. 遵循项目的贡献指南

---

🎉 享受开发！如果遇到问题，请查看日志或创建 Issue。

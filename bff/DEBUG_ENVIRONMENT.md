# 调试环境使用指南

本指南介绍如何使用独立的 PostgreSQL 和 Redis 调试环境，用于本地开发和调试。

## 概述

调试环境只启动必要的基础服务：

- **PostgreSQL 15** - 数据库服务
- **Redis 7** - 缓存服务

这种配置适合：

- 本地开发 FastAPI 应用
- 数据库调试和测试
- API 开发和测试
- 不需要完整容器化环境的场景

## 快速开始

### 1. 启动调试环境

```bash
# 使用 Makefile（推荐）
make debug-start

# 或直接使用脚本
./scripts/debug-start.sh

# 或使用 Docker Compose
docker-compose -f docker-compose.debug.yml up -d
```

### 2. 查看服务状态

```bash
# 查看容器状态
docker-compose -f docker-compose.debug.yml ps

# 查看日志
make debug-logs
# 或
docker-compose -f docker-compose.debug.yml logs -f
```

### 3. 停止调试环境

```bash
# 使用 Makefile
make debug-stop

# 或直接使用脚本
./scripts/debug-stop.sh
```

## 连接信息

### PostgreSQL

- **主机**: `localhost`
- **端口**: `5432` (可通过 `.env` 中的 `DB_PORT` 修改)
- **数据库**: `connet_db` (可通过 `.env` 中的 `DB_NAME` 修改)
- **用户名**: `postgres` (可通过 `.env` 中的 `DB_USER` 修改)
- **密码**: `postgres` (可通过 `.env` 中的 `DB_PASSWORD` 修改)

### Redis

- **主机**: `localhost`
- **端口**: `6379` (可通过 `.env` 中的 `REDIS_PORT` 修改)
- **无密码认证**

## 数据持久化

数据存储在本地目录中，重启容器不会丢失数据：

```
bff/
├── data/
│   ├── postgres/     # PostgreSQL 数据文件
│   └── redis/        # Redis 数据文件
└── docker/
    ├── redis.conf    # Redis 配置文件
    └── postgres-init/ # PostgreSQL 初始化脚本目录
```

## 环境配置

创建 `.env` 文件来自定义配置：

```bash
# 复制示例配置
cp env.example .env

# 编辑配置
nano .env
```

关键配置项：

```env
# 数据库配置
DB_NAME=connet_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 常用操作

### 数据库操作

```bash
# 连接 PostgreSQL
docker exec -it connet-postgres-debug psql -U postgres -d connet_db

# 运行数据库迁移（需要在 BFF 目录下）
alembic upgrade head

# 创建新迁移
alembic revision --autogenerate -m "migration description"

# 备份数据库
docker exec connet-postgres-debug pg_dump -U postgres connet_db > backup.sql

# 恢复数据库
docker exec -i connet-postgres-debug psql -U postgres -d connet_db < backup.sql
```

### Redis 操作

```bash
# 连接 Redis CLI
docker exec -it connet-redis-debug redis-cli

# 查看 Redis 信息
docker exec -it connet-redis-debug redis-cli info

# 清空 Redis 数据
docker exec -it connet-redis-debug redis-cli flushall
```

### 容器管理

```bash
# 重启特定服务
docker-compose -f docker-compose.debug.yml restart postgres
docker-compose -f docker-compose.debug.yml restart redis

# 查看资源使用情况
docker stats connet-postgres-debug connet-redis-debug

# 进入容器shell
docker exec -it connet-postgres-debug sh
docker exec -it connet-redis-debug sh
```

## 故障排除

### 常见问题

1. **端口冲突**

   ```bash
   # 检查端口占用
   netstat -tulpn | grep :5432
   netstat -tulpn | grep :6379

   # 修改 .env 中的端口配置
   DB_PORT=5433
   REDIS_PORT=6380
   ```

2. **数据库连接失败**

   ```bash
   # 检查容器状态
   docker-compose -f docker-compose.debug.yml ps

   # 查看数据库日志
   docker-compose -f docker-compose.debug.yml logs postgres

   # 测试连接
   docker exec connet-postgres-debug pg_isready -U postgres
   ```

3. **Redis 连接失败**

   ```bash
   # 检查 Redis 状态
   docker exec connet-redis-debug redis-cli ping

   # 查看 Redis 日志
   docker-compose -f docker-compose.debug.yml logs redis
   ```

4. **权限问题**
   ```bash
   # 修复数据目录权限
   sudo chown -R $(id -u):$(id -g) data/
   chmod -R 755 data/
   ```

### 完全重置

如果遇到无法解决的问题，可以完全重置环境：

```bash
# 停止并删除所有数据
make debug-clean

# 或手动执行
docker-compose -f docker-compose.debug.yml down -v
rm -rf data/

# 重新启动
make debug-start
```

## 开发工作流

推荐的开发流程：

1. **启动调试环境**

   ```bash
   make debug-start
   ```

2. **运行数据库迁移**

   ```bash
   alembic upgrade head
   ```

3. **启动 FastAPI 应用**

   ```bash
   # 安装依赖
   pip install -r requirements.txt

   # 启动开发服务器
   uvicorn app.main:create_app --factory --reload --host 0.0.0.0 --port 8000
   ```

4. **开发和测试**

   - 应用连接到 localhost:5432 (PostgreSQL)
   - 应用连接到 localhost:6379 (Redis)

5. **完成后停止服务**
   ```bash
   make debug-stop
   ```

## 推荐工具

### 数据库管理工具

- **DBeaver** - 免费的通用数据库工具
- **pgAdmin** - PostgreSQL 专用管理工具
- **TablePlus** - 现代数据库客户端
- **DataGrip** - JetBrains 数据库 IDE

### Redis 管理工具

- **RedisInsight** - Redis 官方可视化工具
- **Another Redis Desktop Manager** - 跨平台 Redis 客户端
- **Medis** - macOS Redis 客户端

### 连接配置示例

**DBeaver/pgAdmin 连接配置:**

```
Host: localhost
Port: 5432
Database: connet_db
Username: postgres
Password: postgres
```

**RedisInsight 连接配置:**

```
Host: localhost
Port: 6379
Name: Connet Debug Redis
```

## 注意事项

1. **数据安全**: 调试环境使用默认密码，不要在生产环境使用
2. **资源使用**: 容器会持续运行，记得在不需要时停止
3. **数据备份**: 重要数据请及时备份
4. **网络安全**: 服务绑定到 localhost，外部无法访问

## 相关文档

- [Docker 完整环境设置](DOCKER_SETUP.md)
- [数据库管理工具推荐](DATABASE_TOOLS.md)
- [FastAPI 开发指南](../docs/backend/backend-architecture.md)

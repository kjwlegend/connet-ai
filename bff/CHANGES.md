# Docker 配置修改总结

本文档记录了对 Connet.AI BFF Docker 配置的所有修改。

## 📋 修改内容

### 1. 移除 Nginx 反向代理

- ❌ 删除了 `nginx` 服务配置
- ❌ 删除了 `docker/nginx.conf` 配置文件
- ❌ 移除了 `--with-proxy` 相关功能

**原因**: 不需要 Nginx 代理，简化架构

### 2. 移除数据库管理工具

- ❌ 删除了 `pgAdmin` 服务配置
- ❌ 删除了 `Redis Commander` 服务配置
- ❌ 删除了相关的数据卷和环境变量

**原因**: 使用外部工具更灵活，减少容器数量

### 3. 环境变量配置优化

- ✅ 数据库用户名密码从硬编码改为环境变量读取
- ✅ 所有敏感配置都支持从 `.env` 文件读取
- ✅ 提供了默认值确保开箱即用

**修改的环境变量**:

```bash
# 原来 (硬编码)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# 现在 (环境变量)
POSTGRES_USER=${DB_USER:-postgres}
POSTGRES_PASSWORD=${DB_PASSWORD:-password}
```

### 4. 数据持久化本地化

- ✅ 将 Docker volumes 改为本地目录映射
- ✅ 创建了 `data/` 目录存储持久化数据
- ✅ 添加了数据目录说明文档

**目录结构**:

```
data/
├── postgres/     # PostgreSQL 数据
├── redis/        # Redis 数据
└── README.md     # 说明文档
```

## 📁 新增文件

1. **env.example** - 环境变量示例文件
2. **data/README.md** - 数据目录说明
3. **DATABASE_TOOLS.md** - 数据库工具推荐
4. **CHANGES.md** - 此修改总结文档

## 🗑️ 删除文件

1. **docker/nginx.conf** - Nginx 配置文件
2. **data/pgadmin/** - pgAdmin 数据目录

## 🔧 配置变更

### docker-compose.local.yml

- 移除 `nginx`, `pgadmin`, `redis-commander` 服务
- 所有环境变量支持从 `.env` 读取
- 数据卷改为本地目录映射

### 启动脚本更新

- `scripts/docker-start.sh`: 移除 proxy 相关功能
- `scripts/docker-stop.sh`: 无需修改
- `scripts/test-docker.sh`: 移除管理工具测试

### Makefile 更新

- 更新帮助信息
- 移除 proxy 相关命令
- 简化工具描述

### 文档更新

- `DOCKER_SETUP.md`: 移除管理工具相关内容
- 添加外部工具推荐

## 🚀 使用方式

### 基础启动

```bash
# 启动核心服务 (FastAPI + PostgreSQL + Redis)
./scripts/docker-start.sh

# 或使用 Windows 下的替代方案
docker-compose -f docker-compose.local.yml up -d
```

### 完整启动 (包含邮件测试工具)

```bash
./scripts/docker-start.sh --with-tools
```

### 自定义配置

1. 复制环境变量文件：

   ```bash
   cp env.example .env
   ```

2. 修改 `.env` 文件中的配置

3. 重启服务

## 🔌 连接信息

### PostgreSQL

- **地址**: localhost:5432
- **用户**: postgres (可在 .env 中修改)
- **密码**: password (可在 .env 中修改)
- **数据库**: connet_ai (可在 .env 中修改)

### Redis

- **地址**: localhost:6379
- **密码**: 无

### FastAPI

- **服务**: http://localhost:8000
- **文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### MailHog (如果启用)

- **Web UI**: http://localhost:8025
- **SMTP**: localhost:1025

## 🛠️ 推荐工具

详见 [DATABASE_TOOLS.md](DATABASE_TOOLS.md)

### PostgreSQL 管理

- **DBeaver** (免费，推荐)
- **pgAdmin** (官方工具)
- **TablePlus** (现代化界面)

### Redis 管理

- **RedisInsight** (官方工具，推荐)
- **Another Redis Desktop Manager** (开源)

## ✅ 优势

1. **简化架构**: 减少不必要的容器
2. **灵活工具选择**: 可使用任何喜欢的数据库管理工具
3. **配置安全**: 敏感信息通过环境变量管理
4. **数据安全**: 本地持久化，便于备份和管理
5. **开发友好**: 更快的启动速度，更少的资源占用

## 🎯 下一步

- 根据需要在 `.env` 中配置真实的 API 密钥
- 选择并安装适合的数据库管理工具
- 开始开发你的 FastAPI 应用！

---

## 📞 需要帮助？

如果遇到问题：

1. 查看 [DOCKER_SETUP.md](DOCKER_SETUP.md) 详细文档
2. 运行 `./scripts/test-docker.sh` 测试环境
3. 查看日志: `docker-compose -f docker-compose.local.yml logs -f`

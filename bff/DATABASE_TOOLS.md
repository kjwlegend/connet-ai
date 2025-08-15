# 数据库和 Redis 连接工具推荐

由于我们移除了 pgAdmin 和 Redis Commander，你可以使用以下推荐的外部工具来管理数据库和 Redis。

## 🗄️ PostgreSQL 数据库管理工具

### 连接信息

- **主机**: localhost
- **端口**: 5432
- **数据库**: connet_ai
- **用户名**: postgres
- **密码**: password (或在 .env 中自定义)

### 推荐工具

#### 1. DBeaver (免费、跨平台)

- **下载**: https://dbeaver.io/download/
- **特点**: 免费、功能强大、支持多种数据库
- **连接方式**: 新建连接 → PostgreSQL → 输入上述连接信息

#### 2. pgAdmin (官方工具)

- **下载**: https://www.pgadmin.org/download/
- **特点**: PostgreSQL 官方管理工具
- **连接方式**: 添加服务器 → 输入连接信息

#### 3. TablePlus (macOS/Windows)

- **下载**: https://tableplus.com/
- **特点**: 现代化界面、支持多种数据库
- **连接方式**: 新建连接 → PostgreSQL → 输入连接信息

#### 4. DataGrip (JetBrains，付费)

- **下载**: https://www.jetbrains.com/datagrip/
- **特点**: 强大的 SQL IDE，与 IntelliJ 系列集成
- **连接方式**: 新建数据源 → PostgreSQL → 输入连接信息

#### 5. VS Code 扩展

- **扩展名**: PostgreSQL (ms-ossdata.vscode-postgresql)
- **特点**: 直接在 VS Code 中管理数据库
- **连接方式**: 添加连接 → 输入连接信息

### 命令行工具

```bash
# 直接连接到 Docker 容器中的 PostgreSQL
docker-compose -f docker-compose.local.yml exec db psql -U postgres -d connet_ai

# 或者使用本地 psql 客户端
psql -h localhost -p 5432 -U postgres -d connet_ai
```

## 🔴 Redis 管理工具

### 连接信息

- **主机**: localhost
- **端口**: 6379
- **密码**: 无 (开发环境)

### 推荐工具

#### 1. RedisInsight (Redis 官方工具)

- **下载**: https://redis.com/redis-enterprise/redis-insight/
- **特点**: Redis 官方免费工具，功能最全
- **连接方式**: 添加数据库 → localhost:6379

#### 2. Another Redis Desktop Manager

- **下载**: https://github.com/qishibo/AnotherRedisDesktopManager
- **特点**: 开源、跨平台、轻量级
- **连接方式**: 新建连接 → localhost:6379

#### 3. Medis (macOS)

- **下载**: https://github.com/luin/medis
- **特点**: macOS 原生应用，界面简洁
- **连接方式**: 添加服务器 → localhost:6379

#### 4. Redis Desktop Manager

- **下载**: https://respapp.com/
- **特点**: 跨平台，商业软件但有免费版本
- **连接方式**: 新建连接 → localhost:6379

#### 5. VS Code 扩展

- **扩展名**: Redis (humao.rest-client 或 database-client.redis-gui)
- **特点**: 直接在 VS Code 中管理 Redis
- **连接方式**: 配置连接到 localhost:6379

### 命令行工具

```bash
# 直接连接到 Docker 容器中的 Redis
docker-compose -f docker-compose.local.yml exec redis redis-cli

# 或者使用本地 redis-cli 客户端
redis-cli -h localhost -p 6379

# 查看所有 keys
redis-cli -h localhost -p 6379 keys "*"

# 监控 Redis 活动
redis-cli -h localhost -p 6379 monitor
```

## 📊 数据库操作示例

### PostgreSQL 常用操作

```sql
-- 查看所有表
\dt

-- 查看表结构
\d table_name

-- 查看所有数据库
\l

-- 切换数据库
\c database_name

-- 退出
\q
```

### Redis 常用操作

```bash
# 查看所有 keys
KEYS *

# 查看 key 的类型
TYPE keyname

# 查看 key 的值
GET keyname

# 设置 key 的值
SET keyname value

# 删除 key
DEL keyname

# 查看数据库信息
INFO

# 清空当前数据库
FLUSHDB
```

## 🔧 配置说明

### 修改数据库密码

如果你想修改默认密码，在 `.env` 文件中设置：

```bash
DB_USER=postgres
DB_PASSWORD=your_new_password
DB_NAME=connet_ai
```

然后重启 Docker 服务：

```bash
make docker-stop
make docker-start
```

### 生产环境安全建议

1. **使用强密码**: 在生产环境中设置复杂密码
2. **限制网络访问**: 不要将数据库端口暴露到公网
3. **启用 SSL**: 在生产环境中启用 SSL 连接
4. **定期备份**: 设置自动备份策略
5. **监控访问**: 启用日志记录和监控

## 🚀 快速开始

1. **启动服务**:

   ```bash
   make docker-start
   ```

2. **选择并安装你喜欢的工具**（推荐 DBeaver 和 RedisInsight）

3. **创建连接**:

   - PostgreSQL: localhost:5432, postgres/password
   - Redis: localhost:6379

4. **开始开发**! 🎉

---

这种方式比内置的 Web 工具更灵活，你可以选择最适合自己工作流程的工具。

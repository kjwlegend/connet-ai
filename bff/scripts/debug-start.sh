#!/bin/bash
# 本地调试环境启动脚本 - 只启动 PostgreSQL 和 Redis

set -e

echo "🔧 启动本地调试环境"
echo "=================="
echo "只启动 PostgreSQL 和 Redis 服务"
echo ""

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker Desktop"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，使用默认配置"
    echo "建议复制 env.example 到 .env 并配置数据库参数"
else
    echo "✅ 找到 .env 配置文件"
fi

# 创建数据持久化目录
echo "📁 创建数据目录..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p docker/postgres-init

# 确保 redis.conf 存在
if [ ! -f docker/redis.conf ]; then
    echo "📝 创建 Redis 配置文件..."
    mkdir -p docker
    cat > docker/redis.conf <<EOF
# Redis 调试配置
bind 0.0.0.0
port 6379
appendonly yes
appendfsync everysec
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF
fi

# 停止可能运行的容器
echo "🛑 停止现有容器..."
docker-compose -f docker-compose.debug.yml down

# 启动调试服务
echo "🚀 启动调试服务..."
docker-compose -f docker-compose.debug.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.debug.yml ps

# 显示连接信息
echo ""
echo "🎯 调试环境已启动！"
echo "==================="
echo ""
echo "📍 服务连接信息："
echo "PostgreSQL:"
echo "  - 主机: localhost"
echo "  - 端口: $(grep DB_PORT .env 2>/dev/null | cut -d'=' -f2 || echo 5432)"
echo "  - 数据库: $(grep DB_NAME .env 2>/dev/null | cut -d'=' -f2 || echo connet_db)"
echo "  - 用户名: $(grep DB_USER .env 2>/dev/null | cut -d'=' -f2 || echo postgres)"
echo "  - 密码: $(grep DB_PASSWORD .env 2>/dev/null | cut -d'=' -f2 || echo postgres)"
echo ""
echo "Redis:"
echo "  - 主机: localhost"
echo "  - 端口: $(grep REDIS_PORT .env 2>/dev/null | cut -d'=' -f2 || echo 6379)"
echo "  - 无密码"
echo ""
echo "🔧 管理命令："
echo "  停止服务: ./scripts/debug-stop.sh"
echo "  查看日志: docker-compose -f docker-compose.debug.yml logs -f"
echo "  进入 PostgreSQL: docker exec -it connet-postgres-debug psql -U postgres -d connet_db"
echo "  进入 Redis CLI: docker exec -it connet-redis-debug redis-cli"
echo ""
echo "📁 数据持久化目录："
echo "  PostgreSQL: ./data/postgres"
echo "  Redis: ./data/redis" 
#!/bin/bash
# 本地调试环境停止脚本

set -e

echo "🛑 停止本地调试环境"
echo "=================="

# 停止所有调试容器
echo "停止 PostgreSQL 和 Redis 服务..."
docker-compose -f docker-compose.debug.yml down

# 显示状态
echo "📊 检查容器状态..."
docker ps --filter "name=connet-*-debug" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "✅ 调试环境已停止"
echo ""
echo "💡 其他操作："
echo "  完全清理(删除数据): docker-compose -f docker-compose.debug.yml down -v"
echo "  查看容器日志: docker-compose -f docker-compose.debug.yml logs"
echo "  重启服务: ./scripts/debug-start.sh" 
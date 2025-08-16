#!/bin/bash
# Docker 问题修复脚本
# 解决 Docker Hub 403 Forbidden 错误

set -e

echo "🔧 Docker 问题修复脚本"
echo "========================"

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 未运行，请启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 正在运行"

# 方案1: 配置 Docker 镜像代理
echo ""
echo "📋 方案1: 配置 Docker 镜像代理"
echo "================================"

# 检查操作系统
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "检测到 Windows 系统"
    echo "请手动配置 Docker Desktop 镜像代理："
    echo "1. 打开 Docker Desktop"
    echo "2. 进入 Settings -> Docker Engine"
    echo "3. 添加以下配置到 JSON:"
    echo '{'
    echo '  "registry-mirrors": ['
    echo '    "https://docker.mirrors.ustc.edu.cn",'
    echo '    "https://hub-mirror.c.163.com",'
    echo '    "https://mirror.baidubce.com"'
    echo '  ],'
    echo '  "insecure-registries": []'
    echo '}'
    echo "4. 点击 Apply & Restart"
    echo ""
    echo "配置完成后，请按 Enter 继续..."
    read -p ""
else
    # Linux/MacOS 自动配置
    echo "配置 Docker 镜像代理..."
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "insecure-registries": []
}
EOF
    sudo systemctl restart docker
    echo "✅ Docker 镜像代理配置完成"
fi

# 方案2: 使用预构建镜像
echo ""
echo "📋 方案2: 创建简化版 Dockerfile"
echo "==============================="

cat > Dockerfile.simple <<EOF
# 简化版 Dockerfile - 使用轻量级基础镜像
FROM python:3.11-alpine

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Alpine 使用 apk）
RUN apk update && apk add --no-cache \\
    gcc \\
    musl-dev \\
    postgresql-dev \\
    curl

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# 运行应用
CMD ["python", "-m", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "✅ 创建了 Dockerfile.simple"

# 方案3: 更新 docker-compose 使用简化镜像
echo ""
echo "📋 方案3: 更新 Docker Compose 配置"
echo "=================================="

# 备份原配置
cp docker-compose.local.yml docker-compose.local.yml.backup

# 更新 docker-compose 文件
sed -i 's/dockerfile: Dockerfile/dockerfile: Dockerfile.simple/' docker-compose.local.yml || \
sed -i '' 's/dockerfile: Dockerfile/dockerfile: Dockerfile.simple/' docker-compose.local.yml

echo "✅ 更新了 docker-compose.local.yml 使用 Dockerfile.simple"

# 方案4: 清理并重试
echo ""
echo "📋 方案4: 清理 Docker 缓存并重试"
echo "==============================="

echo "清理 Docker 缓存..."
docker system prune -f
docker builder prune -f

echo "✅ Docker 缓存清理完成"

# 测试构建
echo ""
echo "🧪 测试构建"
echo "============"

echo "尝试构建镜像..."
if docker build -f Dockerfile.simple -t connet-bff-test . ; then
    echo "✅ 镜像构建成功！"
    echo "现在可以运行: docker-compose -f docker-compose.local.yml up -d"
else
    echo "❌ 构建失败，尝试手动拉取基础镜像..."
    
    # 尝试手动拉取镜像
    echo "尝试拉取 python:3.11-alpine..."
    if docker pull python:3.11-alpine; then
        echo "✅ Alpine 镜像拉取成功，重新构建..."
        docker build -f Dockerfile.simple -t connet-bff-test .
    else
        echo "❌ 仍然无法拉取镜像"
        echo ""
        echo "🔧 手动解决方案："
        echo "1. 检查网络连接"
        echo "2. 配置 VPN 或代理"
        echo "3. 使用公司内网镜像（如果有的话）"
        echo "4. 联系网络管理员"
    fi
fi

echo ""
echo "🎯 修复完成！"
echo "============="
echo "如果问题仍然存在，请尝试："
echo "1. 重启 Docker Desktop"
echo "2. 检查防火墙设置"
echo "3. 使用企业代理设置" 
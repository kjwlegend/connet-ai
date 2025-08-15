#!/bin/bash

# Connet.AI BFF - Docker 快速启动脚本
# 用于本地开发环境的一键部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 和 Docker Compose
check_prerequisites() {
    print_status "检查先决条件..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker 守护进程未运行，请启动 Docker"
        exit 1
    fi
    
    print_success "先决条件检查通过"
}

# 创建必要的目录
create_directories() {
    print_status "创建必要的目录..."
    
    mkdir -p uploads
    mkdir -p logs
    mkdir -p docker/ssl
    
    print_success "目录创建完成"
}

# 检查并创建环境文件
setup_environment() {
    print_status "设置环境变量..."
    
    if [ ! -f .env ]; then
        print_warning ".env 文件不存在，将使用 docker-compose 中的默认环境变量"
        print_warning "如需自定义配置，请复制 .env.example 为 .env 并修改相应配置"
    else
        print_success "发现 .env 文件，将使用自定义环境变量"
    fi
}

# 清理旧容器和镜像
cleanup() {
    print_status "清理旧容器和镜像..."
    
    # 停止并删除容器
    docker-compose -f docker-compose.local.yml down --remove-orphans 2>/dev/null || true
    
    # 删除悬空镜像
    docker image prune -f 2>/dev/null || true
    
    print_success "清理完成"
}

# 构建和启动服务
start_services() {
    print_status "构建并启动服务..."
    
    # 构建镜像
    print_status "构建 BFF 镜像..."
    docker-compose -f docker-compose.local.yml build bff
    
    # 启动基础服务 (数据库和 Redis)
    print_status "启动数据库和 Redis..."
    docker-compose -f docker-compose.local.yml up -d db redis
    
    # 等待数据库就绪
    print_status "等待数据库启动..."
    sleep 10
    
    # 运行数据库迁移
    print_status "运行数据库迁移..."
    docker-compose -f docker-compose.local.yml run --rm bff alembic upgrade head || print_warning "数据库迁移失败，可能是首次运行"
    
    # 启动 BFF 服务
    print_status "启动 BFF 服务..."
    docker-compose -f docker-compose.local.yml up -d bff
    
    print_success "基础服务启动完成"
}

# 启动可选工具 (仅邮件测试工具)
start_tools() {
    if [ "$1" = "--with-tools" ]; then
        print_status "启动邮件测试工具..."
        docker-compose -f docker-compose.local.yml --profile tools up -d
        print_success "邮件测试工具启动完成"
    fi
}

# 启动代理服务 (已移除 Nginx)
start_proxy() {
    if [ "$1" = "--with-proxy" ]; then
        print_warning "Nginx 代理已从配置中移除"
    fi
}

# 显示服务状态和访问信息
show_status() {
    print_status "检查服务状态..."
    sleep 5
    
    echo ""
    echo "=== 🚀 Connet.AI BFF 服务状态 ==="
    echo ""
    
    # 检查服务状态
    if docker-compose -f docker-compose.local.yml ps | grep -q "Up"; then
        print_success "服务运行中"
        
        echo ""
        echo "📊 服务访问地址:"
        echo "  • FastAPI 服务:     http://localhost:8000"
        echo "  • API 文档 (Swagger): http://localhost:8000/docs"
        echo "  • API 文档 (ReDoc):   http://localhost:8000/redoc"
        echo "  • 健康检查:         http://localhost:8000/health"
        echo ""
        echo "🗄️  数据库服务:"
        echo "  • PostgreSQL:       localhost:5432"
        echo "  • Redis:           localhost:6379"
        echo ""
        
        # 检查工具服务
        if docker-compose -f docker-compose.local.yml ps | grep -q "mailhog"; then
            echo "🛠️  开发工具:"
            echo "  • MailHog:         http://localhost:8025"
            echo ""
        fi
        

        
        echo "📝 有用的命令:"
        echo "  • 查看日志: docker-compose -f docker-compose.local.yml logs -f bff"
        echo "  • 停止服务: docker-compose -f docker-compose.local.yml down"
        echo "  • 重启服务: docker-compose -f docker-compose.local.yml restart bff"
        echo "  • 进入容器: docker-compose -f docker-compose.local.yml exec bff bash"
        echo ""
        
    else
        print_error "服务启动失败，请检查日志"
        docker-compose -f docker-compose.local.yml logs
        exit 1
    fi
}

# 主函数
main() {
    echo ""
    echo "🚀 Connet.AI BFF Docker 快速启动"
    echo "=================================="
    echo ""
    
    # 解析参数
    TOOLS=""
    PROXY=""
    CLEAN=""
    
    for arg in "$@"; do
        case $arg in
            --with-tools)
                TOOLS="--with-tools"
                ;;
            --with-proxy)
                PROXY="--with-proxy"
                ;;
            --clean)
                CLEAN="--clean"
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --with-tools    启动开发工具 (MailHog)"
                echo "  --clean         清理旧容器和镜像"
                echo "  --help          显示此帮助信息"
                echo ""
                echo "示例:"
                echo "  $0                          # 启动基础服务"
                echo "  $0 --with-tools             # 启动服务和开发工具"
                echo "  $0 --clean                  # 清理并重新启动"
                exit 0
                ;;
        esac
    done
    
    # 执行步骤
    check_prerequisites
    create_directories
    setup_environment
    
    if [ "$CLEAN" = "--clean" ]; then
        cleanup
    fi
    
    start_services
    start_tools "$TOOLS"
    start_proxy "$PROXY"
    show_status
    
    print_success "🎉 启动完成！服务已就绪"
}

# 执行主函数
main "$@" 
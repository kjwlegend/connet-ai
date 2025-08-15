#!/bin/bash

# Connet.AI BFF - Docker 停止脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 主函数
main() {
    echo ""
    echo "🛑 Connet.AI BFF Docker 停止服务"
    echo "================================"
    echo ""
    
    # 解析参数
    REMOVE_VOLUMES=""
    REMOVE_IMAGES=""
    
    for arg in "$@"; do
        case $arg in
            --remove-volumes)
                REMOVE_VOLUMES="--volumes"
                ;;
            --remove-images)
                REMOVE_IMAGES="true"
                ;;
            --help)
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --remove-volumes    同时删除数据卷 (⚠️  会删除数据库数据)"
                echo "  --remove-images     同时删除 Docker 镜像"
                echo "  --help             显示此帮助信息"
                echo ""
                echo "示例:"
                echo "  $0                      # 停止服务"
                echo "  $0 --remove-volumes     # 停止服务并删除数据"
                echo "  $0 --remove-images      # 停止服务并删除镜像"
                exit 0
                ;;
        esac
    done
    
    # 停止服务
    print_status "停止 Docker 服务..."
    
    if [ -f docker-compose.local.yml ]; then
        docker-compose -f docker-compose.local.yml down --remove-orphans $REMOVE_VOLUMES
        print_success "服务已停止"
    else
        print_error "找不到 docker-compose.local.yml 文件"
        exit 1
    fi
    
    # 删除镜像
    if [ "$REMOVE_IMAGES" = "true" ]; then
        print_status "删除 Docker 镜像..."
        
        # 删除应用镜像
        docker rmi connet-ai-bff 2>/dev/null || print_warning "应用镜像不存在"
        
        # 删除悬空镜像
        docker image prune -f 2>/dev/null || true
        
        print_success "镜像删除完成"
    fi
    
    # 显示状态
    echo ""
    print_status "当前 Docker 状态:"
    echo ""
    
    # 显示容器状态
    CONTAINERS=$(docker ps -a --filter "name=connet-" --format "table {{.Names}}\t{{.Status}}")
    if [ -n "$CONTAINERS" ]; then
        echo "相关容器:"
        echo "$CONTAINERS"
    else
        echo "没有相关容器运行"
    fi
    
    echo ""
    
    # 显示数据卷状态
    if [ "$REMOVE_VOLUMES" != "--volumes" ]; then
        VOLUMES=$(docker volume ls --filter "name=bff_" --format "table {{.Name}}")
        if [ -n "$VOLUMES" ] && [ "$VOLUMES" != "NAME" ]; then
            echo "数据卷 (数据保留):"
            echo "$VOLUMES"
            echo ""
            print_warning "数据卷未删除，重启时数据会保留"
            print_warning "如需完全清理，请使用 --remove-volumes 选项"
        fi
    else
        print_warning "⚠️  数据卷已删除，所有数据已清除"
    fi
    
    echo ""
    print_success "🎉 停止完成！"
    
    if [ "$REMOVE_VOLUMES" != "--volumes" ]; then
        echo ""
        echo "💡 提示:"
        echo "  • 重新启动: ./scripts/docker-start.sh"
        echo "  • 完全清理: ./scripts/docker-stop.sh --remove-volumes --remove-images"
    fi
}

# 执行主函数
main "$@" 
#!/bin/bash

# Connet.AI BFF - Docker 环境测试脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# 测试 API 健康检查
test_api_health() {
    print_status "测试 API 健康检查..."
    
    if curl -f -s http://localhost:8000/health > /dev/null; then
        print_success "API 健康检查通过"
        return 0
    else
        print_error "API 健康检查失败"
        return 1
    fi
}

# 测试数据库连接
test_database() {
    print_status "测试数据库连接..."
    
    if docker-compose -f docker-compose.local.yml exec -T db pg_isready -U postgres -d connet_ai > /dev/null 2>&1; then
        print_success "数据库连接正常"
        return 0
    else
        print_error "数据库连接失败"
        return 1
    fi
}

# 测试 Redis 连接
test_redis() {
    print_status "测试 Redis 连接..."
    
    if docker-compose -f docker-compose.local.yml exec -T redis redis-cli ping | grep -q "PONG"; then
        print_success "Redis 连接正常"
        return 0
    else
        print_error "Redis 连接失败"
        return 1
    fi
}

# 测试 API 文档
test_api_docs() {
    print_status "测试 API 文档..."
    
    if curl -f -s http://localhost:8000/docs > /dev/null; then
        print_success "API 文档可访问"
        return 0
    else
        print_error "API 文档不可访问"
        return 1
    fi
}

# 测试容器状态
test_containers() {
    print_status "检查容器状态..."
    
    local failed=0
    
    # 检查必要的容器
    containers=("connet-bff" "connet-postgres" "connet-redis")
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
            print_success "容器 $container 运行中"
        else
            print_error "容器 $container 未运行"
            failed=1
        fi
    done
    
    return $failed
}

# 运行所有测试
run_all_tests() {
    echo ""
    echo "🧪 Connet.AI BFF Docker 环境测试"
    echo "==============================="
    echo ""
    
    local total_tests=0
    local passed_tests=0
    
    # 测试列表
    tests=(
        "test_containers"
        "test_database" 
        "test_redis"
        "test_api_health"
        "test_api_docs"
    )
    
    # 运行测试
    for test in "${tests[@]}"; do
        total_tests=$((total_tests + 1))
        
        if $test; then
            passed_tests=$((passed_tests + 1))
        fi
        
        echo ""
    done
    
    # 显示结果
    echo "测试结果: $passed_tests/$total_tests 通过"
    echo ""
    
    if [ $passed_tests -eq $total_tests ]; then
        print_success "🎉 所有测试通过！Docker 环境运行正常"
        
        echo ""
        echo "📊 服务访问地址:"
        echo "  • FastAPI:     http://localhost:8000"
        echo "  • API 文档:    http://localhost:8000/docs"
        echo "  • 健康检查:    http://localhost:8000/health"
        echo ""
        
        return 0
    else
        print_error "❌ 部分测试失败，请检查 Docker 环境"
        
        echo ""
        echo "🔍 故障排除:"
        echo "  • 查看日志: make docker-logs"
        echo "  • 检查状态: make docker-status"
        echo "  • 重启服务: make docker-restart"
        echo ""
        
        return 1
    fi
}

# 主函数
main() {
    # 检查参数
    case "${1:-}" in
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --help        显示此帮助信息"
            echo "  --quick       快速测试 (仅测试 API)"
            echo ""
            echo "示例:"
            echo "  $0            # 运行完整测试"
            echo "  $0 --quick    # 快速测试"
            exit 0
            ;;
        --quick)
            print_status "运行快速测试..."
            test_api_health
            exit $?
            ;;
        "")
            run_all_tests
            exit $?
            ;;
        *)
            print_error "未知选项: $1"
            echo "使用 $0 --help 查看帮助"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 
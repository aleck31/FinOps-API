#!/bin/bash

# AWS FinOps 项目运行脚本
# 用法: ./run.sh [start|restart|stop|status|web|demo|test|install]

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT=$(pwd)
API_DIR="$PROJECT_ROOT/finops_api"
WEB_DIR="$PROJECT_ROOT/webui"
LOGS_DIR="$PROJECT_ROOT/logs"
API_PID_FILE="$PROJECT_ROOT/api_server.pid"
WEB_PID_FILE="$PROJECT_ROOT/web_server.pid"

# 创建必要的目录
mkdir -p "$LOGS_DIR"

# 显示标题
show_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "           AWS FinOps 运行管理"
    echo "=================================================="
    echo -e "${NC}"
}

# 安装依赖
install_deps() {
    echo -e "${YELLOW}安装项目依赖...${NC}"
    uv sync
    echo -e "${GREEN}依赖安装完成${NC}"
}

# 启动API服务器
start_api() {
    if [ -f "$API_PID_FILE" ] && kill -0 $(cat "$API_PID_FILE") 2>/dev/null; then
        echo -e "${YELLOW}API服务器已在运行中 (PID: $(cat $API_PID_FILE))${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}启动FinOps API服务...${NC}"
    cd "$API_DIR"
    export AWS_PROFILE=${AWS_PROFILE:-default}
    nohup uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$LOGS_DIR/api_server.log" 2>&1 &
    echo $! > "$API_PID_FILE"
    sleep 3
    
    if kill -0 $(cat "$API_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ API服务器启动成功 (PID: $(cat $API_PID_FILE))${NC}"
        echo -e "${GREEN}🌐 API地址: http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API文档: http://localhost:8000/docs${NC}"
    else
        echo -e "${RED}❌ API服务器启动失败${NC}"
        rm -f "$API_PID_FILE"
        return 1
    fi
}

# 停止API服务器
stop_api() {
    if [ -f "$API_PID_FILE" ]; then
        PID=$(cat "$API_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${YELLOW}停止API服务器 (PID: $PID)...${NC}"
            kill "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}强制停止API服务器...${NC}"
                kill -9 "$PID"
            fi
            echo -e "${GREEN}✅ API服务器已停止${NC}"
        else
            echo -e "${YELLOW}API服务器进程不存在${NC}"
        fi
        rm -f "$API_PID_FILE"
    else
        echo -e "${YELLOW}没有找到API服务器PID文件${NC}"
    fi
    
    # 清理所有可能的uvicorn进程
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
}

# 启动Web演示服务器
start_web() {
    if [ -f "$WEB_PID_FILE" ] && kill -0 $(cat "$WEB_PID_FILE") 2>/dev/null; then
        echo -e "${YELLOW}Web演示服务器已在运行中 (PID: $(cat $WEB_PID_FILE))${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}启动Web演示服务器...${NC}"
    cd "$WEB_DIR"
    nohup uv run python demo_server.py --port 3000 > "$LOGS_DIR/web_server.log" 2>&1 &
    echo $! > "$WEB_PID_FILE"
    sleep 3
    
    if kill -0 $(cat "$WEB_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ Web演示服务器启动成功 (PID: $(cat $WEB_PID_FILE))${NC}"
        echo -e "${GREEN}🌐 Web演示地址: http://localhost:3000${NC}"
    else
        echo -e "${RED}❌ Web演示服务器启动失败${NC}"
        rm -f "$WEB_PID_FILE"
        return 1
    fi
}

# 停止Web演示服务器
stop_web() {
    if [ -f "$WEB_PID_FILE" ]; then
        PID=$(cat "$WEB_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${YELLOW}停止Web演示服务器 (PID: $PID)...${NC}"
            kill "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}强制停止Web演示服务器...${NC}"
                kill -9 "$PID"
            fi
            echo -e "${GREEN}✅ Web演示服务器已停止${NC}"
        else
            echo -e "${YELLOW}Web演示服务器进程不存在${NC}"
        fi
        rm -f "$WEB_PID_FILE"
    else
        echo -e "${YELLOW}没有找到Web演示服务器PID文件${NC}"
    fi
    
    # 清理所有可能的demo_server进程
    pkill -f "demo_server.py" 2>/dev/null || true
}

# 重启API服务器
restart_api() {
    echo -e "${YELLOW}重启API服务器...${NC}"
    stop_api
    sleep 2
    start_api
}

# 重启Web演示服务器
restart_web() {
    echo -e "${YELLOW}重启Web演示服务器...${NC}"
    stop_web
    sleep 2
    start_web
}

# 启动所有服务
start_all() {
    echo -e "${YELLOW}启动所有服务...${NC}"
    start_api
    sleep 2
    start_web
}

# 停止所有服务
stop_all() {
    echo -e "${YELLOW}停止所有服务...${NC}"
    stop_api
    stop_web
}

# 重启所有服务
restart_all() {
    echo -e "${YELLOW}重启所有服务...${NC}"
    stop_all
    sleep 3
    start_all
}

# 检查服务器状态
check_status() {
    echo -e "${BLUE}=== 服务状态检查 ===${NC}"
    
    # 检查API服务器
    echo -e "${BLUE}--- API服务器 ---${NC}"
    if [ -f "$API_PID_FILE" ]; then
        PID=$(cat "$API_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}✅ API服务器运行中 (PID: $PID)${NC}"
            
            # 检查API响应
            if curl -s http://localhost:8000/health >/dev/null 2>&1; then
                echo -e "${GREEN}✅ API健康检查通过${NC}"
                echo -e "${GREEN}🌐 API地址: http://localhost:8000${NC}"
                echo -e "${GREEN}📚 API文档: http://localhost:8000/docs${NC}"
            else
                echo -e "${RED}❌ API无响应${NC}"
            fi
        else
            echo -e "${RED}❌ API服务器进程不存在${NC}"
            rm -f "$API_PID_FILE"
        fi
    else
        echo -e "${RED}❌ API服务器未运行${NC}"
    fi
    
    # 检查Web演示服务器
    echo -e "${BLUE}--- Web演示服务器 ---${NC}"
    if [ -f "$WEB_PID_FILE" ]; then
        PID=$(cat "$WEB_PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Web演示服务器运行中 (PID: $PID)${NC}"
            
            # 检查Web响应
            if curl -s http://localhost:3000 >/dev/null 2>&1; then
                echo -e "${GREEN}✅ Web演示页面可访问${NC}"
                echo -e "${GREEN}🌐 Web演示地址: http://localhost:3000${NC}"
            else
                echo -e "${RED}❌ Web演示页面无响应${NC}"
            fi
        else
            echo -e "${RED}❌ Web演示服务器进程不存在${NC}"
            rm -f "$WEB_PID_FILE"
        fi
    else
        echo -e "${RED}❌ Web演示服务器未运行${NC}"
    fi
    
    # 检查端口占用
    echo -e "${BLUE}--- 端口占用情况 ---${NC}"
    if lsof -i :8000 >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口8000被占用${NC}"
        lsof -i :8000 | head -3
    fi
    if lsof -i :3000 >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口3000被占用${NC}"
        lsof -i :3000 | head -3
    fi
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}运行测试套件...${NC}"
    cd "$PROJECT_ROOT"
    uv run python tests/simple_test.py
}

# 显示使用帮助
show_help() {
    echo -e "${BLUE}AWS FinOps 项目运行管理${NC}"
    echo ""
    echo "用法: ./run.sh [命令]"
    echo ""
    echo "服务管理命令:"
    echo "  start         启动所有服务(API&Web)"
    echo "  stop          停止所有服务"
    echo "  restart       重启所有服务"s
    echo "  status        检查服务状态"
    echo "  api           启动API服务器"
    echo "  stop-api      停止API服务器"
    echo "  restart-api   重启API服务器"
    echo "  web           启动Web演示服务器"
    echo "  stop-web      停止Web演示服务器"
    echo "  restart-web   重启Web演示服务器"
    echo ""
    echo "其他命令:"
    echo "  install       安装项目依赖"
    echo "  demo          启动完整演示环境"
    echo "  test          运行测试套件"
    echo "  help          显示此帮助信息"
}

# 主逻辑
main() {
    show_header
    
    case "${1:-help}" in
        "start")
            install_deps
            start_all
            ;;
        "stop")
            stop_all
            ;;
        "restart")
            restart_all
            ;;
        "status")
            check_status
            ;;
        "api"|"start-api")
            install_deps
            start_api
            ;;
        "stop-api")
            stop_api
            ;;
        "restart-api")
            restart_api
            ;;
        "web"|"start-web")
            install_deps
            start_web
            ;;
        "stop-web")
            stop_web
            ;;
        "restart-web")
            restart_web
            ;;
        "install")
            install_deps
            ;;
        "test")
            run_tests
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"

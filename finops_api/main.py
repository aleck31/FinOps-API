#!/usr/bin/env python3
"""
AWS FinOps API 主应用
重构版本 - 使用APIRouter进行模块化组织
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from models import APIResponse
from dependencies import init_clients
from routers import (
    costs_router,
    budgets_router,
    metrics_router,
    inventory_router,
    optimization_router,
    reports_router
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/finops_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化客户端
    logger.info("初始化AWS客户端...")
    init_clients()
    logger.info("AWS客户端初始化完成")
    
    yield
    
    # 关闭时清理资源
    logger.info("清理资源...")

# 创建FastAPI应用
app = FastAPI(
    title="AWS FinOps API",
    description="AWS财务运营(FinOps)数据API服务 - 提供成本、预算、监控、清单和优化建议",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(costs_router)
app.include_router(budgets_router)
app.include_router(metrics_router)
app.include_router(inventory_router)
app.include_router(optimization_router)
app.include_router(reports_router)

# 基础路由
@app.get("/", response_model=APIResponse)
async def root():
    """根路径"""
    return APIResponse(
        success=True,
        message="AWS FinOps API 服务正在运行",
        data={
            "version": "2.0.0",
            "description": "AWS财务运营数据API服务",
            "endpoints": {
                "成本管理": "/api/v1/costs/*",
                "预算监控": "/api/v1/budgets/*",
                "资源监控": "/api/v1/metrics/*",
                "资源清单": "/api/v1/inventory/*",
                "优化建议": "/api/v1/optimization/*",
                "综合报告": "/api/v1/reports/*"
            }
        }
    )

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    import argparse
    import os
    from pathlib import Path
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='AWS FinOps API 服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--reload', action='store_true', help='启用自动重载')
    parser.add_argument('--log-level', default='info', 
                       choices=['debug', 'info', 'warning', 'error'],
                       help='日志级别')
    parser.add_argument('--workers', type=int, default=1, help='工作进程数')
    
    args = parser.parse_args()
    
    # 检查AWS凭证
    if not (os.getenv('AWS_ACCESS_KEY_ID') or os.path.exists(Path.home() / '.aws' / 'credentials')):
        print("警告: 未检测到AWS凭证配置")
        print("请确保已配置AWS凭证:")
        print("1. 使用 aws configure 命令")
        print("2. 或设置环境变量 AWS_ACCESS_KEY_ID 和 AWS_SECRET_ACCESS_KEY")
        print("3. 或使用IAM角色")
    
    print(f"启动AWS FinOps API服务器...")
    print(f"服务器地址: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    print(f"日志级别: {args.log_level}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        workers=args.workers if not args.reload else 1
    )

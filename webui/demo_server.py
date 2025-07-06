#!/usr/bin/env python3
"""
演示Web服务器
提供FinOps API的演示页面
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import argparse
from pathlib import Path

# 创建FastAPI应用
demo_app = FastAPI(
    title="AWS FinOps API Demo",
    description="AWS FinOps API 演示页面服务器",
    version="1.0.0"
)

@demo_app.get("/", response_class=HTMLResponse)
async def demo_page():
    """返回演示页面"""
    demo_file = Path(__file__).parent / "index.html"
    if demo_file.exists():
        return HTMLResponse(content=demo_file.read_text(encoding='utf-8'))
    else:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>演示页面未找到</h1>
                <p>请确保 index.html 文件存在</p>
            </body>
        </html>
        """)

@demo_app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "demo"}

def main():
    parser = argparse.ArgumentParser(description='AWS FinOps API 演示服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=3000, help='服务器端口')
    parser.add_argument('--api-url', default='http://localhost:8000', help='API服务器地址')
    
    args = parser.parse_args()
    
    print(f"启动演示服务器...")
    print(f"演示页面: http://{args.host}:{args.port}")
    print(f"API服务器: {args.api_url}")
    
    uvicorn.run(
        demo_app,
        host=args.host,
        port=args.port,
        log_level="info"
    )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
测试服务启动脚本
"""

import asyncio
import aiohttp
import time
import subprocess
import signal
import os
from pathlib import Path

async def test_api_endpoints():
    """测试API端点"""
    base_url = "http://127.0.0.1:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 测试健康检查
            print("测试健康检查端点...")
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 健康检查成功: {data}")
                else:
                    print(f"❌ 健康检查失败: {response.status}")
            
            # 测试根路径
            print("\n测试根路径...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 根路径访问成功: {data}")
                else:
                    print(f"❌ 根路径访问失败: {response.status}")
            
            # 测试API文档
            print("\n测试API文档...")
            async with session.get(f"{base_url}/docs") as response:
                if response.status == 200:
                    print("✅ API文档可访问")
                else:
                    print(f"❌ API文档访问失败: {response.status}")
                    
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")

def main():
    """主函数"""
    print("=== AWS FinOps API 启动测试 ===\n")
    
    # 启动服务器
    print("启动FastAPI服务器...")
    server_process = subprocess.Popen([
        "uv", "run", "uvicorn", "main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--log-level", "info"
    ], cwd=Path(__file__).parent)
    
    try:
        # 等待服务器启动
        print("等待服务器启动...")
        time.sleep(5)
        
        # 运行测试
        asyncio.run(test_api_endpoints())
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        # 停止服务器
        print("\n停止服务器...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("服务器已停止")

if __name__ == "__main__":
    main()

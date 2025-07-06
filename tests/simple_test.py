#!/usr/bin/env python3
"""
简单的API测试脚本
"""

import requests
import time
import json

def test_api():
    """测试API端点"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== AWS FinOps API 测试 ===\n")
    
    try:
        # 测试健康检查
        print("1. 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
        
        # 测试根路径
        print("\n2. 测试根路径...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根路径访问成功")
            print(f"   消息: {data.get('message', 'N/A')}")
            print(f"   版本: {data.get('data', {}).get('version', 'N/A')}")
        else:
            print(f"❌ 根路径访问失败: {response.status_code}")
        
        # 测试OpenAPI文档
        print("\n3. 测试OpenAPI规范...")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_spec = response.json()
            print(f"✅ OpenAPI规范可访问")
            print(f"   标题: {openapi_spec.get('info', {}).get('title', 'N/A')}")
            print(f"   版本: {openapi_spec.get('info', {}).get('version', 'N/A')}")
            print(f"   端点数量: {len(openapi_spec.get('paths', {}))}")
        else:
            print(f"❌ OpenAPI规范访问失败: {response.status_code}")
            
        print(f"\n✅ 基础API测试完成！")
        print(f"🌐 API文档地址: {base_url}/docs")
        print(f"📚 ReDoc文档地址: {base_url}/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务器")
        print("请确保服务器正在运行: uv run python start_server.py")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_api()

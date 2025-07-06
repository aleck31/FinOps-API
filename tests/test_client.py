#!/usr/bin/env python3
"""
AWS FinOps API 测试客户端
演示如何调用API接口
"""

import requests
import json
import time
from typing import Dict, Optional

class FinOpsAPIClient:
    """FinOps API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化API客户端
        
        Args:
            base_url: API服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        发起HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 请求参数
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"响应内容: {e.response.text}")
            raise
    
    def health_check(self) -> Dict:
        """健康检查"""
        return self._make_request('GET', '/health')
    
    def get_daily_costs(self, days: int = 30, granularity: str = 'DAILY') -> Dict:
        """获取每日成本数据"""
        params = {'days': days, 'granularity': granularity}
        return self._make_request('GET', '/api/v1/costs/daily', params=params)
    
    def get_costs_by_service(self, days: int = 30) -> Dict:
        """获取按服务分组的成本数据"""
        params = {'days': days}
        return self._make_request('GET', '/api/v1/costs/by-service', params=params)
    
    def get_costs_by_tags(self, tag_key: str, days: int = 30) -> Dict:
        """获取按标签分组的成本数据"""
        params = {'tag_key': tag_key, 'days': days}
        return self._make_request('GET', '/api/v1/costs/by-tags', params=params)
    
    def get_cost_forecast(self, days: int = 30) -> Dict:
        """获取成本预测数据"""
        params = {'days': days}
        return self._make_request('GET', '/api/v1/costs/forecast', params=params)
    
    def get_budgets(self) -> Dict:
        """获取所有预算信息"""
        return self._make_request('GET', '/api/v1/budgets')
    
    def get_budget_details(self, budget_name: str) -> Dict:
        """获取特定预算的详细信息"""
        return self._make_request('GET', f'/api/v1/budgets/{budget_name}')
    
    def get_ec2_metrics(self, instance_id: Optional[str] = None, 
                       metric_name: str = 'CPUUtilization', 
                       hours: int = 24) -> Dict:
        """获取EC2实例指标"""
        params = {'metric_name': metric_name, 'hours': hours}
        if instance_id:
            params['instance_id'] = instance_id
        return self._make_request('GET', '/api/v1/metrics/ec2', params=params)
    
    def get_rds_metrics(self, db_instance_identifier: str, 
                       metric_name: str = 'CPUUtilization', 
                       hours: int = 24) -> Dict:
        """获取RDS实例指标"""
        params = {
            'db_instance_identifier': db_instance_identifier,
            'metric_name': metric_name,
            'hours': hours
        }
        return self._make_request('GET', '/api/v1/metrics/rds', params=params)
    
    def get_lambda_metrics(self, function_name: str, 
                          metric_name: str = 'Invocations', 
                          hours: int = 24) -> Dict:
        """获取Lambda函数指标"""
        params = {
            'function_name': function_name,
            'metric_name': metric_name,
            'hours': hours
        }
        return self._make_request('GET', '/api/v1/metrics/lambda', params=params)
    
    def get_cost_summary(self, days: int = 30) -> Dict:
        """获取成本汇总报告"""
        params = {'days': days}
        return self._make_request('GET', '/api/v1/reports/cost-summary', params=params)


def demo_api_calls():
    """演示API调用"""
    client = FinOpsAPIClient()
    
    print("=== AWS FinOps API 演示 ===\n")
    
    try:
        # 1. 健康检查
        print("1. 健康检查")
        health = client.health_check()
        print(f"服务状态: {health['status']}")
        print(f"时间戳: {health['timestamp']}")
        print()
        
        # 2. 获取每日成本数据
        print("2. 获取每日成本数据 (过去7天)")
        daily_costs = client.get_daily_costs(days=7)
        if daily_costs['success']:
            data = daily_costs['data']
            print(f"总成本: ${data['total_cost']:.2f}")
            print(f"数据点数量: {len(data['daily_costs'])}")
        print()
        
        # 3. 获取按服务分组的成本
        print("3. 获取按服务分组的成本 (过去30天)")
        service_costs = client.get_costs_by_service(days=30)
        if service_costs['success']:
            data = service_costs['data']
            print(f"总成本: ${data['total_cost']:.2f}")
            print("前5个服务:")
            for service in data['services'][:5]:
                print(f"  - {service['name']}: ${service['cost']:.2f}")
        print()
        
        # 4. 获取成本预测
        print("4. 获取成本预测 (未来7天)")
        forecast = client.get_cost_forecast(days=7)
        if forecast['success']:
            data = forecast['data']
            print(f"预测总成本: ${data['total_forecast']:.2f}")
            print(f"预测数据点数量: {len(data['forecast_results'])}")
        print()
        
        # 5. 获取预算信息
        print("5. 获取预算信息")
        budgets = client.get_budgets()
        if budgets['success']:
            data = budgets['data']
            print(f"预算数量: {data['budgets_count']}")
            for budget in data['budgets']:
                print(f"  - {budget['budget_name']}: ${budget['budgeted_amount']:.2f}")
        print()
        
        # 6. 获取EC2指标
        print("6. 获取EC2指标 (CPU使用率)")
        ec2_metrics = client.get_ec2_metrics(hours=24)
        if ec2_metrics['success']:
            data = ec2_metrics['data']
            print(f"监控实例数量: {len(data['instances'])}")
            for instance in data['instances'][:3]:  # 只显示前3个
                print(f"  - 实例 {instance['instance_id']}: {len(instance['datapoints'])} 个数据点")
        print()
        
        # 7. 获取成本汇总报告
        print("7. 获取成本汇总报告")
        summary = client.get_cost_summary(days=30)
        if summary['success']:
            data = summary['data']
            print(f"报告期间: {data['period']['start']} 到 {data['period']['end']}")
            print(f"总成本: ${data['total_cost']:.2f}")
            print(f"预算数量: {len(data['budget_status'])}")
            print(f"每日趋势数据点: {len(data['daily_trend'])}")
        print()
        
    except Exception as e:
        print(f"演示过程中出现错误: {str(e)}")


def monitor_costs_example():
    """监控成本示例 - 模拟监控平台的调用方式"""
    client = FinOpsAPIClient()
    
    print("=== 监控平台集成示例 ===\n")
    
    # 模拟监控平台定期获取数据
    monitoring_data = {}
    
    try:
        # 获取关键指标
        print("正在获取关键FinOps指标...")
        
        # 1. 当前成本趋势
        daily_costs = client.get_daily_costs(days=7)
        if daily_costs['success']:
            monitoring_data['daily_costs'] = daily_costs['data']
        
        # 2. 服务成本分布
        service_costs = client.get_costs_by_service(days=30)
        if service_costs['success']:
            monitoring_data['service_costs'] = service_costs['data']
        
        # 3. 预算状态
        budgets = client.get_budgets()
        if budgets['success']:
            monitoring_data['budgets'] = budgets['data']
        
        # 4. 资源利用率 (EC2)
        ec2_metrics = client.get_ec2_metrics(hours=24)
        if ec2_metrics['success']:
            monitoring_data['ec2_metrics'] = ec2_metrics['data']
        
        # 输出监控数据摘要
        print("\n=== 监控数据摘要 ===")
        
        if 'daily_costs' in monitoring_data:
            total_cost = monitoring_data['daily_costs']['total_cost']
            print(f"过去7天总成本: ${total_cost:.2f}")
        
        if 'service_costs' in monitoring_data:
            top_service = monitoring_data['service_costs']['services'][0]
            print(f"最高成本服务: {top_service['name']} (${top_service['cost']:.2f})")
        
        if 'budgets' in monitoring_data:
            budget_count = monitoring_data['budgets']['budgets_count']
            print(f"活跃预算数量: {budget_count}")
            
            # 检查预算告警
            for budget in monitoring_data['budgets']['budgets']:
                if budget.get('status') in ['WARNING', 'EXCEEDED']:
                    print(f"⚠️  预算告警: {budget['budget_name']} - {budget['status']}")
        
        if 'ec2_metrics' in monitoring_data:
            instance_count = len(monitoring_data['ec2_metrics']['instances'])
            print(f"监控EC2实例数量: {instance_count}")
        
        # 模拟发送到监控系统
        print(f"\n✅ 数据已准备好发送到监控平台")
        print(f"数据大小: {len(json.dumps(monitoring_data))} 字符")
        
    except Exception as e:
        print(f"获取监控数据时出现错误: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS FinOps API 测试客户端')
    parser.add_argument('--url', default='http://localhost:8000', help='API服务器URL')
    parser.add_argument('--demo', action='store_true', help='运行API演示')
    parser.add_argument('--monitor', action='store_true', help='运行监控集成示例')
    
    args = parser.parse_args()
    
    # 更新客户端URL
    if args.url != 'http://localhost:8000':
        FinOpsAPIClient.__init__ = lambda self, base_url=args.url: setattr(self, 'base_url', base_url.rstrip('/')) or setattr(self, 'session', requests.Session())
    
    if args.demo:
        demo_api_calls()
    elif args.monitor:
        monitor_costs_example()
    else:
        print("请使用 --demo 或 --monitor 参数运行示例")
        print("使用 --help 查看更多选项")

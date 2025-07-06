#!/usr/bin/env python3
"""
AWS Cost Explorer API 客户端
用于获取成本和使用情况数据
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class CostExplorerClient:
    def __init__(self, region_name: str = 'us-east-1'):
        """
        初始化Cost Explorer客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.client = boto3.client('ce', region_name=region_name)
        self.logger = logging.getLogger(__name__)
    
    def get_daily_costs(self, days: int = 30, granularity: str = 'DAILY') -> Dict:
        """
        获取每日成本数据
        
        Args:
            days: 获取过去多少天的数据
            granularity: 数据粒度 (DAILY, MONTHLY)
            
        Returns:
            成本数据字典
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity=granularity,
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            return self._format_cost_response(response)
            
        except Exception as e:
            self.logger.error(f"获取每日成本数据失败: {str(e)}")
            raise
    
    def get_cost_by_service(self, days: int = 30) -> Dict:
        """
        获取按服务分组的成本数据
        
        Args:
            days: 获取过去多少天的数据
            
        Returns:
            按服务分组的成本数据
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            return self._format_service_costs(response)
            
        except Exception as e:
            self.logger.error(f"获取服务成本数据失败: {str(e)}")
            raise
    
    def get_cost_by_tags(self, tag_key: str, days: int = 30) -> Dict:
        """
        获取按标签分组的成本数据
        
        Args:
            tag_key: 标签键名
            days: 获取过去多少天的数据
            
        Returns:
            按标签分组的成本数据
        """
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {
                        'Type': 'TAG',
                        'Key': tag_key
                    }
                ]
            )
            
            return self._format_tag_costs(response, tag_key)
            
        except Exception as e:
            self.logger.error(f"获取标签成本数据失败: {str(e)}")
            raise
    
    def get_cost_forecast(self, days: int = 30) -> Dict:
        """
        获取成本预测数据
        
        Args:
            days: 预测未来多少天
            
        Returns:
            成本预测数据
        """
        try:
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=days)
            
            response = self.client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Metric='BLENDED_COST',
                Granularity='DAILY'
            )
            
            return self._format_forecast_response(response)
            
        except Exception as e:
            self.logger.error(f"获取成本预测数据失败: {str(e)}")
            raise
    
    def _format_cost_response(self, response: Dict) -> Dict:
        """格式化成本响应数据"""
        formatted_data = {
            'time_period': {
                'start': response.get('ResultsByTime', [{}])[0].get('TimePeriod', {}).get('Start'),
                'end': response.get('ResultsByTime', [{}])[-1].get('TimePeriod', {}).get('End') if response.get('ResultsByTime') else None
            },
            'daily_costs': [],
            'total_cost': 0.0
        }
        
        for result in response.get('ResultsByTime', []):
            daily_data = {
                'date': result.get('TimePeriod', {}).get('Start'),
                'services': [],
                'total': 0.0
            }
            
            for group in result.get('Groups', []):
                service_name = group.get('Keys', ['Unknown'])[0]
                cost = float(group.get('Metrics', {}).get('BlendedCost', {}).get('Amount', 0))
                
                daily_data['services'].append({
                    'service': service_name,
                    'cost': cost
                })
                daily_data['total'] += cost
            
            formatted_data['daily_costs'].append(daily_data)
            formatted_data['total_cost'] += daily_data['total']
        
        return formatted_data
    
    def _format_service_costs(self, response: Dict) -> Dict:
        """格式化服务成本数据"""
        service_costs = {}
        total_cost = 0.0
        
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service_name = group.get('Keys', ['Unknown'])[0]
                cost = float(group.get('Metrics', {}).get('BlendedCost', {}).get('Amount', 0))
                
                if service_name not in service_costs:
                    service_costs[service_name] = 0.0
                
                service_costs[service_name] += cost
                total_cost += cost
        
        # 按成本排序
        sorted_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'services': [{'name': name, 'cost': cost} for name, cost in sorted_services],
            'total_cost': total_cost
        }
    
    def _format_tag_costs(self, response: Dict, tag_key: str) -> Dict:
        """格式化标签成本数据"""
        tag_costs = {}
        total_cost = 0.0
        
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                tag_value = group.get('Keys', ['Untagged'])[0]
                cost = float(group.get('Metrics', {}).get('BlendedCost', {}).get('Amount', 0))
                
                if tag_value not in tag_costs:
                    tag_costs[tag_value] = 0.0
                
                tag_costs[tag_value] += cost
                total_cost += cost
        
        return {
            'tag_key': tag_key,
            'tag_costs': [{'tag_value': value, 'cost': cost} for value, cost in tag_costs.items()],
            'total_cost': total_cost
        }
    
    def _format_forecast_response(self, response: Dict) -> Dict:
        """格式化预测响应数据"""
        return {
            'forecast_period': {
                'start': response.get('TimePeriod', {}).get('Start'),
                'end': response.get('TimePeriod', {}).get('End')
            },
            'total_forecast': float(response.get('Total', {}).get('Amount', 0)),
            'forecast_results': [
                {
                    'date': result.get('TimePeriod', {}).get('Start'),
                    'mean_value': float(result.get('MeanValue', 0)),
                    'prediction_interval_lower': float(result.get('PredictionIntervalLowerBound', 0)),
                    'prediction_interval_upper': float(result.get('PredictionIntervalUpperBound', 0))
                }
                for result in response.get('ForecastResultsByTime', [])
            ]
        }


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 初始化客户端
    cost_client = CostExplorerClient()
    
    try:
        # 获取过去30天的每日成本
        print("=== 获取每日成本数据 ===")
        daily_costs = cost_client.get_daily_costs(days=7)
        print(json.dumps(daily_costs, indent=2, ensure_ascii=False))
        
        # 获取按服务分组的成本
        print("\n=== 获取服务成本数据 ===")
        service_costs = cost_client.get_cost_by_service(days=30)
        print(json.dumps(service_costs, indent=2, ensure_ascii=False))
        
        # 获取成本预测
        print("\n=== 获取成本预测数据 ===")
        forecast = cost_client.get_cost_forecast(days=7)
        print(json.dumps(forecast, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

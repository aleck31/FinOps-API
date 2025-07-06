#!/usr/bin/env python3
"""
AWS Budgets API 客户端
用于获取预算和成本控制数据
"""

import boto3
from datetime import datetime
from typing import Dict, List, Optional
import logging

class BudgetsClient:
    def __init__(self, region_name: str = 'us-east-1'):
        """
        初始化Budgets客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.client = boto3.client('budgets', region_name=region_name)
        self.account_id = boto3.client('sts').get_caller_identity()['Account']
        self.logger = logging.getLogger(__name__)
    
    def get_all_budgets(self) -> Dict:
        """
        获取所有预算信息
        
        Returns:
            所有预算的信息
        """
        try:
            response = self.client.describe_budgets(
                AccountId=self.account_id
            )
            
            budgets_data = []
            
            for budget in response.get('Budgets', []):
                budget_info = self._format_budget_info(budget)
                
                # 获取预算的实际支出
                try:
                    actual_spend = self.get_budget_performance(budget['BudgetName'])
                    budget_info.update(actual_spend)
                except Exception as e:
                    self.logger.warning(f"获取预算 {budget['BudgetName']} 的实际支出失败: {str(e)}")
                
                budgets_data.append(budget_info)
            
            return {
                'account_id': self.account_id,
                'budgets_count': len(budgets_data),
                'budgets': budgets_data
            }
            
        except Exception as e:
            self.logger.error(f"获取预算信息失败: {str(e)}")
            raise
    
    def get_budget_details(self, budget_name: str) -> Dict:
        """
        获取特定预算的详细信息
        
        Args:
            budget_name: 预算名称
            
        Returns:
            预算详细信息
        """
        try:
            response = self.client.describe_budget(
                AccountId=self.account_id,
                BudgetName=budget_name
            )
            
            budget = response['Budget']
            budget_info = self._format_budget_info(budget)
            
            # 获取预算性能数据
            performance = self.get_budget_performance(budget_name)
            budget_info.update(performance)
            
            # 获取预算历史
            history = self.get_budget_history(budget_name)
            budget_info['history'] = history
            
            return budget_info
            
        except Exception as e:
            self.logger.error(f"获取预算详细信息失败: {str(e)}")
            raise
    
    def get_budget_performance(self, budget_name: str) -> Dict:
        """
        获取预算执行情况
        
        Args:
            budget_name: 预算名称
            
        Returns:
            预算执行情况数据
        """
        try:
            response = self.client.describe_budget_performance_history(
                AccountId=self.account_id,
                BudgetName=budget_name,
                MaxResults=10
            )
            
            performance_data = {
                'actual_spend': 0.0,
                'forecasted_spend': 0.0,
                'percentage_used': 0.0,
                'status': 'UNKNOWN'
            }
            
            if response.get('BudgetPerformanceHistory'):
                latest_performance = response['BudgetPerformanceHistory'][0]
                
                actual_spend = latest_performance.get('ActualCost', {}).get('Amount', '0')
                forecasted_spend = latest_performance.get('ForecastedCost', {}).get('Amount', '0')
                budgeted_amount = latest_performance.get('BudgetedAndActualAmounts', {}).get('BudgetedAmount', {}).get('Amount', '0')
                
                performance_data['actual_spend'] = float(actual_spend)
                performance_data['forecasted_spend'] = float(forecasted_spend)
                
                if float(budgeted_amount) > 0:
                    performance_data['percentage_used'] = (float(actual_spend) / float(budgeted_amount)) * 100
                    
                    if performance_data['percentage_used'] >= 100:
                        performance_data['status'] = 'EXCEEDED'
                    elif performance_data['percentage_used'] >= 80:
                        performance_data['status'] = 'WARNING'
                    else:
                        performance_data['status'] = 'OK'
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"获取预算执行情况失败: {str(e)}")
            return {
                'actual_spend': 0.0,
                'forecasted_spend': 0.0,
                'percentage_used': 0.0,
                'status': 'ERROR'
            }
    
    def get_budget_history(self, budget_name: str, max_results: int = 30) -> List[Dict]:
        """
        获取预算历史数据
        
        Args:
            budget_name: 预算名称
            max_results: 最大返回结果数
            
        Returns:
            预算历史数据列表
        """
        try:
            response = self.client.describe_budget_performance_history(
                AccountId=self.account_id,
                BudgetName=budget_name,
                MaxResults=max_results
            )
            
            history_data = []
            
            for performance in response.get('BudgetPerformanceHistory', []):
                history_item = {
                    'time_period': {
                        'start': performance.get('TimePeriod', {}).get('Start'),
                        'end': performance.get('TimePeriod', {}).get('End')
                    },
                    'budgeted_amount': float(performance.get('BudgetedAndActualAmounts', {}).get('BudgetedAmount', {}).get('Amount', 0)),
                    'actual_cost': float(performance.get('ActualCost', {}).get('Amount', 0)),
                    'forecasted_cost': float(performance.get('ForecastedCost', {}).get('Amount', 0))
                }
                
                history_data.append(history_item)
            
            return sorted(history_data, key=lambda x: x['time_period']['start'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"获取预算历史数据失败: {str(e)}")
            return []
    
    def get_budget_notifications(self, budget_name: str) -> List[Dict]:
        """
        获取预算通知设置
        
        Args:
            budget_name: 预算名称
            
        Returns:
            预算通知设置列表
        """
        try:
            response = self.client.describe_notifications_for_budget(
                AccountId=self.account_id,
                BudgetName=budget_name
            )
            
            notifications = []
            
            for notification in response.get('Notifications', []):
                notification_info = {
                    'notification_type': notification.get('NotificationType'),
                    'comparison_operator': notification.get('ComparisonOperator'),
                    'threshold': notification.get('Threshold'),
                    'threshold_type': notification.get('ThresholdType'),
                    'notification_state': notification.get('NotificationState')
                }
                
                notifications.append(notification_info)
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"获取预算通知设置失败: {str(e)}")
            return []
    
    def _format_budget_info(self, budget: Dict) -> Dict:
        """
        格式化预算信息
        
        Args:
            budget: 原始预算数据
            
        Returns:
            格式化后的预算信息
        """
        return {
            'budget_name': budget.get('BudgetName'),
            'budget_type': budget.get('BudgetType'),
            'time_unit': budget.get('TimeUnit'),
            'time_period': {
                'start': budget.get('TimePeriod', {}).get('Start'),
                'end': budget.get('TimePeriod', {}).get('End')
            },
            'budgeted_amount': float(budget.get('BudgetLimit', {}).get('Amount', 0)),
            'currency': budget.get('BudgetLimit', {}).get('Unit', 'USD'),
            'cost_filters': budget.get('CostFilters', {}),
            'include_credits': budget.get('IncludeCredit', False),
            'include_discounts': budget.get('IncludeDiscount', False),
            'include_other_subscription': budget.get('IncludeOtherSubscription', False),
            'include_recurring': budget.get('IncludeRecurring', False),
            'include_refunds': budget.get('IncludeRefund', False),
            'include_subscriptions': budget.get('IncludeSubscription', False),
            'include_support': budget.get('IncludeSupport', False),
            'include_tax': budget.get('IncludeTax', False),
            'include_upfront': budget.get('IncludeUpfront', False),
            'use_amortized': budget.get('UseAmortized', False),
            'use_blended': budget.get('UseBlended', False)
        }


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 初始化客户端
    budgets_client = BudgetsClient()
    
    try:
        # 获取所有预算
        print("=== 获取所有预算 ===")
        budgets = budgets_client.get_all_budgets()
        print(f"找到 {budgets['budgets_count']} 个预算")
        
        for budget in budgets['budgets']:
            print(f"预算名称: {budget['budget_name']}")
            print(f"预算金额: {budget['budgeted_amount']} {budget['currency']}")
            print(f"实际支出: {budget.get('actual_spend', 0)}")
            print(f"使用百分比: {budget.get('percentage_used', 0):.2f}%")
            print(f"状态: {budget.get('status', 'UNKNOWN')}")
            print("-" * 50)
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

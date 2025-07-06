#!/usr/bin/env python3
"""
AWS优化建议客户端
用于获取AWS Trusted Advisor和Compute Optimizer的优化建议
"""

import boto3
from typing import Dict, List, Optional
import logging

class OptimizationClient:
    def __init__(self, region_name: str = 'us-east-1'):
        """
        初始化优化建议客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.support_client = boto3.client('support', region_name='us-east-1')  # Support API只在us-east-1可用
        self.compute_optimizer_client = boto3.client('compute-optimizer', region_name=region_name)
        self.ce_client = boto3.client('ce', region_name=region_name)
        self.logger = logging.getLogger(__name__)
    
    def get_trusted_advisor_checks(self) -> Dict:
        """获取Trusted Advisor检查结果"""
        try:
            # 获取所有可用的检查
            response = self.support_client.describe_trusted_advisor_checks(language='en')
            
            checks_summary = {
                'total_checks': len(response['checks']),
                'cost_optimization_checks': [],
                'performance_checks': [],
                'security_checks': [],
                'fault_tolerance_checks': []
            }
            
            # 分类检查项
            for check in response['checks']:
                check_info = {
                    'id': check['id'],
                    'name': check['name'],
                    'description': check['description'],
                    'category': check['category']
                }
                
                category = check['category'].lower()
                if 'cost' in category:
                    checks_summary['cost_optimization_checks'].append(check_info)
                elif 'performance' in category:
                    checks_summary['performance_checks'].append(check_info)
                elif 'security' in category:
                    checks_summary['security_checks'].append(check_info)
                elif 'fault' in category:
                    checks_summary['fault_tolerance_checks'].append(check_info)
            
            return checks_summary
            
        except Exception as e:
            self.logger.error(f"获取Trusted Advisor检查失败: {str(e)}")
            # 如果没有Support API权限，返回模拟数据
            return {
                'total_checks': 0,
                'cost_optimization_checks': [],
                'performance_checks': [],
                'security_checks': [],
                'fault_tolerance_checks': [],
                'error': 'Trusted Advisor需要Business或Enterprise支持计划'
            }
    
    def get_compute_optimizer_recommendations(self) -> Dict:
        """获取Compute Optimizer建议"""
        try:
            recommendations = {
                'ec2_recommendations': [],
                'ebs_recommendations': [],
                'lambda_recommendations': [],
                'summary': {
                    'total_recommendations': 0,
                    'potential_monthly_savings': 0.0
                }
            }
            
            # 获取EC2实例建议
            try:
                ec2_response = self.compute_optimizer_client.get_ec2_instance_recommendations()
                recommendations['ec2_recommendations'] = self._format_ec2_recommendations(
                    ec2_response.get('instanceRecommendations', [])
                )
            except Exception as e:
                self.logger.warning(f"获取EC2建议失败: {str(e)}")
            
            # 获取EBS卷建议
            try:
                ebs_response = self.compute_optimizer_client.get_ebs_volume_recommendations()
                recommendations['ebs_recommendations'] = self._format_ebs_recommendations(
                    ebs_response.get('volumeRecommendations', [])
                )
            except Exception as e:
                self.logger.warning(f"获取EBS建议失败: {str(e)}")
            
            # 获取Lambda函数建议
            try:
                lambda_response = self.compute_optimizer_client.get_lambda_function_recommendations()
                recommendations['lambda_recommendations'] = self._format_lambda_recommendations(
                    lambda_response.get('functionRecommendations', [])
                )
            except Exception as e:
                self.logger.warning(f"获取Lambda建议失败: {str(e)}")
            
            # 计算汇总信息
            total_recs = (len(recommendations['ec2_recommendations']) + 
                         len(recommendations['ebs_recommendations']) + 
                         len(recommendations['lambda_recommendations']))
            recommendations['summary']['total_recommendations'] = total_recs
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"获取Compute Optimizer建议失败: {str(e)}")
            return {
                'ec2_recommendations': [],
                'ebs_recommendations': [],
                'lambda_recommendations': [],
                'summary': {
                    'total_recommendations': 0,
                    'potential_monthly_savings': 0.0
                },
                'error': str(e)
            }
    
    def get_reserved_instance_recommendations(self) -> Dict:
        """获取预留实例建议"""
        try:
            response = self.ce_client.get_reservation_purchase_recommendation(
                Service='Amazon Elastic Compute Cloud - Compute'
            )
            
            recommendations = []
            for recommendation in response.get('Recommendations', []):
                rec_info = {
                    'instance_family': recommendation.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('Family'),
                    'instance_type': recommendation.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('InstanceType'),
                    'region': recommendation.get('InstanceDetails', {}).get('EC2InstanceDetails', {}).get('Region'),
                    'recommended_quantity': recommendation.get('RecommendationDetails', {}).get('RecommendedNumberOfInstancesToPurchase'),
                    'estimated_monthly_savings': float(recommendation.get('RecommendationDetails', {}).get('EstimatedMonthlySavingsAmount', 0)),
                    'estimated_monthly_on_demand_cost': float(recommendation.get('RecommendationDetails', {}).get('EstimatedMonthlyOnDemandCost', 0)),
                    'upfront_cost': float(recommendation.get('RecommendationDetails', {}).get('UpfrontCost', 0))
                }
                recommendations.append(rec_info)
            
            total_savings = sum(rec.get('estimated_monthly_savings', 0) for rec in recommendations)
            
            return {
                'recommendations': recommendations,
                'summary': {
                    'total_recommendations': len(recommendations),
                    'total_estimated_monthly_savings': total_savings
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取预留实例建议失败: {str(e)}")
            return {
                'recommendations': [],
                'summary': {
                    'total_recommendations': 0,
                    'total_estimated_monthly_savings': 0.0
                },
                'error': str(e)
            }
    
    def get_savings_plans_recommendations(self) -> Dict:
        """获取节省计划建议"""
        try:
            response = self.ce_client.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT'
            )
            
            recommendations = []
            for recommendation in response.get('SavingsPlansRecommendations', []):
                rec_info = {
                    'savings_plans_type': recommendation.get('SavingsPlansType'),
                    'term_in_years': recommendation.get('TermInYears'),
                    'payment_option': recommendation.get('PaymentOption'),
                    'hourly_commitment': float(recommendation.get('HourlyCommitment', 0)),
                    'estimated_monthly_savings': float(recommendation.get('EstimatedMonthlySavings', 0)),
                    'estimated_on_demand_cost': float(recommendation.get('EstimatedOnDemandCost', 0)),
                    'estimated_sp_cost': float(recommendation.get('EstimatedSPCost', 0))
                }
                recommendations.append(rec_info)
            
            total_savings = sum(rec.get('estimated_monthly_savings', 0) for rec in recommendations)
            
            return {
                'recommendations': recommendations,
                'summary': {
                    'total_recommendations': len(recommendations),
                    'total_estimated_monthly_savings': total_savings
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取节省计划建议失败: {str(e)}")
            return {
                'recommendations': [],
                'summary': {
                    'total_recommendations': 0,
                    'total_estimated_monthly_savings': 0.0
                },
                'error': str(e)
            }
    
    def _format_ec2_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """格式化EC2建议"""
        formatted = []
        for rec in recommendations:
            formatted_rec = {
                'instance_arn': rec.get('instanceArn'),
                'current_instance_type': rec.get('currentInstanceType'),
                'finding': rec.get('finding'),
                'utilization_metrics': rec.get('utilizationMetrics', {}),
                'recommendation_options': []
            }
            
            for option in rec.get('recommendationOptions', []):
                option_info = {
                    'instance_type': option.get('instanceType'),
                    'projected_utilization_metrics': option.get('projectedUtilizationMetrics', {}),
                    'performance_risk': option.get('performanceRisk')
                }
                formatted_rec['recommendation_options'].append(option_info)
            
            formatted.append(formatted_rec)
        
        return formatted
    
    def _format_ebs_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """格式化EBS建议"""
        formatted = []
        for rec in recommendations:
            formatted_rec = {
                'volume_arn': rec.get('volumeArn'),
                'current_configuration': rec.get('currentConfiguration', {}),
                'finding': rec.get('finding'),
                'utilization_metrics': rec.get('utilizationMetrics', {}),
                'recommendation_options': rec.get('volumeRecommendationOptions', [])
            }
            formatted.append(formatted_rec)
        
        return formatted
    
    def _format_lambda_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """格式化Lambda建议"""
        formatted = []
        for rec in recommendations:
            formatted_rec = {
                'function_arn': rec.get('functionArn'),
                'function_version': rec.get('functionVersion'),
                'current_memory_size': rec.get('currentMemorySize'),
                'finding': rec.get('finding'),
                'utilization_metrics': rec.get('utilizationMetrics', {}),
                'memory_size_recommendation_options': rec.get('memorySizeRecommendationOptions', [])
            }
            formatted.append(formatted_rec)
        
        return formatted


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    client = OptimizationClient()
    
    try:
        print("=== Trusted Advisor检查 ===")
        ta_checks = client.get_trusted_advisor_checks()
        print(f"总检查项: {ta_checks['total_checks']}")
        
        print("\n=== Compute Optimizer建议 ===")
        co_recommendations = client.get_compute_optimizer_recommendations()
        print(f"总建议数: {co_recommendations['summary']['total_recommendations']}")
        
        print("\n=== 预留实例建议 ===")
        ri_recommendations = client.get_reserved_instance_recommendations()
        print(f"总建议数: {ri_recommendations['summary']['total_recommendations']}")
        
        print("\n=== 节省计划建议 ===")
        sp_recommendations = client.get_savings_plans_recommendations()
        print(f"总建议数: {sp_recommendations['summary']['total_recommendations']}")
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

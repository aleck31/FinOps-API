#!/usr/bin/env python3
"""
AWS CloudWatch API 客户端
用于获取资源监控指标数据
"""

import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

class CloudWatchClient:
    def __init__(self, region_name: str = 'us-east-1'):
        """
        初始化CloudWatch客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.client = boto3.client('cloudwatch', region_name=region_name)
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.rds_client = boto3.client('rds', region_name=region_name)
        self.lambda_client = boto3.client('lambda', region_name=region_name)
        self.logger = logging.getLogger(__name__)
    
    def get_ec2_metrics(self, instance_id: Optional[str] = None, 
                       metric_name: str = 'CPUUtilization', 
                       hours: int = 24) -> Dict:
        """
        获取EC2实例指标
        
        Args:
            instance_id: EC2实例ID，如果为None则获取所有实例
            metric_name: 指标名称
            hours: 获取过去多少小时的数据
            
        Returns:
            EC2指标数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            if instance_id:
                instances = [{'InstanceId': instance_id}]
            else:
                # 获取所有运行中的实例
                response = self.ec2_client.describe_instances(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
                )
                instances = []
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        instances.append({'InstanceId': instance['InstanceId']})
            
            metrics_data = []
            
            for instance in instances:
                instance_id = instance['InstanceId']
                
                response = self.client.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=[
                        {
                            'Name': 'InstanceId',
                            'Value': instance_id
                        }
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1小时间隔
                    Statistics=['Average', 'Maximum']
                )
                
                datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
                
                metrics_data.append({
                    'instance_id': instance_id,
                    'metric_name': metric_name,
                    'datapoints': [
                        {
                            'timestamp': dp['Timestamp'].isoformat(),
                            'average': dp['Average'],
                            'maximum': dp['Maximum'],
                            'unit': dp['Unit']
                        }
                        for dp in datapoints
                    ]
                })
            
            return {
                'metric_name': metric_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'instances': metrics_data
            }
            
        except Exception as e:
            self.logger.error(f"获取EC2指标失败: {str(e)}")
            raise
    
    def get_rds_metrics(self, db_instance_identifier: str, 
                       metric_name: str = 'CPUUtilization', 
                       hours: int = 24) -> Dict:
        """
        获取RDS实例指标
        
        Args:
            db_instance_identifier: RDS实例标识符
            metric_name: 指标名称
            hours: 获取过去多少小时的数据
            
        Returns:
            RDS指标数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            response = self.client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': db_instance_identifier
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1小时间隔
                Statistics=['Average', 'Maximum']
            )
            
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            
            return {
                'db_instance_identifier': db_instance_identifier,
                'metric_name': metric_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'datapoints': [
                    {
                        'timestamp': dp['Timestamp'].isoformat(),
                        'average': dp['Average'],
                        'maximum': dp['Maximum'],
                        'unit': dp['Unit']
                    }
                    for dp in datapoints
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取RDS指标失败: {str(e)}")
            raise
    
    def get_lambda_metrics(self, function_name: str, 
                          metric_name: str = 'Invocations', 
                          hours: int = 24) -> Dict:
        """
        获取Lambda函数指标
        
        Args:
            function_name: Lambda函数名称
            metric_name: 指标名称
            hours: 获取过去多少小时的数据
            
        Returns:
            Lambda指标数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            response = self.client.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'FunctionName',
                        'Value': function_name
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1小时间隔
                Statistics=['Sum', 'Average'] if metric_name == 'Invocations' else ['Average', 'Maximum']
            )
            
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            
            return {
                'function_name': function_name,
                'metric_name': metric_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'datapoints': [
                    {
                        'timestamp': dp['Timestamp'].isoformat(),
                        'value': dp.get('Sum', dp.get('Average', 0)),
                        'unit': dp['Unit']
                    }
                    for dp in datapoints
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取Lambda指标失败: {str(e)}")
            raise
    
    def get_s3_metrics(self, bucket_name: str, 
                      metric_name: str = 'BucketSizeBytes', 
                      days: int = 7) -> Dict:
        """
        获取S3存储桶指标
        
        Args:
            bucket_name: S3存储桶名称
            metric_name: 指标名称
            days: 获取过去多少天的数据
            
        Returns:
            S3指标数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            response = self.client.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'BucketName',
                        'Value': bucket_name
                    },
                    {
                        'Name': 'StorageType',
                        'Value': 'StandardStorage'
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1天间隔
                Statistics=['Average']
            )
            
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            
            return {
                'bucket_name': bucket_name,
                'metric_name': metric_name,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'datapoints': [
                    {
                        'timestamp': dp['Timestamp'].isoformat(),
                        'value': dp['Average'],
                        'unit': dp['Unit']
                    }
                    for dp in datapoints
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取S3指标失败: {str(e)}")
            raise
    
    def get_custom_metrics(self, namespace: str, metric_name: str, 
                          dimensions: List[Dict], hours: int = 24) -> Dict:
        """
        获取自定义指标
        
        Args:
            namespace: 指标命名空间
            metric_name: 指标名称
            dimensions: 指标维度
            hours: 获取过去多少小时的数据
            
        Returns:
            自定义指标数据
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            response = self.client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1小时间隔
                Statistics=['Average', 'Sum', 'Maximum']
            )
            
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'])
            
            return {
                'namespace': namespace,
                'metric_name': metric_name,
                'dimensions': dimensions,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'datapoints': [
                    {
                        'timestamp': dp['Timestamp'].isoformat(),
                        'average': dp.get('Average'),
                        'sum': dp.get('Sum'),
                        'maximum': dp.get('Maximum'),
                        'unit': dp['Unit']
                    }
                    for dp in datapoints
                ]
            }
            
        except Exception as e:
            self.logger.error(f"获取自定义指标失败: {str(e)}")
            raise


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 初始化客户端
    cw_client = CloudWatchClient()
    
    try:
        # 获取EC2指标
        print("=== 获取EC2指标 ===")
        ec2_metrics = cw_client.get_ec2_metrics(hours=24)
        print(f"获取到 {len(ec2_metrics['instances'])} 个实例的指标数据")
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

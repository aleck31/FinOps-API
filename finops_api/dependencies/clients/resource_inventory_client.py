#!/usr/bin/env python3
"""
AWS资源清单客户端
用于获取AWS资源清单和配置信息
"""

import boto3
from typing import Dict, List, Optional
import logging

class ResourceInventoryClient:
    def __init__(self, region_name: str = 'us-east-1'):
        """
        初始化资源清单客户端
        
        Args:
            region_name: AWS区域名称
        """
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        self.rds_client = boto3.client('rds', region_name=region_name)
        self.s3_client = boto3.client('s3')
        self.lambda_client = boto3.client('lambda', region_name=region_name)
        self.logger = logging.getLogger(__name__)
    
    def get_ec2_inventory(self) -> Dict:
        """获取EC2实例清单"""
        try:
            response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = {
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'vpc_id': instance.get('VpcId'),
                        'subnet_id': instance.get('SubnetId'),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'public_ip': instance.get('PublicIpAddress'),
                        'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    }
                    instances.append(instance_info)
            
            return {
                'total_instances': len(instances),
                'instances': instances,
                'summary': self._get_ec2_summary(instances)
            }
            
        except Exception as e:
            self.logger.error(f"获取EC2清单失败: {str(e)}")
            raise
    
    def get_rds_inventory(self) -> Dict:
        """获取RDS实例清单"""
        try:
            response = self.rds_client.describe_db_instances()
            
            instances = []
            for db_instance in response['DBInstances']:
                instance_info = {
                    'db_instance_identifier': db_instance['DBInstanceIdentifier'],
                    'db_instance_class': db_instance['DBInstanceClass'],
                    'engine': db_instance['Engine'],
                    'engine_version': db_instance['EngineVersion'],
                    'db_instance_status': db_instance['DBInstanceStatus'],
                    'allocated_storage': db_instance['AllocatedStorage'],
                    'storage_type': db_instance['StorageType'],
                    'multi_az': db_instance['MultiAZ'],
                    'availability_zone': db_instance.get('AvailabilityZone'),
                    'vpc_security_groups': [sg['VpcSecurityGroupId'] for sg in db_instance.get('VpcSecurityGroups', [])],
                    'backup_retention_period': db_instance['BackupRetentionPeriod'],
                    'instance_create_time': db_instance['InstanceCreateTime'].isoformat()
                }
                instances.append(instance_info)
            
            return {
                'total_instances': len(instances),
                'instances': instances,
                'summary': self._get_rds_summary(instances)
            }
            
        except Exception as e:
            self.logger.error(f"获取RDS清单失败: {str(e)}")
            raise
    
    def get_s3_inventory(self) -> Dict:
        """获取S3存储桶清单"""
        try:
            response = self.s3_client.list_buckets()
            
            buckets = []
            for bucket in response['Buckets']:
                bucket_name = bucket['Name']
                
                # 获取存储桶详细信息
                try:
                    location = self.s3_client.get_bucket_location(Bucket=bucket_name)
                    region = location['LocationConstraint'] or 'us-east-1'
                    
                    # 获取存储桶大小（简化版本）
                    bucket_info = {
                        'bucket_name': bucket_name,
                        'creation_date': bucket['CreationDate'].isoformat(),
                        'region': region
                    }
                    buckets.append(bucket_info)
                    
                except Exception as e:
                    self.logger.warning(f"获取存储桶 {bucket_name} 详细信息失败: {str(e)}")
                    buckets.append({
                        'bucket_name': bucket_name,
                        'creation_date': bucket['CreationDate'].isoformat(),
                        'region': 'unknown'
                    })
            
            return {
                'total_buckets': len(buckets),
                'buckets': buckets
            }
            
        except Exception as e:
            self.logger.error(f"获取S3清单失败: {str(e)}")
            raise
    
    def get_lambda_inventory(self) -> Dict:
        """获取Lambda函数清单"""
        try:
            response = self.lambda_client.list_functions()
            
            functions = []
            for function in response['Functions']:
                function_info = {
                    'function_name': function['FunctionName'],
                    'runtime': function['Runtime'],
                    'handler': function['Handler'],
                    'code_size': function['CodeSize'],
                    'description': function.get('Description', ''),
                    'timeout': function['Timeout'],
                    'memory_size': function['MemorySize'],
                    'last_modified': function['LastModified'],
                    'role': function['Role']
                }
                functions.append(function_info)
            
            return {
                'total_functions': len(functions),
                'functions': functions,
                'summary': self._get_lambda_summary(functions)
            }
            
        except Exception as e:
            self.logger.error(f"获取Lambda清单失败: {str(e)}")
            raise
    
    def _get_ec2_summary(self, instances: List[Dict]) -> Dict:
        """生成EC2实例汇总"""
        summary = {
            'by_state': {},
            'by_instance_type': {},
            'by_availability_zone': {}
        }
        
        for instance in instances:
            # 按状态统计
            state = instance['state']
            summary['by_state'][state] = summary['by_state'].get(state, 0) + 1
            
            # 按实例类型统计
            instance_type = instance['instance_type']
            summary['by_instance_type'][instance_type] = summary['by_instance_type'].get(instance_type, 0) + 1
            
            # 按可用区统计
            az = instance['availability_zone']
            summary['by_availability_zone'][az] = summary['by_availability_zone'].get(az, 0) + 1
        
        return summary
    
    def _get_rds_summary(self, instances: List[Dict]) -> Dict:
        """生成RDS实例汇总"""
        summary = {
            'by_engine': {},
            'by_instance_class': {},
            'by_status': {}
        }
        
        for instance in instances:
            # 按引擎统计
            engine = instance['engine']
            summary['by_engine'][engine] = summary['by_engine'].get(engine, 0) + 1
            
            # 按实例类型统计
            instance_class = instance['db_instance_class']
            summary['by_instance_class'][instance_class] = summary['by_instance_class'].get(instance_class, 0) + 1
            
            # 按状态统计
            status = instance['db_instance_status']
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
        
        return summary
    
    def _get_lambda_summary(self, functions: List[Dict]) -> Dict:
        """生成Lambda函数汇总"""
        summary = {
            'by_runtime': {},
            'total_code_size': 0,
            'average_memory_size': 0
        }
        
        total_memory = 0
        for function in functions:
            # 按运行时统计
            runtime = function['runtime']
            summary['by_runtime'][runtime] = summary['by_runtime'].get(runtime, 0) + 1
            
            # 代码大小统计
            summary['total_code_size'] += function['code_size']
            
            # 内存大小统计
            total_memory += function['memory_size']
        
        if functions:
            summary['average_memory_size'] = total_memory / len(functions)
        
        return summary


def main():
    """测试函数"""
    logging.basicConfig(level=logging.INFO)
    
    client = ResourceInventoryClient()
    
    try:
        print("=== EC2实例清单 ===")
        ec2_inventory = client.get_ec2_inventory()
        print(f"总实例数: {ec2_inventory['total_instances']}")
        
        print("\n=== RDS实例清单 ===")
        rds_inventory = client.get_rds_inventory()
        print(f"总实例数: {rds_inventory['total_instances']}")
        
        print("\n=== S3存储桶清单 ===")
        s3_inventory = client.get_s3_inventory()
        print(f"总存储桶数: {s3_inventory['total_buckets']}")
        
        print("\n=== Lambda函数清单 ===")
        lambda_inventory = client.get_lambda_inventory()
        print(f"总函数数: {lambda_inventory['total_functions']}")
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()

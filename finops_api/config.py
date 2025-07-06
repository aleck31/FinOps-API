#!/usr/bin/env python3
"""
配置文件
"""

import os
from typing import List, Dict

class Config:
    """应用配置类"""
    
    # AWS配置
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')
    
    # API配置
    API_TITLE = "AWS FinOps API"
    API_DESCRIPTION = "AWS财务运营数据API服务"
    API_VERSION = "1.0.0"
    
    # 服务器配置
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'finops_api.log')
    
    # 缓存配置
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))  # 5分钟
    
    # 限流配置
    RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # 60秒
    
    # 默认查询参数
    DEFAULT_DAYS = 30
    DEFAULT_HOURS = 24
    MAX_DAYS = 365
    MAX_HOURS = 168  # 7天
    
    # 支持的指标
    EC2_METRICS = [
        'CPUUtilization',
        'NetworkIn',
        'NetworkOut',
        'DiskReadOps',
        'DiskWriteOps',
        'DiskReadBytes',
        'DiskWriteBytes'
    ]
    
    RDS_METRICS = [
        'CPUUtilization',
        'DatabaseConnections',
        'FreeableMemory',
        'ReadIOPS',
        'WriteIOPS',
        'ReadLatency',
        'WriteLatency',
        'FreeStorageSpace'
    ]
    
    LAMBDA_METRICS = [
        'Invocations',
        'Duration',
        'Errors',
        'Throttles',
        'ConcurrentExecutions'
    ]
    
    S3_METRICS = [
        'BucketSizeBytes',
        'NumberOfObjects'
    ]
    
    # 成本维度
    COST_DIMENSIONS = [
        'SERVICE',
        'LINKED_ACCOUNT',
        'REGION',
        'AVAILABILITY_ZONE',
        'INSTANCE_TYPE',
        'USAGE_TYPE',
        'OPERATION',
        'PURCHASE_TYPE',
        'RESOURCE_ID',
        'PLATFORM',
        'TENANCY',
        'SCOPE',
        'LEGAL_ENTITY_NAME',
        'DEPLOYMENT_OPTION',
        'DATABASE_ENGINE',
        'CACHE_ENGINE',
        'INSTANCE_TYPE_FAMILY',
        'BILLING_ENTITY',
        'RESERVATION_ID',
        'SAVINGS_PLANS_TYPE',
        'SAVINGS_PLAN_ARN',
        'PAYMENT_OPTION',
        'AGREEMENT_END_DATE_TIME_AFTER',
        'AGREEMENT_END_DATE_TIME_BEFORE'
    ]
    
    @classmethod
    def get_aws_config(cls) -> Dict:
        """获取AWS配置"""
        return {
            'region_name': cls.AWS_REGION,
            'profile_name': cls.AWS_PROFILE if cls.AWS_PROFILE != 'default' else None
        }
    
    @classmethod
    def get_supported_metrics(cls, service: str) -> List[str]:
        """获取支持的指标列表"""
        service_metrics = {
            'ec2': cls.EC2_METRICS,
            'rds': cls.RDS_METRICS,
            'lambda': cls.LAMBDA_METRICS,
            's3': cls.S3_METRICS
        }
        return service_metrics.get(service.lower(), [])


# 环境特定配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'INFO'


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


# 根据环境变量选择配置
def get_config():
    """根据环境变量获取配置"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()


# 全局配置实例
config = get_config()

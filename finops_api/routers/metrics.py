"""
资源监控相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from models import APIResponse
from dependencies import get_cloudwatch_client
from dependencies.clients import CloudWatchClient

router = APIRouter(prefix="/api/v1/metrics", tags=["资源监控"])
logger = logging.getLogger(__name__)

@router.get("/ec2", response_model=APIResponse)
async def get_ec2_metrics(
    instance_id: Optional[str] = Query(default=None, description="EC2实例ID"),
    metric_name: str = Query(default="CPUUtilization", description="指标名称"),
    hours: int = Query(default=24, ge=1, le=168, description="获取过去多少小时的数据"),
    client: CloudWatchClient = Depends(get_cloudwatch_client)
):
    """获取EC2实例监控指标"""
    try:
        data = client.get_ec2_metrics(
            instance_id=instance_id,
            metric_name=metric_name,
            hours=hours
        )
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取EC2指标数据"
        )
    except Exception as e:
        logger.error(f"获取EC2指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rds", response_model=APIResponse)
async def get_rds_metrics(
    db_instance_identifier: str = Query(description="RDS实例标识符"),
    metric_name: str = Query(default="CPUUtilization", description="指标名称"),
    hours: int = Query(default=24, ge=1, le=168, description="获取过去多少小时的数据"),
    client: CloudWatchClient = Depends(get_cloudwatch_client)
):
    """获取RDS实例监控指标"""
    try:
        data = client.get_rds_metrics(
            db_instance_identifier=db_instance_identifier,
            metric_name=metric_name,
            hours=hours
        )
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取RDS指标数据"
        )
    except Exception as e:
        logger.error(f"获取RDS指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lambda", response_model=APIResponse)
async def get_lambda_metrics(
    function_name: str = Query(description="Lambda函数名称"),
    metric_name: str = Query(default="Invocations", description="指标名称"),
    hours: int = Query(default=24, ge=1, le=168, description="获取过去多少小时的数据"),
    client: CloudWatchClient = Depends(get_cloudwatch_client)
):
    """获取Lambda函数监控指标"""
    try:
        data = client.get_lambda_metrics(
            function_name=function_name,
            metric_name=metric_name,
            hours=hours
        )
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取Lambda指标数据"
        )
    except Exception as e:
        logger.error(f"获取Lambda指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

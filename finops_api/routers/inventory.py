"""
资源清单相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from models import APIResponse
from dependencies import get_inventory_client
from dependencies.clients import ResourceInventoryClient

router = APIRouter(prefix="/api/v1/inventory", tags=["资源清单"])
logger = logging.getLogger(__name__)

@router.get("/ec2", response_model=APIResponse)
async def get_ec2_inventory(
    client: ResourceInventoryClient = Depends(get_inventory_client)
):
    """获取EC2实例清单"""
    try:
        data = client.get_ec2_inventory()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取EC2实例清单"
        )
    except Exception as e:
        logger.error(f"获取EC2清单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rds", response_model=APIResponse)
async def get_rds_inventory(
    client: ResourceInventoryClient = Depends(get_inventory_client)
):
    """获取RDS实例清单"""
    try:
        data = client.get_rds_inventory()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取RDS实例清单"
        )
    except Exception as e:
        logger.error(f"获取RDS清单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/s3", response_model=APIResponse)
async def get_s3_inventory(
    client: ResourceInventoryClient = Depends(get_inventory_client)
):
    """获取S3存储桶清单"""
    try:
        data = client.get_s3_inventory()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取S3存储桶清单"
        )
    except Exception as e:
        logger.error(f"获取S3清单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lambda", response_model=APIResponse)
async def get_lambda_inventory(
    client: ResourceInventoryClient = Depends(get_inventory_client)
):
    """获取Lambda函数清单"""
    try:
        data = client.get_lambda_inventory()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取Lambda函数清单"
        )
    except Exception as e:
        logger.error(f"获取Lambda清单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

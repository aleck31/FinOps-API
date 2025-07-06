"""
成本管理相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from models import APIResponse
from dependencies import get_cost_client
from dependencies.clients import CostExplorerClient

router = APIRouter(prefix="/api/v1/costs", tags=["成本管理"])
logger = logging.getLogger(__name__)

@router.get("/daily", response_model=APIResponse)
async def get_daily_costs(
    days: int = Query(default=30, ge=1, le=365, description="获取过去多少天的数据"),
    granularity: str = Query(default="DAILY", description="数据粒度: DAILY 或 MONTHLY"),
    client: CostExplorerClient = Depends(get_cost_client)
):
    """获取每日成本数据"""
    try:
        data = client.get_daily_costs(days=days, granularity=granularity)
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取过去{days}天的成本数据"
        )
    except Exception as e:
        logger.error(f"获取每日成本数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-service", response_model=APIResponse)
async def get_costs_by_service(
    days: int = Query(default=30, ge=1, le=365, description="获取过去多少天的数据"),
    client: CostExplorerClient = Depends(get_cost_client)
):
    """获取按服务分组的成本数据"""
    try:
        data = client.get_cost_by_service(days=days)
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取过去{days}天按服务分组的成本数据"
        )
    except Exception as e:
        logger.error(f"获取服务成本数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-tags", response_model=APIResponse)
async def get_costs_by_tags(
    tag_key: str = Query(description="标签键名"),
    days: int = Query(default=30, ge=1, le=365, description="获取过去多少天的数据"),
    client: CostExplorerClient = Depends(get_cost_client)
):
    """获取按标签分组的成本数据"""
    try:
        data = client.get_cost_by_tags(tag_key=tag_key, days=days)
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取过去{days}天按标签'{tag_key}'分组的成本数据"
        )
    except Exception as e:
        logger.error(f"获取标签成本数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast", response_model=APIResponse)
async def get_cost_forecast(
    days: int = Query(default=30, ge=1, le=90, description="预测未来多少天"),
    client: CostExplorerClient = Depends(get_cost_client)
):
    """获取成本预测数据"""
    try:
        data = client.get_cost_forecast(days=days)
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取未来{days}天的成本预测"
        )
    except Exception as e:
        logger.error(f"获取成本预测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

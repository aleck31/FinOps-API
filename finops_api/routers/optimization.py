"""
优化建议相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from models import APIResponse
from dependencies import get_optimization_client
from dependencies.clients import OptimizationClient

router = APIRouter(prefix="/api/v1/optimization", tags=["优化建议"])
logger = logging.getLogger(__name__)

@router.get("/trusted-advisor", response_model=APIResponse)
async def get_trusted_advisor_checks(
    client: OptimizationClient = Depends(get_optimization_client)
):
    """获取Trusted Advisor检查结果"""
    try:
        data = client.get_trusted_advisor_checks()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取Trusted Advisor检查结果"
        )
    except Exception as e:
        logger.error(f"获取Trusted Advisor检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compute-optimizer", response_model=APIResponse)
async def get_compute_optimizer_recommendations(
    client: OptimizationClient = Depends(get_optimization_client)
):
    """获取Compute Optimizer建议"""
    try:
        data = client.get_compute_optimizer_recommendations()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取Compute Optimizer建议"
        )
    except Exception as e:
        logger.error(f"获取Compute Optimizer建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reserved-instances", response_model=APIResponse)
async def get_reserved_instance_recommendations(
    client: OptimizationClient = Depends(get_optimization_client)
):
    """获取预留实例建议"""
    try:
        data = client.get_reserved_instance_recommendations()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取预留实例建议"
        )
    except Exception as e:
        logger.error(f"获取预留实例建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/savings-plans", response_model=APIResponse)
async def get_savings_plans_recommendations(
    client: OptimizationClient = Depends(get_optimization_client)
):
    """获取节省计划建议"""
    try:
        data = client.get_savings_plans_recommendations()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取节省计划建议"
        )
    except Exception as e:
        logger.error(f"获取节省计划建议失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

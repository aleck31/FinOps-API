"""
预算监控相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException
import logging

from models import APIResponse
from dependencies import get_budgets_client
from dependencies.clients import BudgetsClient

router = APIRouter(prefix="/api/v1/budgets", tags=["预算监控"])
logger = logging.getLogger(__name__)

@router.get("", response_model=APIResponse)
async def get_budgets(
    client: BudgetsClient = Depends(get_budgets_client)
):
    """获取所有预算信息"""
    try:
        data = client.get_all_budgets()
        return APIResponse(
            success=True,
            data=data,
            message="成功获取预算信息"
        )
    except Exception as e:
        logger.error(f"获取预算信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{budget_name}", response_model=APIResponse)
async def get_budget_details(
    budget_name: str,
    client: BudgetsClient = Depends(get_budgets_client)
):
    """获取特定预算的详细信息"""
    try:
        data = client.get_budget_details(budget_name=budget_name)
        return APIResponse(
            success=True,
            data=data,
            message=f"成功获取预算'{budget_name}'的详细信息"
        )
    except Exception as e:
        logger.error(f"获取预算详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

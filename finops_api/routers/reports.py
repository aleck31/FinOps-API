"""
综合报告相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
import logging

from models import APIResponse
from dependencies import get_cost_client, get_budgets_client
from dependencies.clients import CostExplorerClient, BudgetsClient

router = APIRouter(prefix="/api/v1/reports", tags=["综合报告"])
logger = logging.getLogger(__name__)

@router.get("/cost-summary", response_model=APIResponse)
async def get_cost_summary(
    days: int = Query(default=30, ge=1, le=365, description="统计过去多少天的数据"),
    cost_client: CostExplorerClient = Depends(get_cost_client),
    budgets_client: BudgetsClient = Depends(get_budgets_client)
):
    """获取成本汇总报告"""
    try:
        # 获取成本数据
        daily_costs = cost_client.get_daily_costs(days=days)
        service_costs = cost_client.get_cost_by_service(days=days)
        cost_forecast = cost_client.get_cost_forecast(days=7)
        
        # 获取预算数据
        budgets_data = budgets_client.get_all_budgets()
        
        # 生成汇总报告
        summary = {
            "report_period": f"过去{days}天",
            "daily_costs": daily_costs,
            "service_costs": service_costs,
            "cost_forecast": cost_forecast,
            "budgets": budgets_data,
            "summary_metrics": {
                "total_cost": daily_costs.get("total_cost", 0),
                "average_daily_cost": daily_costs.get("total_cost", 0) / days if days > 0 else 0,
                "top_service": service_costs.get("services", [{}])[0].get("service", "N/A") if service_costs.get("services") else "N/A",
                "forecast_next_week": cost_forecast.get("total_forecast", 0),
                "active_budgets": len(budgets_data.get("budgets", []))
            }
        }
        
        return APIResponse(
            success=True,
            data=summary,
            message=f"成功生成过去{days}天的成本汇总报告"
        )
    except Exception as e:
        logger.error(f"获取成本汇总报告失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

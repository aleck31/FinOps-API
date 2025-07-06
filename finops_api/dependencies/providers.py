"""
客户端依赖注入
"""

from fastapi import HTTPException
from .clients import (
    CostExplorerClient,
    CloudWatchClient,
    BudgetsClient,
    ResourceInventoryClient,
    OptimizationClient
)

# 全局客户端实例
_cost_client = None
_cloudwatch_client = None
_budgets_client = None
_inventory_client = None
_optimization_client = None

def init_clients():
    """初始化所有客户端"""
    global _cost_client, _cloudwatch_client, _budgets_client, _inventory_client, _optimization_client
    
    _cost_client = CostExplorerClient()
    _cloudwatch_client = CloudWatchClient()
    _budgets_client = BudgetsClient()
    _inventory_client = ResourceInventoryClient()
    _optimization_client = OptimizationClient()

def get_cost_client() -> CostExplorerClient:
    if _cost_client is None:
        raise HTTPException(status_code=500, detail="Cost Explorer客户端未初始化")
    return _cost_client

def get_cloudwatch_client() -> CloudWatchClient:
    if _cloudwatch_client is None:
        raise HTTPException(status_code=500, detail="CloudWatch客户端未初始化")
    return _cloudwatch_client

def get_budgets_client() -> BudgetsClient:
    if _budgets_client is None:
        raise HTTPException(status_code=500, detail="Budgets客户端未初始化")
    return _budgets_client

def get_inventory_client() -> ResourceInventoryClient:
    if _inventory_client is None:
        raise HTTPException(status_code=500, detail="资源清单客户端未初始化")
    return _inventory_client

def get_optimization_client() -> OptimizationClient:
    if _optimization_client is None:
        raise HTTPException(status_code=500, detail="优化建议客户端未初始化")
    return _optimization_client

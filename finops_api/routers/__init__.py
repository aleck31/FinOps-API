"""
API路由模块
"""

from .costs import router as costs_router
from .budgets import router as budgets_router
from .metrics import router as metrics_router
from .inventory import router as inventory_router
from .optimization import router as optimization_router
from .reports import router as reports_router

__all__ = [
    "costs_router",
    "budgets_router", 
    "metrics_router",
    "inventory_router",
    "optimization_router",
    "reports_router"
]

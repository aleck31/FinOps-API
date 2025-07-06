"""
API响应模型
"""

from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class APIResponse(BaseModel):
    """统一的API响应格式"""
    success: bool
    data: Optional[Any] = None
    message: str = ""
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

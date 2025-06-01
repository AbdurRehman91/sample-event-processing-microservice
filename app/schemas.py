from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class EventCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    event_type: str = Field(..., min_length=1, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class EventResponse(BaseModel):
    message: str
    event_id: Optional[str] = None
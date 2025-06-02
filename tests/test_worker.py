import pytest
import pytest_asyncio
from app.worker import EventWorker
from datetime import datetime

@pytest.mark.asyncio
async def test_process_event():
    worker = EventWorker()
    
    event_data = {
        "user_id": "test123",
        "event_type": "test_event",
        "metadata": {"test": "data"},
        "timestamp": "2025-05-28T10:00:00Z"
    }
    
    result = await worker.process_event(event_data)
    assert result.user_id == "test123"
    assert result.event_type == "test_event"
    assert result.processed_at is not None

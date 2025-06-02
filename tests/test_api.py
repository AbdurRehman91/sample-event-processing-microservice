import logging
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from moto import mock_aws
import boto3
from app.main import app
from app.database import Base, engine
from datetime import datetime
import structlog


logger = structlog.get_logger()
@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    return TestClient(app)

@mock_aws
def test_create_event(client):
    # Setup mock SQS
    sqs = boto3.client('sqs', region_name='us-east-1')
    sqs.create_queue(QueueName='events-queue')
    
    event_data = {
        "user_id": "abc123",
        "event_type": "page_view",
        "metadata": {"page": "home"},
        "timestamp": "2025-05-28T10:00:00Z"
    }
    
    response = client.post("/events", json=event_data)
    logger.info("Response JSON:", response.json())
    assert response.status_code == 200

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "total_events" in response.json()
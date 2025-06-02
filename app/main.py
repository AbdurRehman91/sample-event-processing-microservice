import sys
import uvicorn
import logging
import structlog
import asyncio
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from contextlib import asynccontextmanager
from app.database import get_db, Base, engine
from app.schemas import EventCreate, EventResponse
from app.queue_service import QueueService
from app.worker import EventWorker
from app.models import EventLog
from app.config import settings

logging.basicConfig(
    format="%(message)s",  # structlog formats the message, so we just want the message
    level=settings.log_level,    # Set the minimum level you want to see (e.g., INFO, DEBUG)
    stream=sys.stdout      # Send output to the console
)

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,     # Add the logger name (e.g., your module name)
        structlog.stdlib.add_log_level,       # Add the log level (INFO, DEBUG, etc.)
        structlog.processors.TimeStamper(fmt="iso"), # Add ISO-formatted timestamp
        structlog.dev.ConsoleRenderer()       # Renders output for console readability
        # For JSON output to console, use: structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global worker instance
worker = EventWorker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")
    Base.metadata.create_all(bind=engine)
    
    # Start worker in background
    asyncio.create_task(worker.start_worker())
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    worker.stop_worker()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

queue_service = QueueService()

@app.post("/events", response_model=EventResponse)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """
    Create and queue an application usage event
    """
    try:
        logger.info("Received event for processing")
        # Validate and enqueue event
        event_data = event.dict()
        message_id = await queue_service.send_event(event_data)
        # db_event = create_event_db(db=db, event=event)
        # logger.info("Event saved to database", db_id=db_event.id)
        logger.info("Event queued successfully", 
                   user_id=event.user_id, 
                   event_type=event.event_type,
                   message_id=message_id)
        
        return EventResponse(
            message="Event queued successfully",
            event_id=message_id
        )
        
    except Exception as e:
        logger.error("Failed to queue event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to queue event")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "event-processor"}

@app.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Get basic metrics about processed events"""
    try:
        total_events = db.query(func.count(EventLog.id)).scalar()
        event_types = db.query(EventLog.event_type, func.count(EventLog.id)).group_by(EventLog.event_type).all()
        return {
            "total_events": total_events,
            "event_types": {event_type: count for event_type, count in event_types}
        }
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
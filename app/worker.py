import asyncio
import json
import structlog
from datetime import datetime, timezone
from app.models import EventLog 
from app.database import SessionLocal
from app.queue_service import QueueService
from app.schemas import EventCreate 
from app.crud import create_db_event

logger = structlog.get_logger()

class EventWorker:
    def __init__(self):
        self.queue_service = QueueService()
        self.running = False
    
    async def process_event(self, event_data: dict) -> EventLog:
        """Process individual event and save to database"""
        try:
            # Enrich the event data
            enriched_data = {
                **event_data,
                "processed_at": datetime.now(timezone.utc),
                "enriched_metadata": {
                    **(event_data.get("metadata", {})),
                    "processing_version": "1.0",
                    "worker_id": "worker-001"
                }
            }
            
            # Save to database
            db = SessionLocal()
            try:
                logger.info(f"event data dict is : {event_data}")
                event_log = EventLog(
                    user_id=event_data["user_id"],
                    event_type=event_data["event_type"],
                    metadata=enriched_data["enriched_metadata"],
                    original_timestamp=datetime.fromisoformat(event_data["timestamp"].replace("Z", "+00:00")),
                    processed_at=enriched_data["processed_at"]
                )
                
                db.add(event_log)
                db.commit()
                db.refresh(event_log)
                
                logger.info("Event processed and saved", event_id=event_log.id, user_id=event_data["user_id"])
                return event_log
                
            finally:
                db.close()
        except Exception as e:
            logger.error("Failed to process event", error=str(e), event_data=event_data)
            raise
    
    async def start_worker(self):
        """Start the worker to process events from queue"""
        self.running = True
        logger.info("Worker started")
        
        while self.running:
            try:
                logger.info("Polling for messages from queue")
                messages = await self.queue_service.receive_events()
                
                for message in messages:
                    try:
                        logger.info(f"current message is:{message}")
                        await self.process_event(message)
                        
                        # Delete message after successful processing
                        await self.queue_service.delete_message(message['ReceiptHandle'])
                    except Exception as e:
                        logger.error("Failed to process message", error=str(e), message_id=message.get('MessageId'))
                        # In production, you might want to send to DLQ instead of just logging
                
                if not messages:
                    await asyncio.sleep(5)  # Wait before polling again
                    
            except Exception as e:
                logger.error("Worker error", error=str(e))
                await asyncio.sleep(5)  # Wait before retrying
    
    def stop_worker(self):
        """Stop the worker"""
        self.running = False
        logger.info("Worker stopping")
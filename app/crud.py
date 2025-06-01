from datetime import datetime
from sqlalchemy.orm import Session
from app.models import EventLog
from app.schemas import EventCreate

def create_db_event(db: Session, event_obj: EventCreate):
    # If timestamp is not provided in the input, use current time
    db_timestamp = event_obj.timestamp if event_obj.timestamp else datetime.now()

    # db_event = EventLog(user_id=event_obj["user_id"],
    #                 event_type=event_obj["event_type"],
    #                 metadata=enriched_data["enriched_metadata"],
    #                 original_timestamp=datetime.fromisoformat(event_obj["timestamp"].replace("Z", "+00:00")),
    #                 processed_at=event_obj["processed_at"]
    #             )
    db_event = EventLog(user_id=event_obj["user_id"],
                    event_type=event_obj["event_type"],
                    original_timestamp=datetime.fromisoformat(event_obj["timestamp"].replace("Z", "+00:00")),
                    processed_at=event_obj["processed_at"]
                )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

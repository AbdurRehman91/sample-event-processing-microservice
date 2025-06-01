from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from datetime import datetime
import os

class EventLog(Base):
    __tablename__ = "event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    original_timestamp = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=False)
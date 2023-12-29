from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = 'log_entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(120), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = Column(String(50), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    request = Column(Text, nullable=True)
    response = Column(Text, nullable=True)

    # Indexes
    Index('idx_timestamp', timestamp)
    Index('idx_user_id', user_id)
    Index('idx_status', status)
    Index('idx_timestamp_user_id', timestamp, user_id)  # Composite index

# If using Alembic, can generate a new migration script after defining this model.

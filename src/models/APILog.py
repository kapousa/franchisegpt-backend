from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Float, Text
from config import Base


class APILog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String)
    path = Column(String)
    query_params = Column(String, nullable=True)
    status_code = Column(Integer)
    status_description = Column(String)
    duration = Column(String)
    user_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    
    children = relationship("Child", back_populates="parent")

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    age = Column(Integer)
    habits = Column(String) # Stored as JSON string or comma-separated
    behavioral_patterns = Column(String)
    
    parent = relationship("User", back_populates="children")
    activity_logs = relationship("ActivityLog", back_populates="child")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())
    mood = Column(Integer) # Scale e.g., 1-10
    sleep_duration = Column(Float) # In hours
    screen_time = Column(Float) # In hours
    activity_level = Column(Integer) # Scale e.g., 1-10
    predicted_stress_level = Column(String) # "low", "medium", "high"
    stress_score = Column(Float) # Continuous value from ML model
    
    child = relationship("Child", back_populates="activity_logs")

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Activity Log ---
class ActivityLogBase(BaseModel):
    mood: int
    sleep_duration: float
    screen_time: float
    activity_level: int

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLog(ActivityLogBase):
    id: int
    child_id: int
    date: datetime
    predicted_stress_level: Optional[str] = None
    stress_score: Optional[float] = None

    class Config:
        from_attributes = True

# --- Child ---
class ChildBase(BaseModel):
    name: str
    age: int
    habits: Optional[str] = None
    behavioral_patterns: Optional[str] = None

class ChildCreate(ChildBase):
    pass

class Child(ChildBase):
    id: int
    parent_id: int
    activity_logs: List[ActivityLog] = []

    class Config:
        from_attributes = True

# --- User ---
class UserBase(BaseModel):
    email: str
    name: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    children: List[Child] = []

    class Config:
        from_attributes = True

# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

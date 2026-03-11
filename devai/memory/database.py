from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session, select
import os

# Database Configuration
DATABASE_PATH = os.path.expanduser("~/.devai/devai.db")
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
engine = create_engine(DATABASE_URL)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str # 'user' or 'ai'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ResourceState(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str
    properties_json: str # JSON string of properties
    status: str # 'deployed', 'deleted', 'failed'
    last_updated: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

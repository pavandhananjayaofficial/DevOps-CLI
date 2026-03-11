from typing import List
from sqlmodel import select, desc
from devai.memory.database import get_session, Message

class HistoryManager:
    """
    Tracks conversation history to provide context for Layer 3 (AI Planner).
    """

    @staticmethod
    def add_message(role: str, content: str):
        with get_session() as session:
            msg = Message(role=role, content=content)
            session.add(msg)
            session.commit()

    @staticmethod
    def get_recent_history(limit: int = 10) -> List[dict]:
        with get_session() as session:
            statement = select(Message).order_by(desc(Message.timestamp)).limit(limit)
            results = session.exec(statement).all()
            # Return in chronological order
            return [{"role": m.role, "content": m.content} for m in reversed(results)]

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlmodel import select
from sqlmodel import select, delete
from devai.memory.database import get_session, ResourceState, ServerState

class StateManager:
    """
    Manages the lifecycle and persistence of infrastructure resource states.
    Allows DevAI to know what is currently 'alive' in the cloud/local system.
    """
    
    @staticmethod
    def update_resource(name: str, resource_type: str, properties: Dict[str, Any], status: str = "deployed"):
        with get_session() as session:
            statement = select(ResourceState).where(ResourceState.name == name)
            existing = session.exec(statement).first()
            
            if existing:
                existing.properties_json = json.dumps(properties)
                existing.status = status
                existing.last_updated = datetime.utcnow()
                session.add(existing)
            else:
                new_state = ResourceState(
                    name=name,
                    type=resource_type,
                    properties_json=json.dumps(properties),
                    status=status
                )
                session.add(new_state)
            
            session.commit()

    @staticmethod
    def delete_resource(name: str):
        with get_session() as session:
            statement = select(ResourceState).where(ResourceState.name == name)
            existing = session.exec(statement).first()
            if existing:
                existing.status = "deleted"
                existing.last_updated = datetime.utcnow()
                session.add(existing)
                session.commit()

    @staticmethod
    def get_all_resources() -> List[Dict[str, Any]]:
        with get_session() as session:
            statement = select(ResourceState).where(ResourceState.status != "deleted")
            results = session.exec(statement).all()
            return [
                {
                    "name": r.name,
                    "type": r.type,
                    "properties": json.loads(r.properties_json),
                    "status": r.status
                } for r in results
            ]

    @staticmethod
    def add_server(name: str, ip: str, username: str, status: str = "pending"):
        with get_session() as session:
            new_server = ServerState(name=name, ip=ip, username=username, status=status)
            session.add(new_server)
            session.commit()

    @staticmethod
    def get_servers() -> List[Dict[str, Any]]:
        with get_session() as session:
            statement = select(ServerState)
            results = session.exec(statement).all()
            return [
                {
                    "name": s.name,
                    "ip": s.ip,
                    "username": s.username,
                    "status": s.status
                } for s in results
            ]

    @staticmethod
    def remove_server(name: str):
        with get_session() as session:
            statement = delete(ServerState).where(ServerState.name == name)
            session.exec(statement)
            session.commit()

    @staticmethod
    def update_server_status(name: str, status: str):
        with get_session() as session:
            statement = select(ServerState).where(ServerState.name == name)
            server = session.exec(statement).first()
            if server:
                server.status = status
                server.last_seen = datetime.utcnow()
                session.add(server)
                session.commit()

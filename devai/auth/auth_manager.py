from typing import Dict, List, Optional
from enum import Enum
import hashlib

class Role(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class AuthManager:
    """
    Manages user authentication and Role-Based Access Control (RBAC).
    """

    def __init__(self):
        # In a real app, this would be backed by a DB table 'users'
        self.mock_users = {
            "admin": {"role": Role.ADMIN, "password_hash": self._hash("admin123")},
            "dev": {"role": Role.DEVELOPER, "password_hash": self._hash("dev123")},
            "guest": {"role": Role.VIEWER, "password_hash": self._hash("guest123")}
        }
        self.current_user: Optional[str] = None
        self.current_role: Optional[Role] = None

    def _hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, username: str, password: str) -> bool:
        user = self.mock_users.get(username)
        if user and user["password_hash"] == self._hash(password):
            self.current_user = username
            self.current_role = user["role"]
            print(f"[Auth] 🔓 Logged in as {username} ({self.current_role.value})")
            return True
        return False

    def has_permission(self, action: str) -> bool:
        """Simple RBAC logic."""
        if not self.current_role:
            return False
        
        if self.current_role == Role.ADMIN:
            return True
        
        if self.current_role == Role.DEVELOPER:
            return action not in ["destroy_cluster", "delete_project"]
        
        if self.current_role == Role.VIEWER:
            return action in ["list", "status", "logs", "monitor"]
        
        return False

    def logout(self):
        self.current_user = None
        self.current_role = None

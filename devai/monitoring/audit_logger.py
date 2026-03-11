import datetime
from typing import Any, Dict, List, Optional

class AuditLogger:
    """
    Logs critical infrastructure changes and AI decisions for auditing.
    """
    def __init__(self, log_path: str = "devai_audit.log"):
        self.log_path = log_path

    def record(self, event_type: str, **kwargs):
        timestamp = datetime.datetime.now().isoformat()
        entry = f"[{timestamp}] EVENT: {event_type} | DATA: {kwargs}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"📝 Audit Record: {event_type}")

    def get_logs(self, limit: int = 50) -> List[str]:
        import os
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return f.readlines()[-limit:]

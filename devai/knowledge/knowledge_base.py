from typing import Dict, Any, List
import json
import os

class KnowledgeBase:
    """
    Stores failure patterns, remediation steps, and successful deployment data.
    Allows DevAI to learn from previous incidents.
    """

    def __init__(self, storage_path: str = "~/.devai/knowledge_base.json"):
        self.storage_path = os.path.expanduser(storage_path)
        self.records = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return []

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.records, f, indent=4)

    def record_incident(self, project: str, failure: str, remediation: str, success: bool):
        record = {
            "project": project,
            "failure": failure,
            "remediation": remediation,
            "success": success,
            "timestamp": "ISO-TIMESTAMP"
        }
        self.records.append(record)
        self._save()
        print(f"[KnowledgeBase] 🧠 Learned new pattern for {project}")

    def query_patterns(self, failure_type: str) -> List[Dict[str, Any]]:
        return [r for r in self.records if failure_type.lower() in r['failure'].lower()]

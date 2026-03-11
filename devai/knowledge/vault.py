import os
import json
from typing import Dict, Optional
from cryptography.fernet import Fernet
from devai.core.exceptions import DevAIException

class VaultManager:
    """
    Manages encrypted storage for sensitive data like API keys and .env variables.
    Uses Fernet symmetric encryption.
    """
    
    VAULT_DIR = os.path.expanduser("~/.devai/vault")
    KEY_FILE = os.path.join(VAULT_DIR, ".key")
    STORAGE_FILE = os.path.join(VAULT_DIR, "secure_data.bin")

    def __init__(self):
        if not os.path.exists(self.VAULT_DIR):
            os.makedirs(self.VAULT_DIR, exist_ok=True)
        
        self.key = self._get_or_create_key()
        self.fernet = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        if os.path.exists(self.KEY_FILE):
            with open(self.KEY_FILE, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.KEY_FILE, "wb") as f:
                f.write(key)
            return key

    def store_secret(self, key: str, value: str):
        data = self._load_vault()
        data[key] = value
        self._save_vault(data)

    def get_secret(self, key: str) -> Optional[str]:
        data = self._load_vault()
        return data.get(key)

    def _load_vault(self) -> Dict[str, str]:
        if not os.path.exists(self.STORAGE_FILE):
            return {}
        
        try:
            with open(self.STORAGE_FILE, "rb") as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    return {}
                decrypted_data = self.fernet.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
        except Exception:
            return {}

    def _save_vault(self, data: Dict[str, str]):
        json_data = json.dumps(data).encode()
        encrypted_data = self.fernet.encrypt(json_data)
        with open(self.STORAGE_FILE, "wb") as f:
            f.write(encrypted_data)

    def list_secrets(self) -> list[str]:
        return list(self._load_vault().keys())
